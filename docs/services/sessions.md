# Sessions Service

`SessionsService` exposes user/client session queries and session cleanup operations.

Typical methods:

- `get_user_sessions_async(user_id)`
- `get_client_sessions_async(query=None)`
- `delete_session_by_id_async(session_id, is_offline)`
- `logout_all_users_async()`
