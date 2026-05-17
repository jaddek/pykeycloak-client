# Roles Service

`RolesService` manages client roles and role assignment.

Typical methods:

- `get_client_roles_async()`
- `get_role_by_name_async(role_name)`
- `create_role_async(payload)`
- `update_role_by_name_async(role_name, payload)`
- `delete_role_by_name_async(role_name)`
- `assign_role_async(user_id, roles)`
