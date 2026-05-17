# UMA Service

`UmaService` provides User-Managed Access (UMA) permission checks.

Typical methods:

- `get_permissions_async(payload)`
- `get_permissions_raw_async(payload)`

Use `UMAAuthorizationPayload` to request decisions/scopes for a subject token.
