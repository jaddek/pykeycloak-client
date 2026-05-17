# Authz Permission Service

`AuthzPermissionService` manages permissions and permission-scope relations.

Typical methods:

- `create_permission_async(payload)`
- `get_permissions_async(query=None)`
- `get_permission_by_id_async(permission_id)`
- `update_permission_async(permission_id, payload)`
- `delete_permission_async(permission_id)`
