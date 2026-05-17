# Queries Reference

## `AdminRealmClientRoleGroupQuery`

| Field | Type | Default |
|---|---|---|
| `max` | `<class 'int'>` | `factory()` |
| `first` | `<class 'int'>` | `0` |
| `find_all` | `<class 'bool'>` | `False` |
| `brief_representation` | `<class 'bool'>` | `False` |

## `AdminRolesQuery`

| Field | Type | Default |
|---|---|---|
| `search` | `str | None` | `None` |
| `max` | `<class 'int'>` | `factory()` |
| `first` | `<class 'int'>` | `0` |
| `find_all` | `<class 'bool'>` | `False` |
| `brief_representation` | `<class 'bool'>` | `False` |

## `BaseQuery`

| Field | Type | Default |
|---|---|---|

## `BriefRepresentationQuery`

| Field | Type | Default |
|---|---|---|
| `brief_representation` | `<class 'bool'>` | `False` |

## `FilterFindPolicyParams`

| Field | Type | Default |
|---|---|---|
| `fields` | `list[str] | None` | `None` |
| `name` | `str | None` | `None` |

## `FilterQueryParams`

| Field | Type | Default |
|---|---|---|
| `max` | `<class 'int'>` | `factory()` |
| `first` | `<class 'int'>` | `0` |
| `find_all` | `<class 'bool'>` | `False` |
| `name` | `<class 'str'>` | `''` |
| `exact_name` | `<class 'bool'>` | `False` |
| `uri` | `<class 'str'>` | `''` |
| `owner` | `str | None` | `None` |
| `resource_type` | `str | None` | `None` |
| `scope` | `str | None` | `None` |
| `matching_uri` | `<class 'bool'>` | `False` |

## `FindPermissionQuery`

| Field | Type | Default |
|---|---|---|
| `max` | `<class 'int'>` | `factory()` |
| `first` | `<class 'int'>` | `0` |
| `find_all` | `<class 'bool'>` | `False` |
| `fields` | `list[str] | None` | `None` |
| `name` | `str | None` | `None` |
| `owner` | `str | None` | `None` |
| `permission` | `bool | None` | `None` |
| `policy_id` | `str | None` | `None` |
| `resource` | `str | None` | `None` |
| `resource_type` | `str | None` | `None` |
| `scope` | `str | None` | `None` |
| `type` | `str | None` | `None` |

## `GetUsersCountQuery`

| Field | Type | Default |
|---|---|---|
| `search` | `str | None` | `None` |

## `GetUsersQuery`

| Field | Type | Default |
|---|---|---|
| `max` | `<class 'int'>` | `factory()` |
| `first` | `<class 'int'>` | `0` |
| `find_all` | `<class 'bool'>` | `False` |
| `search` | `str | None` | `None` |

## `GroupListQuery`

| Field | Type | Default |
|---|---|---|
| `search` | `str | None` | `None` |
| `brief_representation` | `<class 'bool'>` | `False` |
| `max` | `<class 'int'>` | `factory()` |
| `first` | `<class 'int'>` | `0` |
| `find_all` | `<class 'bool'>` | `False` |
| `exact` | `<class 'bool'>` | `False` |
| `populate_hierarchy` | `<class 'bool'>` | `True` |
| `q` | `str | None` | `None` |
| `sub_group_count` | `<class 'bool'>` | `True` |

## `GroupMemberListQuery`

| Field | Type | Default |
|---|---|---|
| `brief_representation` | `<class 'bool'>` | `False` |
| `max` | `<class 'int'>` | `factory()` |
| `first` | `<class 'int'>` | `0` |
| `find_all` | `<class 'bool'>` | `False` |

## `PaginationQuery`

| Field | Type | Default |
|---|---|---|
| `max` | `<class 'int'>` | `factory()` |
| `first` | `<class 'int'>` | `0` |
| `find_all` | `<class 'bool'>` | `False` |

## `ResourcesListQuery`

| Field | Type | Default |
|---|---|---|
| `max` | `<class 'int'>` | `factory()` |
| `first` | `<class 'int'>` | `0` |
| `find_all` | `<class 'bool'>` | `False` |
| `deep` | `<class 'bool'>` | `True` |
| `matchingUri` | `str | None` | `None` |
| `name` | `str | None` | `None` |
| `owner` | `str | None` | `None` |
| `scope` | `str | None` | `None` |
| `type` | `str | None` | `None` |
| `uri` | `str | None` | `None` |

## `RoleMembersListQuery`

| Field | Type | Default |
|---|---|---|
| `brief_representation` | `<class 'bool'>` | `False` |
| `max` | `<class 'int'>` | `factory()` |
| `first` | `<class 'int'>` | `0` |
| `find_all` | `<class 'bool'>` | `False` |

## `SearchQuery`

| Field | Type | Default |
|---|---|---|
| `search` | `str | None` | `None` |
