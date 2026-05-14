# SPDX-License-Identifier: MIT
from importlib.metadata import PackageNotFoundError
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import Headers

from pykeycloak_client.core.realm import RealmClient
from pykeycloak_client.core.settings import ClientSettings
from pykeycloak_client.dependencies import (
    FactoryRegistry,
    KeycloakServiceFactory,
    get_async_client,
    get_default_user_agent,
    get_headers_factory,
    get_keycloak_http_client,
    get_keycloak_http_client_from_env,
    get_package_name,
    get_response_validator,
    get_sanitizer,
    get_service_factory,
)


class TestFactoryRegistry:
    def test_register_and_get(self):
        registry = FactoryRegistry()
        factory = MagicMock()

        registry.register("k1", factory)

        assert registry.get("k1") is factory

    def test_unregister_missing_key_raises(self):
        registry = FactoryRegistry()
        with pytest.raises(KeyError):
            registry.unregister("missing")

    async def test_close_all_aggregates_errors(self):
        registry = FactoryRegistry()

        ok_factory = MagicMock()
        ok_factory.provider.close_connection = AsyncMock(return_value=None)

        bad_factory = MagicMock()
        bad_factory.provider.close_connection = AsyncMock(
            side_effect=RuntimeError("boom")
        )

        registry.register("ok", ok_factory)
        registry.register("bad", bad_factory)

        with pytest.raises(RuntimeError, match="Errors during close_all"):
            await registry.close_all()

        ok_factory.provider.close_connection.assert_awaited_once()
        bad_factory.provider.close_connection.assert_awaited_once()


class TestGetAsyncClient:
    def test_sets_default_user_agent_when_missing(self):
        client = get_async_client(client_settings=ClientSettings())
        try:
            assert client.headers.get("User-Agent")
        finally:
            import asyncio

            asyncio.run(client.aclose())


class TestDependencyHelpers:
    def test_simple_helpers_return_expected_types(self):
        assert get_package_name() == "pykeycloak_client"
        assert "User-Agent" in get_default_user_agent()
        assert get_headers_factory() is not None
        assert get_response_validator() is not None
        assert get_sanitizer() is not None

    def test_get_default_user_agent_fallback_version(self):
        with patch(
            "pykeycloak_client.dependencies.version",
            side_effect=PackageNotFoundError("not found"),
        ):
            ua = get_default_user_agent()
            assert ua["User-Agent"].startswith("pykeycloak_client/")

    def test_get_service_factory_constructs_provider(self):
        provider_instance = MagicMock()
        provider_cls = MagicMock(return_value=provider_instance)
        realm = RealmClient(
            realm_name="r",
            client_uuid="7f6ea8bf-10e4-4caf-b4dd-551a7fb56853",
            client_id="cid",
            client_secret="sec",
        )
        http_client = MagicMock()
        headers = MagicMock()

        factory = get_service_factory(
            kc_realm_client=realm,
            kc_http_client=http_client,
            headers=headers,
            provider_cls=provider_cls,
        )

        assert isinstance(factory, KeycloakServiceFactory)
        provider_cls.assert_called_once()

    def test_keycloak_service_factory_cached_properties(self):
        provider = MagicMock()
        validator = MagicMock()
        factory = KeycloakServiceFactory(provider=provider, validator=validator)

        assert factory.users is factory.users
        assert factory.auth is factory.auth
        assert factory.authz is factory.authz
        assert factory.roles is factory.roles
        assert factory.sessions is factory.sessions
        assert factory.uma is factory.uma
        assert factory.clients is factory.clients
        assert factory.authz_resource is factory.authz_resource
        assert factory.authz_permission is factory.authz_permission
        assert factory.authz_scope is factory.authz_scope
        assert factory.authz_policy is factory.authz_policy
        assert factory.well_known is factory.well_known

    def test_get_keycloak_http_client_helpers(self):
        client = MagicMock()
        wrapped = get_keycloak_http_client(client=client)
        assert wrapped.client is client

        with patch(
            "pykeycloak_client.dependencies.get_async_client_with_env", return_value=client
        ):
            wrapped_env = get_keycloak_http_client_from_env()
            assert wrapped_env.client is client

    def test_preserves_existing_user_agent(self):
        client = get_async_client(
            client_settings=ClientSettings(headers={"User-Agent": "custom/1.0"})
        )
        try:
            assert client.headers.get("User-Agent") == "custom/1.0"
        finally:
            import asyncio

            asyncio.run(client.aclose())

    def test_accepts_bytes_headers(self):
        client = get_async_client(
            client_settings=ClientSettings(headers=Headers({b"X-Test": b"1"}))
        )
        try:
            assert client.headers.get("X-Test") == "1"
            assert client.headers.get("User-Agent")
        finally:
            import asyncio

            asyncio.run(client.aclose())
