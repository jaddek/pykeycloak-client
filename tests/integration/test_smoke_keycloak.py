# SPDX-License-Identifier: MIT
import os

import pytest

from pykeycloak_client.core.enums import UrnIetfOauthUmaTicketResponseModeEnum
from pykeycloak_client.providers.payloads import (
    CreateUserPayload,
    RefreshTokenPayload,
    UMAAuthorizationPayload,
)

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_client_login_smoke(keycloak) -> None:
    token = await keycloak.auth.client_login_async()

    assert token.access_token
    assert token.refresh_token
    assert token.expires_in and token.expires_in > 0


@pytest.mark.asyncio
async def test_refresh_token_smoke(keycloak) -> None:
    token = await keycloak.auth.client_login_async()
    assert token.refresh_token

    refreshed = await keycloak.auth.refresh_token_async(
        payload=RefreshTokenPayload(refresh_token=token.refresh_token)
    )

    assert refreshed.access_token
    assert refreshed.expires_in and refreshed.expires_in > 0


@pytest.mark.asyncio
async def test_create_and_delete_user_smoke(keycloak, unique_username: str) -> None:
    user_id = await keycloak.users.create_user_async(
        payload=CreateUserPayload(
            username=unique_username,
            email=f"{unique_username}@example.com",
            first_name="Integration",
            last_name="Smoke",
            enabled=True,
        )
    )
    assert user_id

    fetched = await keycloak.users.get_user_async(user_id=user_id)
    assert fetched.username == unique_username

    await keycloak.users.delete_user_async(user_id=user_id)


@pytest.mark.asyncio
async def test_uma_permissions_smoke_if_user_configured(
    keycloak,
    integration_user_credentials,
) -> None:
    if integration_user_credentials is None:
        pytest.skip("KEYCLOAK_IT_USERNAME/KEYCLOAK_IT_PASSWORD are not configured")

    permissions_csv = os.getenv("KEYCLOAK_IT_UMA_PERMISSIONS", "").strip()
    if not permissions_csv:
        pytest.skip("KEYCLOAK_IT_UMA_PERMISSIONS is not configured")

    user_token = await keycloak.auth.user_login_async(payload=integration_user_credentials)
    assert user_token.access_token

    permissions = [value.strip() for value in permissions_csv.split(",") if value.strip()]
    assert permissions

    result = await keycloak.uma.get_uma_permissions_async(
        payload=UMAAuthorizationPayload(
            audience=None,
            permissions=permissions,
            subject_token=user_token.access_token,
            response_mode=UrnIetfOauthUmaTicketResponseModeEnum.PERMISSIONS,
        )
    )

    assert result.status_code in (200, 201, 204)
