# Quickstart

## Install

```bash
uv sync
```

## Configure environment

Required base variable:

```bash
export KEYCLOAK_BASE_URL=http://127.0.0.1:8080
```

Required client variables (replace `OTAGO_SERVICE` with your key):

```bash
export KEYCLOAK_REALM_OTAGO_SERVICE_REALM_NAME=your-realm
export KEYCLOAK_REALM_OTAGO_SERVICE_CLIENT_UUID=00000000-0000-0000-0000-000000000000
export KEYCLOAK_REALM_OTAGO_SERVICE_CLIENT_ID=your-client-id
export KEYCLOAK_REALM_OTAGO_SERVICE_CLIENT_SECRET=your-client-secret
```

## First call

```python
import asyncio

from pykeycloak_client.core.realm import RealmClient
from pykeycloak_client.pykeycloak import PyKeycloak


async def main() -> None:
    key = "otago_service"

    pkc = PyKeycloak()
    pkc.register(key=key, realm_client=RealmClient.from_env(client_name=key))

    service = pkc.get(key)
    conf = await service.well_known.get_openid_configuration_async()
    print(conf)


if __name__ == "__main__":
    asyncio.run(main())
```
