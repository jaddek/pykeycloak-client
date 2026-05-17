# Users Service

`UsersService` provides user CRUD, search/pagination, role member listing, and impersonation.

Typical methods:

- `get_user_async(user_id)`
- `get_users_async(query=None)`
- `create_user_async(payload)`
- `update_user_async(user_id, payload)`
- `delete_user_async(user_id)`
- `impersonate_async(user_id)`
