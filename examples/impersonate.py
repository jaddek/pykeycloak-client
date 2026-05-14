import asyncio
import logging

from _common import default_realm_client, get_keycloak

logging.basicConfig(
    level=logging.DEBUG, format="%(name)s - %(levelname)s - %(message)s"
)


async def main():
    keycloak = get_keycloak(default_realm_client)

    await keycloak.auth.client_login_async()

    users, _count = await keycloak.users.get_users_async()
    if not users:
        print("No users found to impersonate")
        return

    # Pick first available user to keep the example reproducible across environments.
    user_id = users[0].id
    result = await keycloak.users.impersonate_async(user_id)  # noqa: F841

    print("-----")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
