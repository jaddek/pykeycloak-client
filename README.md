# PyKeycloak

PyKeycloak is a library for working with Keycloak that provides asynchronous methods for authentication, token management, and permission handling.

## What's Different from Other Libraries

- Sanitized logging: Automatically hide sensitive data in request/response logs.
- Httpx-powered: Gain full control using standard httpx client configuration.
- Rich Request/Response handling: Access a comprehensive list of parameters and detailed response fields.
- Flexible Data Access: Easily work with both raw data and structured representations.
- Environment-based config: Quick setup using environment variables.

## Installation

To install dependencies for local development, use the following command:

```bash
make install
```

## Development and Security Tooling

Runtime users of the library only install `pykeycloak` and its package dependencies.

For contributors (local checks + CI parity), install:

- `uv`
- `pre-commit`

Then run:

```bash
make install
uv run pre-commit install
```

Security checks are executed in both pre-commit and GitHub Actions:

- Dependency CVE audit: `pip-audit --strict`

## Release Version Bump

Releases are tag-driven via GitHub Actions:

- Tag format: `vX.Y.Z` (example: `v0.7.4`)
- On tag push, CI syncs `pyproject.toml` version from the tag before build/publish.
- After successful publish, GitHub Release is created automatically with generated release notes.
- Build artifacts include a CycloneDX SBOM (`sbom.cyclonedx.json`) attached to the GitHub Release.
- CI enforces an SBOM license deny policy (fails on disallowed copyleft licenses by default).
- License policy is defined in `.license-policy.toml` (`deny = [...]`).

Local helpers:

```bash
make release-bump                    # uses GITHUB_REF_NAME
make release-bump-tag TAG=v0.7.4     # explicit tag
```

## Usage Examples

The library can be used in 3 different ways:

1. Make requests directly through the client
2. Use the provider to get a response with content
3. Use the service to get either raw responses or Representation objects corresponding to the data received from Keycloak

### MCP Server

This repository includes an MCP server: `mcp_server.py`.

Run MCP smoke test:

```bash
make mcp-smoke
```

Run server:

```bash
uv run python mcp_server.py
```

MCP runtime env vars:

- `MCP_TRANSPORT` (`stdio`, `sse`, or `streamable-http`; default `stdio`)
- `MCP_HOST` (default `127.0.0.1`)
- `MCP_PORT` (default `8000`)

Codex MCP config example (`~/.codex/config.toml`):

```toml
[mcp_servers.pykeycloak]
command = "uv"
args = ["run", "python", "mcp_server.py"]
cwd = "path/to/PyKeycloak"

[mcp_servers.pykeycloak.env]
MCP_TRANSPORT = "stdio"
MCP_HOST = "127.0.0.1"
MCP_PORT = "8000"
KEYCLOAK_BASE_URL = "http://127.0.0.1:8080"
```

Set `cwd` to your local repository path.

Main MCP tools:

- `health`
- `keycloak_register`
- `keycloak_register_from_env`
- `keycloak_list_methods`
- `keycloak_call`
- `keycloak_close_all`

MCP client configuration examples:

1. Codex (`~/.codex/config.toml`)

```toml
[mcp_servers.pykeycloak]
command = "uv"
args = ["run", "python", "mcp_server.py"]
cwd = "path/to/PyKeycloak"

[mcp_servers.pykeycloak.env]
MCP_TRANSPORT = "stdio"
KEYCLOAK_BASE_URL = "http://127.0.0.1:8080"
```

2. Claude Desktop (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "pykeycloak": {
      "command": "uv",
      "args": ["run", "python", "mcp_server.py"],
      "cwd": "path/to/PyKeycloak",
      "env": {
        "MCP_TRANSPORT": "stdio",
        "KEYCLOAK_BASE_URL": "http://127.0.0.1:8080"
      }
    }
  }
}
```

3. Cursor (MCP JSON config)

```json
{
  "mcpServers": {
    "pykeycloak": {
      "command": "uv",
      "args": ["run", "python", "mcp_server.py"],
      "cwd": "path/to/PyKeycloak",
      "env": {
        "MCP_TRANSPORT": "stdio",
        "KEYCLOAK_BASE_URL": "http://127.0.0.1:8080"
      }
    }
  }
}
```

4. Cline (MCP JSON config)

```json
{
  "mcpServers": {
    "pykeycloak": {
      "command": "uv",
      "args": ["run", "python", "mcp_server.py"],
      "cwd": "path/to/PyKeycloak",
      "env": {
        "MCP_TRANSPORT": "stdio",
        "KEYCLOAK_BASE_URL": "http://127.0.0.1:8080"
      }
    }
  }
}
```

5. Continue (MCP JSON config)

```json
{
  "mcpServers": {
    "pykeycloak": {
      "command": "uv",
      "args": ["run", "python", "mcp_server.py"],
      "cwd": "path/to/PyKeycloak",
      "env": {
        "MCP_TRANSPORT": "stdio",
        "KEYCLOAK_BASE_URL": "http://127.0.0.1:8080"
      }
    }
  }
}
```

After connecting your MCP client, test with this sequence:

1. `health`
2. `keycloak_register_from_env` (or `keycloak_register`)
3. `keycloak_list_methods`
4. `keycloak_call`

## Constants

*Dynamic environment*

```shell
## These variables are dependant on client name
##
## KEYCLOAK_REALM_{realm_client_name}_REALM_NAME
##
## When the instance attached to container it looking for environment variables
## KEYCLOAK_REALM_{realm_client_name}_CLIENT_ID
## KEYCLOAK_REALM_{realm_client_name}_CLIENT_SECRET
##
## pykeycloak_client.register(key, RealmClient.from_env(client_name=realm_client_name))
##
## But you don't need those when making RealmClient not from env
##
KEYCLOAK_REALM_OTAGO_SERVICE_REALM_NAME=
KEYCLOAK_REALM_OTAGO_SERVICE_CLIENT_UUID=
KEYCLOAK_REALM_OTAGO_SERVICE_CLIENT_ID=
KEYCLOAK_REALM_OTAGO_SERVICE_CLIENT_SECRET=

KEYCLOAK_REALM_OTAGO_SSO_REALM_NAME=
KEYCLOAK_REALM_OTAGO_SSO_CLIENT_UUID=
KEYCLOAK_REALM_OTAGO_SSO_CLIENT_ID=
KEYCLOAK_REALM_OTAGO_SSO_CLIENT_SECRET=
##
```

*Default environment*

```shell
KEYCLOAK_BASE_URL=
KEYCLOAK_HTTPX_CLIENT_PARAMS_HTTP1=
KEYCLOAK_HTTPX_CLIENT_PARAMS_HTTP2=
KEYCLOAK_HTTPX_CLIENT_PARAMS_SSL_VERIFY=
KEYCLOAK_HTTPX_CLIENT_PARAMS_FOLLOW_REDIRECTS=
KEYCLOAK_HTTPX_CLIENT_PARAMS_TRUST_ENV=
KEYCLOAK_HTTPX_CLIENT_PARAMS_TIMEOUT=
KEYCLOAK_HTTPX_CLIENT_PARAMS_MAX_CONNECTIONS=
KEYCLOAK_HTTPX_CLIENT_PARAMS_MAX_KEEPALIVE_CONNECTIONS=
KEYCLOAK_HTTPX_CLIENT_PARAMS_KEEPALIVE_EXPIRY=
KEYCLOAK_HTTPX_CLIENT_PARAMS_MAX_REDIRECTS=
KEYCLOAK_HTTPX_CLIENT_PARAMS_DEFAULT_ENCODING=utf-8
KEYCLOAK_MAX_ROWS_QUERY_LIMIT=1000

KEYCLOAK_HTTPX_HTTP_TRANSPORT_HTTP_VERIFY=
KEYCLOAK_HTTPX_HTTP_TRANSPORT_HTTP_CERT=
KEYCLOAK_HTTPX_HTTP_TRANSPORT_HTTP_TRUST_ENV=
KEYCLOAK_HTTPX_HTTP_TRANSPORT_HTTP_HTTP1=
KEYCLOAK_HTTPX_HTTP_TRANSPORT_HTTP_HTTP2=
KEYCLOAK_HTTPX_HTTP_TRANSPORT_HTTP_RETRIES=
KEYCLOAK_HTTPX_HTTP_TRANSPORT_HTTP_PROXY=
KEYCLOAK_HTTPX_HTTP_TRANSPORT_HTTP_UDS=
KEYCLOAK_HTTPX_HTTP_TRANSPORT_HTTP_LOCAL_ADDRESS=
KEYCLOAK_HTTPX_HTTP_TRANSPORT_HTTP_MAX_CONNECTIONS=
KEYCLOAK_HTTPX_HTTP_TRANSPORT_HTTP_KEEPALIVE_EXPIRY=
KEYCLOAK_HTTPX_HTTP_TRANSPORT_HTTP_MAX_KEEPALIVE_CONNECTIONS=

KEYCLOAK_HTTP_RETRY_ENABLED=true
KEYCLOAK_HTTP_RETRY_MAX_ATTEMPTS=3
KEYCLOAK_HTTP_RETRY_BASE_DELAY_SECONDS=0.2
KEYCLOAK_HTTP_RETRY_MAX_DELAY_SECONDS=2.0
KEYCLOAK_HTTP_RETRY_JITTER_SECONDS=0.1
KEYCLOAK_HTTP_RETRY_METHODS=GET,HEAD,OPTIONS,DELETE

DATA_SANITIZER_EXTRA_SENSITIVE_KEYS=

UMA_PERMISSIONS_CHUNK_SIZE=1

```

### Initial start

```python
from pykeycloak_client.pykeycloak import PyKeycloak
from pykeycloak_client.core.realm import RealmClient

key = "otago_service"
pkc = PyKeycloak()

pkc.register(key, RealmClient.from_env(client_name=key))
pkc.get(key)
```

### Providers

- `KeycloakInMemoryProviderAsync` - Asynchronous provider for working with Keycloak that provides methods for authentication, token refresh, user information retrieval, logout, token introspection, device authentication, and certificate retrieval.

### Services

- `AuthService` - authentication, token refresh, user information retrieval, logout, token introspection, device authentication, and certificate retrieval.
- `UmaService`  - UMA permissions.
- `UsersService`
- `RolesService`
- `SessionsService`
- `ClientsService`
- `AuthzService`
- `AuthzResourceService`
- `AuthzScopeService`
- `AuthzPermissionService`
- `AuthzPolicyService`
- `WellKnownService`

### Core Entities

#### Payloads

- `TokenIntrospectionPayload` - Payload for token introspection containing the token.

- `RTPIntrospectionPayload` - Payload for token introspection inherited from `TokenIntrospectionPayload`, containing the token type.

- `ObtainTokenPayload` - Base class for obtaining a token, containing the scope and grant type.

- `UserCredentialsLoginPayload` - Payload for user authentication containing username and password.

- `ClientCredentialsLoginPayload` - Payload for client authentication used to obtain a client token.

- `RefreshTokenPayload` - Payload for refreshing a token containing the refresh token.

- `UMAAuthorizationPayload` - Payload for UMA authorization containing audience, permissions, and other parameters.



#### Representations

Representations duplicate the data from Keycloak documentation based on the actual values they return.

`TokenRepresentation` - Representation of a token containing information about the access token, expiration time, scope, and token type.

`UserInfoRepresentation` - Representation of user information containing user data such as first name, last name, email address, and other attributes.

`RealmAccessRepresentation` - Representation of realm access containing user roles in the realm.

`IntrospectRepresentation` - Representation of token introspection result containing token information such as audience, expiration time, token type, and other attributes.

#### Client

`RealmClient` - Entity that stores realm data:

```python
import os
from pykeycloak_client.core.realm import RealmClient

## To get pre-configured client based on environment variables
RealmClient.from_env(client_name='random_client_name')

# or if you hande environment variables manually
RealmClient(
    realm_name='realm_name',
    client_id=os.getenv("KEYCLOAK_REALM_CLIENT_ID"),
    client_uuid=os.getenv("KEYCLOAK_REALM_CLIENT_UUID"),
    client_secret=os.getenv("KEYCLOAK_REALM_CLIENT_SECRET")
)
```

#### Sanitizer

Processes headers and request/response logs, hiding all critical information and marking it as hidden.

```python
import os
from pykeycloak_client.core.sanitizer import SensitiveDataSanitizer

SensitiveDataSanitizer.from_env()

SensitiveDataSanitizer(
    sensitive_keys=frozenset(os.getenv("DATA_SANITIZER_EXTRA_SENSITIVE_KEYS", None))
)
```

### Client Initialization

To get started, you need to initialize the client using environment variables:

### User Authentication

To authenticate a user, use the `user_login_async` method:

```python
from pykeycloak_client.providers.payloads import UserCredentialsLoginPayload
from pykeycloak_client.pykeycloak import PyKeycloak

pkc = PyKeycloak()

# add client ....

token = await pkc.get('otago_client').auth.user_login_async(
    payload=UserCredentialsLoginPayload(
        username=username,
        password=password,
    ))
```

### Token Refresh

To refresh a token, use the `refresh_token_async` method:

```python
from pykeycloak_client.pykeycloak import PyKeycloak

pkc = PyKeycloak()

# add client ....

token = await pkc.get('otago_client').auth.refresh_token_async(
    payload=RefreshTokenPayload(refresh_token=token.refresh_token)
)
```

## Integration Smoke Tests

Integration tests are disabled by default and run only against a real Keycloak instance.

Required environment variables:

```shell
PYKEYCLOAK_INTEGRATION_ENABLED=1
KEYCLOAK_BASE_URL=http://localhost:8080
KEYCLOAK_REALM_IT_REALM_NAME=master
KEYCLOAK_REALM_IT_CLIENT_UUID=<client-uuid>
KEYCLOAK_REALM_IT_CLIENT_ID=<client-id>
KEYCLOAK_REALM_IT_CLIENT_SECRET=<client-secret>
```

Optional variables for user login + UMA smoke test:

```shell
KEYCLOAK_IT_USERNAME=<username>
KEYCLOAK_IT_PASSWORD=<password>
KEYCLOAK_IT_UMA_PERMISSIONS=/resource#view,/resource#update
```

Run:

```bash
uv run pytest tests/integration -m integration -vv -s
```

CI has a manual compatibility matrix against Keycloak `24.0`, `25.0`, and `26.0` via GitHub Actions `workflow_dispatch` input (`run_integration_matrix=true`).

### Token Introspection

To introspect a token, use the `introspect_async` method:

```python
from pykeycloak_client.providers.payloads import TokenIntrospectionPayload
from pykeycloak_client.pykeycloak import PyKeycloak

pkc = PyKeycloak()

# add client ....

introspection = await pkc.get('otago_client').auth.introspect_token_async(
    payload=TokenIntrospectionPayload(
        token=refresh.auth_token,
    )
)
```

### UMA Permission Retrieval

To retrieve UMA permissions, use the `get_uma_permissions_async` method:

```python
from pykeycloak_client.providers.payloads import UMAAuthorizationPayload
from pykeycloak_client.pykeycloak import PyKeycloak

pkc = PyKeycloak()

# add client ....

permissions = await pkc.get('otago_client').uma.get_uma_permissions_async(
    payload=UMAAuthorizationPayload(
        audience=client.client_id,
        subject_token=token.auth_token,  # user token
        permissions=['otago/users#view']
    )
)
```

### User Information Retrieval

To retrieve user information, use the `get_user_info_async` method:

```python
from pykeycloak_client.pykeycloak import PyKeycloak

pkc = PyKeycloak()

# add client ....

user_info = await pkc.get('otago_client').auth.get_user_info_async(
    access_token=refresh.auth_token
)
```

### Logout

To log out, use the `logout_async` method:

```python
from pykeycloak_client.pykeycloak import PyKeycloak

pkc = PyKeycloak()

# add client ....

await pkc.get('otago_client').auth.logout_async(refresh.refresh_token)
```

### Certificate Retrieval

To retrieve certificates, use the `get_certs_async` method:

```python
from pykeycloak_client.pykeycloak import PyKeycloak

pkc = PyKeycloak()

# add client ....

certs = await pkc.get('otago_client').well_known.get_certs_async()
```

### Other Methods

All services are available in protocols.py with their methods.

## License

This project is licensed under the MIT License.
