# Payloads Reference

## `ClientCredentialsLoginPayload`

| Field | Type | Default |
|---|---|---|
| `scopes` | `str | None` | `None` |

## `ConfidentialClientRevokePayload`

| Field | Type | Default |
|---|---|---|
| `token` | `<class 'str'>` | `required` |
| `token_type_hint` | `<class 'str'>` | `'refresh_token'` |

## `CreateUserPayload`

| Field | Type | Default |
|---|---|---|
| `id` | `uuid.UUID | None` | `None` |
| `username` | `<class 'str'>` | `required` |
| `email` | `<class 'str'>` | `''` |
| `emailVerified` | `<class 'bool'>` | `False` |
| `first_name` | `<class 'str'>` | `''` |
| `last_name` | `<class 'str'>` | `''` |
| `enabled` | `<class 'bool'>` | `True` |
| `credentials` | `list[pykeycloak_client.providers.payloads.CredentialsPayload]` | `factory()` |
| `requiredActions` | `list[str]` | `factory()` |

## `CredentialsPayload`

| Field | Type | Default |
|---|---|---|
| `type` | `<class 'str'>` | `required` |
| `value` | `<class 'str'>` | `required` |

## `ObtainTokenPayload`

| Field | Type | Default |
|---|---|---|
| `scopes` | `str | None` | `None` |

## `PasswordCredentialsPayload`

| Field | Type | Default |
|---|---|---|
| `type` | `<class 'str'>` | `'password'` |
| `value` | `<class 'str'>` | `required` |
| `temporary` | `<class 'bool'>` | `False` |

## `Payload`

| Field | Type | Default |
|---|---|---|

## `PermissionPayload`

| Field | Type | Default |
|---|---|---|
| `id` | `str | None` | `None` |
| `name` | `str | None` | `None` |
| `type` | `str | None` | `None` |
| `logic` | `pykeycloak_client.core.enums.LogicEnum | None` | `None` |
| `description` | `str | None` | `None` |
| `decision_strategy` | `str | None` | `None` |

## `PermissionScopesPayload`

| Field | Type | Default |
|---|---|---|
| `name` | `<class 'str'>` | `required` |
| `policies` | `list[str]` | `factory()` |
| `decision_strategy` | `str | None` | `None` |

## `PublicClientRevokePayload`

| Field | Type | Default |
|---|---|---|
| `client_id` | `<class 'str'>` | `required` |
| `token` | `<class 'str'>` | `required` |
| `token_type_hint` | `<class 'str'>` | `'refresh_token'` |

## `RTPExchangeTokenPayload`

| Field | Type | Default |
|---|---|---|
| `scopes` | `str | None` | `None` |
| `refresh_token` | `<class 'str'>` | `required` |

## `RTPIntrospectionPayload`

| Field | Type | Default |
|---|---|---|
| `token` | `<class 'str'>` | `required` |
| `token_type_hint` | `<class 'str'>` | `'requesting_party_token'` |

## `RefreshTokenPayload`

| Field | Type | Default |
|---|---|---|
| `scopes` | `str | None` | `None` |
| `refresh_token` | `<class 'str'>` | `required` |

## `ResourcePayload`

| Field | Type | Default |
|---|---|---|
| `id` | `str | None` | `None` |
| `name` | `str | None` | `None` |
| `display_name` | `str | None` | `None` |
| `type` | `str | None` | `None` |
| `uris` | `list[str]` | `factory()` |
| `scopes` | `list[dict[str, str]]` | `factory()` |
| `attributes` | `dict[str, list[str]]` | `factory()` |

## `RoleAssignPayload`

| Field | Type | Default |
|---|---|---|
| `id` | `<class 'str'>` | `required` |
| `name` | `<class 'str'>` | `required` |

## `RolePayload`

| Field | Type | Default |
|---|---|---|
| `name` | `<class 'str'>` | `required` |
| `id` | `str | None` | `None` |
| `description` | `str | None` | `None` |
| `scope_param_required` | `bool | None` | `None` |
| `composite` | `bool | None` | `None` |
| `container_id` | `str | None` | `None` |
| `attributes` | `dict[str, list[str]] | None` | `None` |

## `RolePolicyPayload`

| Field | Type | Default |
|---|---|---|
| `name` | `<class 'str'>` | `required` |
| `roles` | `list[str]` | `factory()` |

## `SSOLoginPayload`

| Field | Type | Default |
|---|---|---|
| `client_id` | `<class 'str'>` | `required` |
| `redirect_uri` | `<class 'str'>` | `required` |
| `state` | `<class 'str'>` | `required` |
| `scopes` | `str | None` | `None` |

## `TokenIntrospectionPayload`

| Field | Type | Default |
|---|---|---|
| `token` | `<class 'str'>` | `required` |

## `UMAAuthorizationPayload`

| Field | Type | Default |
|---|---|---|
| `audience` | `str | None` | `None` |
| `permissions` | `list[str]` | `required` |
| `response_mode` | `<enum 'UrnIetfOauthUmaTicketResponseModeEnum'>` | `<UrnIetfOauthUmaTicketResponseModeEnum.DECISION: 'decision'>` |
| `permission_resource_format` | `<enum 'UrnIetfOauthUmaTicketPermissionResourceFormatEnum'>` | `<UrnIetfOauthUmaTicketPermissionResourceFormatEnum.URI: 'uri'>` |
| `subject_token` | `<class 'str'>` | `required` |
| `permission_resource_matching_uri` | `<class 'bool'>` | `False` |
| `response_include_resource_name` | `<class 'bool'>` | `False` |

## `UpdateUserPayload`

| Field | Type | Default |
|---|---|---|
| `id` | `uuid.UUID | None` | `None` |
| `email` | `str | None` | `None` |
| `emailVerified` | `bool | None` | `None` |
| `first_name` | `str | None` | `None` |
| `last_name` | `str | None` | `None` |
| `enabled` | `bool | None` | `None` |
| `credentials` | `list[pykeycloak_client.providers.payloads.CredentialsPayload] | None` | `None` |
| `requiredActions` | `list[str] | None` | `None` |

## `UserAuthorisationCodePayload`

| Field | Type | Default |
|---|---|---|
| `scopes` | `str | None` | `None` |
| `code` | `<class 'str'>` | `required` |
| `redirect_uri` | `<class 'str'>` | `required` |

## `UserCredentialsLoginPayload`

| Field | Type | Default |
|---|---|---|
| `scopes` | `str | None` | `None` |
| `username` | `<class 'str'>` | `required` |
| `password` | `<class 'str'>` | `required` |

## `UserUpdateEnablePayload`

| Field | Type | Default |
|---|---|---|
| `enabled` | `<class 'bool'>` | `True` |

## `UserUpdatePasswordPayload`

| Field | Type | Default |
|---|---|---|
| `credentials` | `list[dict[str, Any]]` | `factory()` |
