# Authz Policy Service

`AuthzPolicyService` manages policies and policy associations.

Typical methods:

- `create_policy_async(payload)`
- `get_policies_async(query=None)`
- `get_policy_by_id_async(policy_id)`
- `update_policy_async(policy_id, payload)`
- `delete_policy_async(policy_id)`
