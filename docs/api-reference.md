# API Reference

This project exposes API surface through service classes and typed payload/query models.

## Service classes

- `AuthService`
- `UmaService`
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

## Typed models

- Payloads: `pykeycloak_client.providers.payloads`
- Queries: `pykeycloak_client.providers.queries`
- Representations: `pykeycloak_client.services.representations`

## Runtime introspection via MCP

For exact callable methods in your installed version:

1. Start MCP server: `uv run python mcp_server.py`
2. Register a key: `keycloak_register_from_env` or `keycloak_register`
3. List methods: `keycloak_list_methods`
4. Invoke methods: `keycloak_call`
