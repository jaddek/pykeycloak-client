# SPDX-License-Identifier: MIT
from unittest.mock import MagicMock, patch

from pykeycloak.core.realm import RealmClient
from pykeycloak.pykeycloak import PyKeycloak


class TestPyKeycloak:
    def test_get_delegates_to_registry(self):
        registry = MagicMock()
        registry.get.return_value = "factory"
        pkc = PyKeycloak(registry=registry)

        assert pkc.get("k1") == "factory"
        registry.get.assert_called_once_with("k1")

    def test_register_uses_defaults_when_dependencies_not_passed(self):
        registry = MagicMock()
        pkc = PyKeycloak(registry=registry)
        realm = RealmClient(
            realm_name="r",
            client_uuid="7f6ea8bf-10e4-4caf-b4dd-551a7fb56853",
            client_id="cid",
            client_secret="sec",
        )

        with (
            patch("pykeycloak.pykeycloak.get_headers_factory", return_value="headers"),
            patch(
                "pykeycloak.pykeycloak.get_keycloak_http_client_from_env",
                return_value="client",
            ),
            patch("pykeycloak.pykeycloak.get_response_validator", return_value="validator"),
            patch("pykeycloak.pykeycloak.KeycloakInMemoryProviderAsync") as provider_cls,
            patch("pykeycloak.pykeycloak.KeycloakServiceFactory") as factory_cls,
        ):
            provider_instance = MagicMock()
            provider_cls.return_value = provider_instance
            factory_instance = MagicMock()
            factory_cls.return_value = factory_instance

            pkc.register("k1", realm_client=realm)

            provider_cls.assert_called_once()
            factory_cls.assert_called_once_with(
                provider=provider_instance, validator="validator"
            )
            registry.register.assert_called_once_with("k1", factory_instance)
