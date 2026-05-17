# Authz Services

Authorization services are split by concern:

- `AuthzService` (settings)
- `AuthzScopeService`
- `AuthzResourceService`
- `AuthzPolicyService`
- `AuthzPermissionService`

Use the appropriate payload/query dataclasses from `pykeycloak_client.providers.payloads` and `pykeycloak_client.providers.queries`.
