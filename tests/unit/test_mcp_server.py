# SPDX-License-Identifier: MIT
import dataclasses
import inspect
import os
from enum import Enum
from typing import Any
from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest

os.environ.setdefault("KEYCLOAK_BASE_URL", "http://localhost")

from pykeycloak_client import mcp_server  # noqa: E402

EXPECTED_TOOLS = {
    "health",
    "keycloak_register",
    "keycloak_register_from_env",
    "keycloak_unregister",
    "keycloak_list_keys",
    "keycloak_list_methods",
    "keycloak_describe_method",
    "keycloak_call",
    "keycloak_close_all",
}


class SampleEnum(Enum):
    ACTIVE = "active"


@dataclasses.dataclass
class SampleData:
    name: str
    count: int = 1


@dataclasses.dataclass
class FactoryData:
    required: str
    optional: int = 2
    generated: list[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class PayloadData:
    value: str = ""

    __module__ = mcp_server.payloads.__name__


@dataclasses.dataclass
class QueryData:
    value: str = ""

    __module__ = mcp_server.queries.__name__


def test_mcp_server_registers_expected_tools():
    assert mcp_server.mcp.name == "pykeycloak-mcp"
    assert set(mcp_server.mcp._tool_manager._tools) == EXPECTED_TOOLS


def test_health_tool():
    assert mcp_server.health() == {"status": "ok", "server": "pykeycloak-mcp"}


def test_register_list_and_unregister_key(monkeypatch):
    key = "mcp-unit-test"
    monkeypatch.setattr(
        "pykeycloak_client.pykeycloak.get_keycloak_http_client_from_env",
        lambda: Mock(),
    )
    registered = mcp_server.keycloak_register(
        key=key,
        realm_name="unit-test",
        client_uuid="00000000-0000-0000-0000-000000000000",
        client_id="unit-test-client",
        client_secret="unit-test-secret",
    )
    try:
        assert registered["registered"] == key
        assert key in mcp_server.keycloak_list_keys()["keys"]
    finally:
        mcp_server.keycloak_unregister(key)

    assert key not in mcp_server.keycloak_list_keys()["keys"]


def test_serialization_handles_nested_values():
    value = {
        "uuid": UUID("00000000-0000-0000-0000-000000000001"),
        "enum": SampleEnum.ACTIVE,
        "bytes": b"hello",
        "data": SampleData("item", 3),
        "sequence": (1, {2, 3}),
    }
    assert mcp_server._serialize(value) == {
        "uuid": "00000000-0000-0000-0000-000000000001",
        "enum": "active",
        "bytes": "hello",
        "data": {"name": "item", "count": 3},
        "sequence": [1, [2, 3]],
    }
    assert mcp_server._serialize(None) is None
    assert mcp_server._serialize("text") == "text"
    assert mcp_server._serialize(b"\xff") == "�"
    assert mcp_server._serialize(object())


def test_coerce_value_supports_common_annotations(monkeypatch):
    monkeypatch.setitem(mcp_server.TYPE_REGISTRY, "SampleData", SampleData)
    uid = "00000000-0000-0000-0000-000000000002"
    assert mcp_server._coerce_value("SampleData", {"name": "x", "count": "4"}) == SampleData(
        "x", 4
    )
    assert mcp_server._coerce_value(Any, "value") == "value"
    assert mcp_server._coerce_value(inspect._empty, "value") == "value"
    assert mcp_server._coerce_value(UUID, uid) == UUID(uid)
    assert mcp_server._coerce_value(SampleEnum, "active") is SampleEnum.ACTIVE
    assert mcp_server._coerce_value(int, "4") == 4
    assert mcp_server._coerce_value(str, 4) == "4"
    assert mcp_server._coerce_value(list[int], ["1", "2"]) == [1, 2]
    assert mcp_server._coerce_value(list[int], "not-a-list") == "not-a-list"
    assert mcp_server._coerce_value(dict[str, int], {1: "2"}) == {"1": 2}
    assert mcp_server._coerce_value(dict[str, int], []) == []
    assert mcp_server._coerce_value(tuple[int, ...], [1]) == [1]
    assert mcp_server._coerce_value(int | str, "4") == 4
    assert mcp_server._coerce_value(int | UUID, "not-convertible") == "not-convertible"
    assert mcp_server._coerce_value(None, None) is None


def test_resolve_callable_validates_paths(monkeypatch):
    service = Mock()
    service.public = lambda value=1: value
    factory = Mock(auth=service)
    monkeypatch.setattr(mcp_server, "_get_factory", lambda key: factory)

    method, signature = mcp_server._resolve_callable("key", "auth.public")
    assert callable(method)
    assert isinstance(signature, inspect.Signature)

    with pytest.raises(ValueError, match="<service>\\.<method>"):
        mcp_server._resolve_callable("key", "invalid")
    with pytest.raises(ValueError, match="Unknown service"):
        mcp_server._resolve_callable("key", "unknown.public")
    service.missing = None
    with pytest.raises(ValueError, match="Method not found"):
        mcp_server._resolve_callable("key", "auth.missing")
    with pytest.raises(ValueError, match="Method not found"):
        mcp_server._resolve_callable("key", "auth._private")


def test_schema_helpers_classify_parameters():
    assert mcp_server._param_location(PayloadData, "payload") == "body"
    assert mcp_server._param_location(QueryData, "query") == "query"
    assert mcp_server._param_location(str, "user_id") == "path"
    assert mcp_server._param_location(str, "access_token") == "path"
    assert mcp_server._param_location(str, "other") == "other"

    schema = mcp_server._dataclass_fields_schema(FactoryData)
    assert [field["default"] for field in schema] == ["required", "2", "factory()"]

    def method(self, payload: PayloadData, query: QueryData, user_id: str, limit: int = 5):
        return None

    result = mcp_server._method_schema(inspect.signature(method))
    assert [param["name"] for param in result["params"]] == [
        "payload",
        "query",
        "user_id",
        "limit",
    ]
    assert result["params"][-1]["required"] is False


def test_register_from_env(monkeypatch):
    realm = Mock()
    from_env = Mock(return_value=realm)
    register = Mock()
    monkeypatch.setattr(mcp_server.RealmClient, "from_env", from_env)
    monkeypatch.setattr(mcp_server.pkc, "register", register)
    monkeypatch.setattr(mcp_server, "_get_registered_keys", lambda: ["env-key"])

    result = mcp_server.keycloak_register_from_env("env-key", "client")
    assert result == {"registered": "env-key", "keys": ["env-key"]}
    from_env.assert_called_once_with(client_name="client")
    register.assert_called_once_with(key="env-key", realm_client=realm)


def test_list_and_describe_methods(monkeypatch):
    class Service:
        def public(self, payload: PayloadData, user_id: str, limit: int = 1):
            return None

        def _private(self):
            return None

    monkeypatch.setattr(mcp_server, "SERVICE_NAMES", ("auth",))
    monkeypatch.setattr(mcp_server, "_get_factory", lambda key: Mock(auth=Service()))

    result = mcp_server.keycloak_list_methods("key")
    assert result["key"] == "key"
    assert [entry["name"] for entry in result["methods"]["auth"]] == ["public"]
    assert result["methods"]["auth"][0]["body"][0]["name"] == "payload"

    described = mcp_server.keycloak_describe_method("key", "auth.public")
    assert described["method"] == "auth.public"
    assert described["body"][0]["name"] == "payload"
    assert described["path"][0]["name"] == "user_id"


@pytest.mark.asyncio
async def test_keycloak_call_handles_sync_and_async(monkeypatch):
    def sync_method(user_id: UUID, count: int = 0):
        return {"id": user_id, "count": count}

    monkeypatch.setattr(
        mcp_server,
        "_resolve_callable",
        lambda key, path: (sync_method, inspect.signature(sync_method)),
    )
    result = await mcp_server.keycloak_call(
        "key",
        "auth.sync_method",
        {"user_id": "00000000-0000-0000-0000-000000000003", "count": "2", "ignored": 1},
    )
    assert result["kwargs"] == {
        "user_id": "00000000-0000-0000-0000-000000000003",
        "count": 2,
    }
    assert result["result"]["count"] == 2

    async_method = AsyncMock(return_value=SampleData("async", 5))
    monkeypatch.setattr(
        mcp_server,
        "_resolve_callable",
        lambda key, path: (async_method, inspect.signature(async_method)),
    )
    async_result = await mcp_server.keycloak_call("key", "auth.async_method")
    assert async_result["result"] == {"name": "async", "count": 5}
    async_method.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_close_all(monkeypatch):
    close_all = AsyncMock()
    monkeypatch.setattr(mcp_server.pkc._registry, "close_all", close_all)
    assert await mcp_server.keycloak_close_all() == {"closed": True}
    close_all.assert_awaited_once_with()


@pytest.mark.parametrize("transport", ["stdio", "sse", "streamable-http"])
def test_main_dispatches_supported_transports(monkeypatch, transport):
    run = Mock()
    monkeypatch.setattr(mcp_server.mcp, "run", run)
    monkeypatch.setattr(mcp_server, "MCP_TRANSPORT", transport)
    monkeypatch.setattr(mcp_server, "MCP_HOST", "127.0.0.2")
    monkeypatch.setattr(mcp_server, "MCP_PORT", 8100)

    mcp_server.main()

    if transport == "stdio":
        run.assert_called_once_with(transport="stdio")
    else:
        run.assert_called_once_with(
            transport=transport,
            host="127.0.0.2",
            port=8100,
        )


def test_main_rejects_unknown_transport(monkeypatch):
    monkeypatch.setattr(mcp_server, "MCP_TRANSPORT", "invalid")

    with pytest.raises(ValueError, match="MCP_TRANSPORT"):
        mcp_server.main()
