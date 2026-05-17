# Auth Service

`AuthService` handles login, token refresh, introspection, revocation, user info, and OIDC metadata.

Typical methods:

- `client_login_async()`
- `user_login_async(payload)`
- `refresh_token_async(payload)`
- `get_user_info_async(access_token)`
- `logout_async(refresh_token)`
- `revoke_async(refresh_token)`
