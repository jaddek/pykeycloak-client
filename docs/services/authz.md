# Authz Services Overview

Authorization support is split across five services:

- `AuthzService` for general authorization settings
- `AuthzResourceService` for resources
- `AuthzScopeService` for scopes
- `AuthzPermissionService` for permissions
- `AuthzPolicyService` for policies

Use dedicated pages for each sub-service:

- Resource: `services/authz-resource.md`
- Scope: `services/authz-scope.md`
- Permission: `services/authz-permission.md`
- Policy: `services/authz-policy.md`

Use payload/query dataclasses from:

- `pykeycloak_client.providers.payloads`
- `pykeycloak_client.providers.queries`
