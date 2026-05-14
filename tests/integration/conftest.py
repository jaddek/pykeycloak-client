# SPDX-License-Identifier: MIT
import os
import uuid
from collections.abc import AsyncGenerator

import pytest

from pykeycloak.core.realm import RealmClient
from pykeycloak.providers.payloads import UserCredentialsLoginPayload
from pykeycloak.pykeycloak import PyKeycloak

REQUIRED_ENV_VARS = (
    "PYKEYCLOAK_INTEGRATION_ENABLED",
    "KEYCLOAK_BASE_URL",
    "KEYCLOAK_REALM_IT_REALM_NAME",
    "KEYCLOAK_REALM_IT_CLIENT_UUID",
    "KEYCLOAK_REALM_IT_CLIENT_ID",
    "KEYCLOAK_REALM_IT_CLIENT_SECRET",
)


def _integration_enabled() -> bool:
    enabled = os.getenv("PYKEYCLOAK_INTEGRATION_ENABLED", "").strip().lower()
    if enabled not in {"1", "true", "yes", "on"}:
        return False
    return all(os.getenv(name) for name in REQUIRED_ENV_VARS[1:])


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if _integration_enabled():
        return

    skip_reason = (
        "integration env is not configured; set PYKEYCLOAK_INTEGRATION_ENABLED=1 and "
        "KEYCLOAK_BASE_URL + KEYCLOAK_REALM_IT_* variables"
    )
    skip_marker = pytest.mark.skip(reason=skip_reason)
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_marker)


@pytest.fixture(scope="session")
async def keycloak() -> AsyncGenerator:
    pkc = PyKeycloak()
    pkc.register("it", RealmClient.from_env(client_name="it"))
    client = pkc.get("it")
    try:
        yield client
    finally:
        await pkc._registry.close_all()


@pytest.fixture(scope="session")
def integration_user_credentials() -> UserCredentialsLoginPayload | None:
    username = os.getenv("KEYCLOAK_IT_USERNAME")
    password = os.getenv("KEYCLOAK_IT_PASSWORD")
    if not username or not password:
        return None
    return UserCredentialsLoginPayload(username=username, password=password)


@pytest.fixture
def unique_username() -> str:
    return f"pykeycloak-it-{uuid.uuid4().hex[:12]}"
