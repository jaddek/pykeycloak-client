# SPDX-License-Identifier: MIT
from unittest.mock import AsyncMock, MagicMock

from pykeycloak_client.core.realm import RealmClient
from pykeycloak_client.providers.providers import KeycloakProviderAsync


class TestKeycloakProviderAsync:
    def test_properties_are_initialized(self):
        provider = KeycloakProviderAsync(
            realm_client=RealmClient(
                realm_name="r",
                client_uuid="7f6ea8bf-10e4-4caf-b4dd-551a7fb56853",
                client_id="cid",
                client_secret="sec",
            ),
            headers=MagicMock(),
            wrapper=MagicMock(),
        )

        assert provider.auth is not None
        assert provider.users is not None
        assert provider.sessions is not None
        assert provider.roles is not None
        assert provider.clients is not None
        assert provider.authz is not None
        assert provider.authz_scope is not None
        assert provider.authz_resource is not None
        assert provider.authz_policy is not None
        assert provider.authz_permission is not None

    async def test_close_connection_delegates_to_base(self):
        provider = KeycloakProviderAsync(
            realm_client=RealmClient(
                realm_name="r",
                client_uuid="7f6ea8bf-10e4-4caf-b4dd-551a7fb56853",
                client_id="cid",
                client_secret="sec",
            ),
            headers=MagicMock(),
            wrapper=MagicMock(),
        )
        provider._base.close_connection = AsyncMock(return_value=None)

        await provider.close_connection()

        provider._base.close_connection.assert_awaited_once()
