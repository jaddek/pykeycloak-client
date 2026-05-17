"""
Dynamic MCP server for pykeycloak-client.

Run:
    uv run python mcp_server.py

Notes:
- Exposes registration + method discovery + dynamic invocation for all services.
- Requires normal library env vars (for example `KEYCLOAK_BASE_URL`) to be set.
"""

from __future__ import annotations

import dataclasses
import inspect
import os
from collections.abc import Mapping
from enum import Enum
from types import UnionType
from typing import Any, get_args, get_origin
from uuid import UUID

from mcp.server.fastmcp import FastMCP

from pykeycloak_client.core.realm import RealmClient
from pykeycloak_client.providers import payloads, queries
from pykeycloak_client.pykeycloak import PyKeycloak

MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("MCP_PORT", "8000"))
MCP_TRANSPORT = os.getenv("MCP_TRANSPORT", "stdio")

mcp = FastMCP("pykeycloak-mcp", host=MCP_HOST, port=MCP_PORT)
pkc = PyKeycloak()

SERVICE_NAMES = (
    "auth",
    "users",
    "sessions",
    "roles",
    "clients",
    "authz",
    "authz_scope",
    "authz_resource",
    "authz_policy",
    "authz_permission",
    "uma",
    "well_known",
)


def _build_type_registry() -> dict[str, type[Any]]:
    registry: dict[str, type[Any]] = {}

    for module in (payloads, queries):
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ != module.__name__:
                continue
            registry[obj.__name__] = obj
    return registry


TYPE_REGISTRY = _build_type_registry()


def _serialize(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if dataclasses.is_dataclass(value):
        result: dict[str, Any] = {}
        for field in dataclasses.fields(value):
            result[field.name] = _serialize(getattr(value, field.name))
        return result
    if isinstance(value, Mapping):
        return {str(k): _serialize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_serialize(v) for v in value]
    return str(value)


def _coerce_dataclass(cls: type[Any], raw: Mapping[str, Any]) -> Any:
    kwargs: dict[str, Any] = {}
    for field in dataclasses.fields(cls):
        if field.name not in raw:
            continue
        kwargs[field.name] = _coerce_value(field.type, raw[field.name])
    return cls(**kwargs)


def _coerce_value(annotation: Any, value: Any) -> Any:
    if value is None:
        return None

    if isinstance(annotation, str):
        resolved = TYPE_REGISTRY.get(annotation)
        if resolved is not None:
            annotation = resolved

    if annotation is Any or annotation is inspect._empty:
        return value

    def _try_union_candidates(candidates: tuple[Any, ...]) -> Any:
        for candidate in candidates:
            try:
                return _coerce_value(candidate, value)
            except (TypeError, ValueError):
                continue
        return value

    origin = get_origin(annotation)
    if origin in (UnionType,):
        return _try_union_candidates(get_args(annotation))

    if origin is not None:
        if origin is list:
            item_type = get_args(annotation)[0] if get_args(annotation) else Any
            if isinstance(value, list):
                return [_coerce_value(item_type, item) for item in value]
            return value
        if origin is dict:
            args = get_args(annotation)
            key_type = args[0] if len(args) > 0 else Any
            val_type = args[1] if len(args) > 1 else Any
            if isinstance(value, Mapping):
                return {
                    _coerce_value(key_type, k): _coerce_value(val_type, v)
                    for k, v in value.items()
                }
            return value
        if origin is tuple:
            return value
        # typing.Union on some interpreters
        if str(origin).endswith("Union"):
            return _try_union_candidates(get_args(annotation))

    if inspect.isclass(annotation):
        if issubclass(annotation, UUID) and isinstance(value, str):
            return UUID(value)
        if issubclass(annotation, Enum):
            return annotation(value)
        if dataclasses.is_dataclass(annotation) and isinstance(value, Mapping):
            return _coerce_dataclass(annotation, value)
        if annotation in (str, int, float, bool):
            return annotation(value)

    return value


def _get_factory(key: str) -> Any:
    return pkc.get(key)


def _get_registered_keys() -> list[str]:
    return sorted(pkc._registry._map.keys())


def _resolve_callable(key: str, method_path: str) -> tuple[Any, inspect.Signature]:
    if "." not in method_path:
        raise ValueError("method_path must be '<service>.<method>'")

    service_name, method_name = method_path.split(".", 1)
    if service_name not in SERVICE_NAMES:
        raise ValueError(
            f"Unknown service '{service_name}'. Expected one of {SERVICE_NAMES}"
        )

    service = getattr(_get_factory(key), service_name)
    method = getattr(service, method_name, None)
    if method is None or method_name.startswith("_") or not callable(method):
        raise ValueError(f"Method not found: {method_path}")

    return method, inspect.signature(method)


def _stringify_type(annotation: Any) -> str:
    if annotation is inspect._empty:
        return "Any"
    return str(annotation).replace("typing.", "")


def _resolve_annotation(annotation: Any) -> Any:
    if isinstance(annotation, str):
        return TYPE_REGISTRY.get(annotation, annotation)
    return annotation


def _param_location(annotation: Any, param_name: str) -> str:
    resolved = _resolve_annotation(annotation)
    if inspect.isclass(resolved) and dataclasses.is_dataclass(resolved):
        module_name = getattr(resolved, "__module__", "")
        if module_name == payloads.__name__:
            return "body"
        if module_name == queries.__name__:
            return "query"
    if param_name.endswith("_id") or param_name in {"access_token", "refresh_token"}:
        return "path"
    return "other"


def _dataclass_fields_schema(cls: type[Any]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for field in dataclasses.fields(cls):
        default = "required"
        if field.default is not dataclasses.MISSING:
            default = repr(field.default)
        elif field.default_factory is not dataclasses.MISSING:  # type: ignore[attr-defined]
            default = "factory()"
        result.append(
            {
                "name": field.name,
                "type": _stringify_type(field.type),
                "default": default,
            }
        )
    return result


def _method_schema(signature: inspect.Signature) -> dict[str, Any]:
    params: list[dict[str, Any]] = []
    for param_name, param in signature.parameters.items():
        if param_name == "self":
            continue
        resolved = _resolve_annotation(param.annotation)
        entry: dict[str, Any] = {
            "name": param_name,
            "type": _stringify_type(param.annotation),
            "location": _param_location(param.annotation, param_name),
            "required": param.default is inspect._empty,
        }
        if param.default is not inspect._empty:
            entry["default"] = repr(param.default)
        if inspect.isclass(resolved) and dataclasses.is_dataclass(resolved):
            entry["fields"] = _dataclass_fields_schema(resolved)
        params.append(entry)
    return {"params": params}


@mcp.tool()
def health() -> dict[str, Any]:
    """Basic health check tool."""
    return {"status": "ok", "server": "pykeycloak-mcp"}


@mcp.tool()
def keycloak_register(
    key: str,
    realm_name: str,
    client_uuid: str,
    client_id: str,
    client_secret: str | None = None,
) -> dict[str, Any]:
    """Register a Keycloak realm client under a key."""
    pkc.register(
        key=key,
        realm_client=RealmClient(
            realm_name=realm_name,
            client_uuid=client_uuid,
            client_id=client_id,
            client_secret=client_secret,
        ),
    )
    return {"registered": key, "keys": _get_registered_keys()}


@mcp.tool()
def keycloak_register_from_env(key: str, client_name: str) -> dict[str, Any]:
    """Register realm client from env using RealmClient.from_env(client_name)."""
    pkc.register(
        key=key,
        realm_client=RealmClient.from_env(client_name=client_name),
    )
    return {"registered": key, "keys": _get_registered_keys()}


@mcp.tool()
def keycloak_unregister(key: str) -> dict[str, Any]:
    """Unregister a previously registered key."""
    pkc._registry.unregister(key)
    return {"unregistered": key, "keys": _get_registered_keys()}


@mcp.tool()
def keycloak_list_keys() -> dict[str, Any]:
    """List currently registered client keys."""
    return {"keys": _get_registered_keys()}


@mcp.tool()
def keycloak_list_methods(key: str) -> dict[str, Any]:
    """List available public methods across all services for a registered key."""
    factory = _get_factory(key)
    methods: dict[str, list[dict[str, Any]]] = {}

    for service_name in SERVICE_NAMES:
        service = getattr(factory, service_name)
        entries: list[dict[str, str]] = []
        for name, member in inspect.getmembers(service, callable):
            if name.startswith("_"):
                continue
            signature = inspect.signature(member)
            schema = _method_schema(signature)
            entries.append(
                {
                    "name": name,
                    "signature": str(signature),
                    "query": [
                        p for p in schema["params"] if p.get("location") == "query"
                    ],
                    "body": [
                        p for p in schema["params"] if p.get("location") == "body"
                    ],
                }
            )
        methods[service_name] = sorted(entries, key=lambda x: x["name"])

    return {"key": key, "methods": methods}


@mcp.tool()
def keycloak_describe_method(key: str, method_path: str) -> dict[str, Any]:
    """Describe method params including query/body schema for one service method."""
    _, signature = _resolve_callable(key, method_path)
    schema = _method_schema(signature)
    return {
        "key": key,
        "method": method_path,
        "query": [p for p in schema["params"] if p.get("location") == "query"],
        "body": [p for p in schema["params"] if p.get("location") == "body"],
        "other": [p for p in schema["params"] if p.get("location") == "other"],
        "path": [p for p in schema["params"] if p.get("location") == "path"],
        "params": schema["params"],
    }


@mcp.tool()
async def keycloak_call(
    key: str,
    method_path: str,
    kwargs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Call any pykeycloak service method dynamically.

    Example:
    - method_path: "users.get_user_async"
    - kwargs: {"user_id": "..."}
    """
    call_kwargs = kwargs or {}
    method, signature = _resolve_callable(key, method_path)

    typed_kwargs: dict[str, Any] = {}
    for param_name, param in signature.parameters.items():
        if param_name not in call_kwargs:
            continue
        typed_kwargs[param_name] = _coerce_value(
            param.annotation, call_kwargs[param_name]
        )

    result = method(**typed_kwargs)
    if inspect.isawaitable(result):
        result = await result

    return {
        "key": key,
        "method": method_path,
        "kwargs": _serialize(typed_kwargs),
        "result": _serialize(result),
    }


@mcp.tool()
async def keycloak_close_all() -> dict[str, Any]:
    """Close underlying HTTP connections for all registered clients."""
    await pkc._registry.close_all()
    return {"closed": True}


def main() -> None:
    mcp.run(transport=MCP_TRANSPORT)


if __name__ == "__main__":
    main()
