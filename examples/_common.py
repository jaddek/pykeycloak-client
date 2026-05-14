import logging
import os

from pykeycloak_client.core.protocols import KeycloakServiceFactoryProtocol
from pykeycloak_client.core.realm import RealmClient
from pykeycloak_client.providers.payloads import UserCredentialsLoginPayload
from pykeycloak_client.pykeycloak import PyKeycloak

logging.basicConfig(
    level=logging.DEBUG, format="%(name)s - %(levelname)s - %(message)s"
)

# Demo defaults for local development; override with env vars in real usage.
username = os.getenv("PYKEYCLOAK_EXAMPLE_USERNAME", "admin")
password = os.getenv("PYKEYCLOAK_EXAMPLE_PASSWORD", "password")  # noqa: S105
default_realm_client = os.getenv("PYKEYCLOAK_EXAMPLE_CLIENT", "otago_service")
__pkc = PyKeycloak()


def get_keycloak(key: str) -> KeycloakServiceFactoryProtocol:
    __pkc.register(key, RealmClient.from_env(client_name=key))

    return __pkc.get(key)


def get_user_credentials() -> UserCredentialsLoginPayload:
    return UserCredentialsLoginPayload(
        username=username,
        password=password,
    )
