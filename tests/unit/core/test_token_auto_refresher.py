# SPDX-License-Identifier: MIT
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from pykeycloak.core.token_manager import (
    AuthToken,
    TokenAutoRefresher,
    TokenManager,
    inject_verified_access_token,
    mark_need_access_token_initialization,
)
from pykeycloak.providers.payloads import ClientCredentialsLoginPayload


@pytest.fixture
def token_manager():
    return TokenManager()


def _make_token_response(access_token: str = "tok", refresh_token: str = "ref"):
    response = MagicMock()
    response.json.return_value = {
        "access_token": access_token,
        "expires_in": 3600,
        "refresh_token": refresh_token,
        "refresh_expires_in": 7200,
    }
    return response


def _make_decorated_client(token_manager: TokenManager):
    refresher = TokenAutoRefresher(token_manager=token_manager)

    @refresher
    class DummyClient:
        @staticmethod
        def token_manager_update_access_token():
            return AsyncMock(return_value=_make_token_response("new_tok", "new_ref"))

        @mark_need_access_token_initialization
        async def login(self, payload):  # noqa: ANN001
            return _make_token_response()

        @inject_verified_access_token
        async def protected(self, *, access_token: str) -> str:
            return access_token

    return DummyClient()


class TestTokenAutoRefresher:
    async def test_initialization_wrapper_updates_token(self, token_manager):
        client = _make_decorated_client(token_manager)

        await client.login(payload=ClientCredentialsLoginPayload())

        assert token_manager.auth_tokens is not None
        assert token_manager.auth_tokens.access_token == "tok"
        assert token_manager.auth_tokens.refresh_token == "ref"

    async def test_verified_wrapper_uses_get_valid_token(self, token_manager):
        expired = AuthToken(
            access_token="old",
            expires_in=10,
            refresh_token="ref",
            refresh_expires_in=7200,
            issued_at=datetime.now(UTC) - timedelta(seconds=100),
        )
        token_manager.update_auth_tokens(expired)
        client = _make_decorated_client(token_manager)

        token = await client.protected()

        assert token == "new_tok"

    async def test_verified_wrapper_raises_when_refresh_missing(self, token_manager):
        expired_no_refresh = AuthToken(
            access_token="old",
            expires_in=10,
            refresh_token=None,
            refresh_expires_in=None,
            issued_at=datetime.now(UTC) - timedelta(seconds=100),
        )
        token_manager.update_auth_tokens(expired_no_refresh)
        client = _make_decorated_client(token_manager)

        with pytest.raises(RuntimeError, match="refresh_token first"):
            await client.protected()
