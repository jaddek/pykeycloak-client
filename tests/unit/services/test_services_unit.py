# SPDX-License-Identifier: MIT
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from pykeycloak.core.enums import UrnIetfOauthUmaTicketResponseModeEnum
from pykeycloak.core.exceptions import KeycloakException, KeycloakHTTPException
from pykeycloak.providers.payloads import (
    ClientCredentialsLoginPayload,
    CreateUserPayload,
    PermissionPayload,
    PermissionScopesPayload,
    RefreshTokenPayload,
    ResourcePayload,
    RoleAssignPayload,
    RolePayload,
    RolePolicyPayload,
    RTPIntrospectionPayload,
    TokenIntrospectionPayload,
    UMAAuthorizationPayload,
    UpdateUserPayload,
    UserAuthorisationCodePayload,
    UserCredentialsLoginPayload,
    UserUpdateEnablePayload,
    UserUpdatePasswordPayload,
)
from pykeycloak.providers.queries import FilterFindPolicyParams, GetUsersQuery
from pykeycloak.services.services import (
    AuthService,
    AuthzPermissionService,
    AuthzPolicyService,
    AuthzResourceService,
    AuthzScopeService,
    AuthzService,
    ClientsService,
    RolesService,
    SessionsService,
    UmaService,
    UsersService,
    WellKnownService,
)


def make_response(
    *,
    status_code: int = 200,
    text: str = "",
    body: object | None = None,
    headers: dict[str, str] | None = None,
):
    response = MagicMock()
    response.status_code = status_code
    response.text = text
    response.headers = headers or {}
    response.content = b""
    response.json.return_value = body
    return response


class TestUsersService:
    @pytest.fixture
    def validator(self):
        v = MagicMock()
        v.validate = MagicMock(return_value=None)
        return v

    @pytest.fixture
    def provider(self):
        p = MagicMock()
        p.create_user_async = AsyncMock()
        p.get_users_count_async = AsyncMock()
        p.get_users_async = AsyncMock()
        return p

    async def test_create_user_extracts_uuid(self, provider, validator):
        user_id = str(uuid4())
        provider.create_user_async.return_value = make_response(
            status_code=201,
            headers={"Location": f"https://kc/admin/realms/r/users/{user_id}"},
        )
        service = UsersService(provider=provider, validator=validator)

        result = await service.create_user_async(
            payload=CreateUserPayload(username="u", email="u@example.com")
        )

        assert result == user_id

    async def test_create_user_without_headers_raises(self, provider, validator):
        provider.create_user_async.return_value = make_response(status_code=201, headers={})
        service = UsersService(provider=provider, validator=validator)

        with pytest.raises(KeycloakException, match="Headers should be present"):
            await service.create_user_async(
                payload=CreateUserPayload(username="u", email="u@example.com")
            )

    async def test_create_user_invalid_location_raises(self, provider, validator):
        provider.create_user_async.return_value = make_response(
            status_code=201, headers={"Location": "https://kc/admin/realms/r/users/not-uuid"}
        )
        service = UsersService(provider=provider, validator=validator)

        with pytest.raises(ValueError, match="Invalid user uuid"):
            await service.create_user_async(
                payload=CreateUserPayload(username="u", email="u@example.com")
            )

    async def test_create_user_headers_without_location_raises(self, provider, validator):
        provider.create_user_async.return_value = make_response(
            status_code=201, headers={"X-Other": "1"}
        )
        service = UsersService(provider=provider, validator=validator)

        with pytest.raises(ValueError, match="Location header is missing"):
            await service.create_user_async(
                payload=CreateUserPayload(username="u", email="u@example.com")
            )

    async def test_create_user_sequence_headers_branch(self, provider, validator):
        user_id = str(uuid4())
        response = make_response(status_code=201, headers={})
        response.headers = [
            ("X-Other", "1"),
            ("Location", f"https://kc/admin/realms/r/users/{user_id}"),
        ]
        provider.create_user_async.return_value = response
        service = UsersService(provider=provider, validator=validator)

        result = await service.create_user_async(
            payload=CreateUserPayload(username="u", email="u@example.com")
        )

        assert result == user_id

    async def test_create_user_empty_location_hits_extract_uuid_empty(
        self, provider, validator
    ):
        provider.create_user_async.return_value = make_response(
            status_code=201, headers={"Location": ""}
        )
        service = UsersService(provider=provider, validator=validator)

        with pytest.raises(ValueError, match="Invalid user uuid"):
            await service.create_user_async(
                payload=CreateUserPayload(username="u", email="u@example.com")
            )

    async def test_get_users_count_invalid_type_raises(self, provider, validator):
        bad_response = make_response(status_code=200, body={"count": 1})
        provider.get_users_count_async.return_value = bad_response
        service = UsersService(provider=provider, validator=validator)

        with pytest.raises(ValueError, match="Expected numeric data"):
            await service.get_users_count_async()

    async def test_get_users_count_accepts_numeric_string(self, provider, validator):
        provider.get_users_count_async.return_value = make_response(
            status_code=200, body="3"
        )
        service = UsersService(provider=provider, validator=validator)

        assert await service.get_users_count_async() == 3

    async def test_get_user_and_get_users_mapping(self, provider, validator, monkeypatch):
        monkeypatch.setenv("KEYCLOAK_MAX_ROWS_QUERY_LIMIT", "1")
        provider.get_user_async = AsyncMock(
            return_value=make_response(
                status_code=200,
                text="ok",
                body={"id": "u1", "username": "user1", "emailVerified": True},
            )
        )
        provider.get_users_count_async = AsyncMock(
            return_value=make_response(status_code=200, text="1", body=1)
        )
        provider.get_users_async = AsyncMock(
            return_value=make_response(
                status_code=200,
                text="ok",
                body=[{"id": "u1", "username": "user1", "emailVerified": True}],
            )
        )
        service = UsersService(provider=provider, validator=validator)

        user = await service.get_user_async("u1")
        users, count = await service.get_users_async(
            query=GetUsersQuery(find_all=True, max=1)
        )

        assert user.id == "u1"
        assert len(users) == 1
        assert count == 1

    async def test_get_paginated_users_find_all(self, provider, validator, monkeypatch):
        monkeypatch.setenv("KEYCLOAK_MAX_ROWS_QUERY_LIMIT", "1")
        provider.get_users_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body=[{"id": "u1"}])
        )
        service = UsersService(provider=provider, validator=validator)
        query = GetUsersQuery(find_all=True, max=1, first=0)

        result = await service.get_paginated_users_async(users_count=2, query=query)

        assert len(result) == 2
        assert provider.get_users_async.await_count == 2

    async def test_get_users_raw_and_all_and_update_wrappers(
        self, provider, validator, monkeypatch
    ):
        monkeypatch.setenv("KEYCLOAK_MAX_ROWS_QUERY_LIMIT", "1")
        provider.get_users_count_async = AsyncMock(
            return_value=make_response(status_code=200, text="2", body=2)
        )
        provider.get_users_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body=[{"id": "u1"}])
        )
        provider.get_users_by_role_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body=[])
        )
        provider.update_user_by_id_async = AsyncMock(
            return_value=make_response(status_code=204, text="", body=None)
        )
        provider.update_user_enable_by_id_async = AsyncMock(
            return_value=make_response(status_code=204, text="", body=None)
        )
        provider.update_user_password_by_id_async = AsyncMock(
            return_value=make_response(status_code=204, text="", body=None)
        )
        provider.delete_user_async = AsyncMock(
            return_value=make_response(status_code=204, text="", body=None)
        )
        provider.impersonate_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body={})
        )
        service = UsersService(provider=provider, validator=validator)

        users_raw, count = await service.get_users_raw_async(
            query=GetUsersQuery(find_all=True, max=1)
        )
        assert count == 2
        assert len(users_raw) == 2

        users, users_count = await service.get_all_users_async()
        assert users_count == 2
        assert len(users) == 2

        await service.get_users_by_role_async("role")
        await service.update_user_async("uid", payload=UpdateUserPayload())
        await service.enable_user_async("uid", payload=UserUpdateEnablePayload(enabled=True))
        await service.update_user_password_async(
            "uid", payload=UserUpdatePasswordPayload(credentials=[])
        )
        await service.delete_user_async("uid")
        await service.impersonate_async("uid")


class TestUmaService:
    async def test_get_permissions_by_uris_chunks_deduplicates(self):
        provider = MagicMock()
        validator = MagicMock()
        validator.validate = MagicMock(return_value=None)
        service = UmaService(provider=provider, validator=validator, uma_permissions_chunk_size=1)

        r1 = make_response(
            status_code=200, text="ok", body=[{"rsid": "r1", "scopes": ["view"]}]
        )
        r2 = make_response(
            status_code=200, text="ok", body=[{"rsid": "r1", "scopes": ["view"]}]
        )
        provider.get_uma_permission_async = AsyncMock(side_effect=[r1, r2])

        result = await service.get_permissions_by_uris_chunks_async(
            payload=UMAAuthorizationPayload(
                permissions=["/a#view", "/b#view"],
                subject_token="token",
                response_mode=UrnIetfOauthUmaTicketResponseModeEnum.PERMISSIONS,
            ),
            chunk_size=1,
        )

        assert result == [{"rsid": "r1", "scopes": ["view"]}]

    async def test_get_permissions_by_uris_chunks_skips_403_exceptions(self):
        provider = MagicMock()
        validator = MagicMock()
        validator.validate = MagicMock(return_value=None)
        service = UmaService(provider=provider, validator=validator, uma_permissions_chunk_size=1)

        good = make_response(
            status_code=200, text="ok", body=[{"rsid": "r2", "scopes": ["view"]}]
        )
        forbidden = KeycloakHTTPException(message="forbidden", status_code=403)
        provider.get_uma_permission_async = AsyncMock(side_effect=[forbidden, good])

        result = await service.get_permissions_by_uris_chunks_async(
            payload=UMAAuthorizationPayload(
                permissions=["/a#view", "/b#view"],
                subject_token="token",
                response_mode=UrnIetfOauthUmaTicketResponseModeEnum.PERMISSIONS,
            ),
            chunk_size=1,
        )

        assert result == [{"rsid": "r2", "scopes": ["view"]}]

    async def test_get_permissions_by_uris_chunks_handles_decision_mode_and_non403(self):
        provider = MagicMock()
        validator = MagicMock()
        validator.validate = MagicMock(return_value=None)
        service = UmaService(provider=provider, validator=validator, uma_permissions_chunk_size=1)

        error = KeycloakHTTPException(message="bad", status_code=500)
        decision = make_response(status_code=200, text="ok", body={"result": True})
        provider.get_uma_permission_async = AsyncMock(side_effect=[error, decision])

        result = await service.get_permissions_by_uris_chunks_async(
            payload=UMAAuthorizationPayload(
                permissions=["/a#view", "/b#view"],
                subject_token="token",
                response_mode=UrnIetfOauthUmaTicketResponseModeEnum.DECISION,
            ),
            chunk_size=1,
        )

        assert result == [{"result": True}]


class TestAuthService:
    async def test_client_login_async_maps_token(self):
        provider = MagicMock()
        validator = MagicMock()
        validator.validate = MagicMock(return_value=None)
        provider.obtain_token_async = AsyncMock(
            return_value=make_response(
                status_code=200,
                text="ok",
                body={
                    "access_token": "a",
                    "expires_in": 300,
                    "scope": "openid",
                    "token_type": "Bearer",
                    "not-before-policy": 0,
                    "refresh_token": "r",
                    "refresh_expires_in": 600,
                },
            )
        )
        service = AuthService(provider=provider, validator=validator)

        token = await service.client_login_async()

        assert token.access_token == "a"
        assert token.refresh_token == "r"

    async def test_refresh_token_async_calls_provider(self):
        provider = MagicMock()
        validator = MagicMock()
        validator.validate = MagicMock(return_value=None)
        provider.refresh_token_async = AsyncMock(
            return_value=make_response(
                status_code=200,
                text="ok",
                body={
                    "access_token": "a2",
                    "expires_in": 300,
                    "scope": "openid",
                    "token_type": "Bearer",
                    "not-before-policy": 0,
                    "refresh_token": "r2",
                    "refresh_expires_in": 600,
                },
            )
        )
        service = AuthService(provider=provider, validator=validator)


        refreshed = await service.refresh_token_async(
            payload=RefreshTokenPayload(refresh_token="old")
        )

        assert refreshed.access_token == "a2"
        provider.refresh_token_async.assert_awaited_once()

    async def test_auth_service_other_methods(self):
        provider = MagicMock()
        validator = MagicMock()
        validator.validate = MagicMock(return_value=None)
        token_body = {
            "access_token": "a",
            "expires_in": 300,
            "scope": "openid",
            "token_type": "Bearer",
            "not-before-policy": 0,
            "refresh_token": "r",
            "refresh_expires_in": 600,
        }
        provider.get_sso_redirect_url = MagicMock(return_value="https://kc/auth")
        provider.obtain_token_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body=token_body)
        )
        provider.get_user_info_async = AsyncMock(
            return_value=make_response(
                status_code=200, text="ok", body={"sub": "u1", "preferred_username": "u"}
            )
        )
        provider.logout_async = AsyncMock(
            return_value=make_response(status_code=204, text="", body=None)
        )
        provider.introspect_token_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body={})
        )
        provider.auth_device_async = AsyncMock(
            return_value=make_response(
                status_code=200,
                text="ok",
                body={
                    "device_code": "d",
                    "user_code": "u",
                    "verification_uri": "http://v",
                    "expires_in": 100,
                    "interval": 5,
                },
            )
        )
        provider.revoke_async = AsyncMock(
            return_value=make_response(status_code=204, text="", body=None)
        )
        provider.get_uma_permission_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body={})
        )
        service = AuthService(provider=provider, validator=validator)

        assert service.get_redirect_code_url(
            UserAuthorisationCodePayload(code="c", redirect_uri="r")
        ) == "https://kc/auth"
        await service.user_login_raw_async(
            payload=UserCredentialsLoginPayload(username="u", password="p")
        )
        await service.exchange_code_to_token(
            payload=UserAuthorisationCodePayload(code="c", redirect_uri="r")
        )
        user_tok = await service.user_login_async(
            payload=UserCredentialsLoginPayload(username="u", password="p")
        )
        obt_tok = await service.obtain_token_async(
            payload=ClientCredentialsLoginPayload()
        )
        ui = await service.get_user_info_async("atk")
        await service.logout_raw_async("rt")
        await service.logout_async("rt")
        await service.introspect_token_raw_async(
            payload=TokenIntrospectionPayload(token="t")
        )
        await service.introspect_token_async(payload=RTPIntrospectionPayload(token="t"))
        await service.auth_device_raw_async()
        dev = await service.auth_device_async()
        await service.revoke_raw_async("rt")
        await service.revoke_async("rt")
        await service.get_uma_permission_async(
            payload=UMAAuthorizationPayload(permissions=["/a#v"], subject_token="t")
        )

        assert user_tok.access_token == "a"
        assert obt_tok.access_token == "a"
        assert ui.id == "u1"
        assert dev.device_code == "d"


class TestSessionsService:
    async def test_get_client_sessions_async_maps_items(self):
        provider = MagicMock()
        validator = MagicMock()
        validator.validate = MagicMock(return_value=None)
        provider.get_client_sessions_async = AsyncMock(
            return_value=make_response(
                status_code=200,
                text="ok",
                body=[{"id": "s1", "userId": "u1"}],
            )
        )
        service = SessionsService(provider=provider, validator=validator)

        sessions = await service.get_client_sessions_async()

        assert len(sessions) == 1
        assert sessions[0].id == "s1"
        assert sessions[0].user_id == "u1"

    async def test_other_sessions_methods(self):
        provider = MagicMock()
        validator = MagicMock()
        validator.validate = MagicMock(return_value=None)

        provider.get_user_sessions_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body=[{"id": "s2", "userId": "u2"}])
        )
        provider.get_client_sessions_count_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body={"count": 1})
        )
        provider.get_offline_sessions_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body=[{"id": "s3", "userId": "u3"}])
        )
        provider.get_offline_sessions_count_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body={"count": 2})
        )
        provider.remove_user_sessions_async = AsyncMock(
            return_value=make_response(status_code=204, text="", body=None)
        )
        provider.logout_all_users_async = AsyncMock(
            return_value=make_response(status_code=204, text="", body=None)
        )
        provider.get_client_session_stats_async = AsyncMock(
            return_value=make_response(
                status_code=200,
                text="ok",
                body=[{"id": "sid", "offline": "0", "clientId": "cid", "active": "1"}],
            )
        )
        provider.get_client_user_offline_sessions_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body={"id": "s4", "userId": "u4"})
        )
        provider.delete_session_by_id_async = AsyncMock(
            return_value=make_response(status_code=204, text="", body=None)
        )
        service = SessionsService(provider=provider, validator=validator)

        user_sessions = await service.get_user_sessions_async("u2")
        count = await service.get_client_sessions_count_async()
        offline = await service.get_offline_sessions_async()
        offline_count = await service.get_offline_sessions_count_async()
        await service.remove_user_sessions_raw_async("u2")
        await service.logout_all_users_raw_async()
        await service.logout_all_users_async()
        stats = await service.get_client_session_stats_async()
        one = await service.get_client_user_offline_sessions_async("u4")
        await service.delete_session_by_id_async("s4", is_offline=False)

        assert len(user_sessions) == 1
        assert count.count == 1
        assert len(offline) == 1
        assert offline_count.count == 2
        assert len(stats) == 1
        assert one.id == "s4"


class TestRolesService:
    async def test_role_methods_happy_path(self):
        provider = MagicMock()
        validator = MagicMock()
        validator.validate = MagicMock(return_value=None)

        provider.get_client_roles_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body=[])
        )
        provider.get_role_by_name_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body={})
        )
        provider.create_role_async = AsyncMock(
            return_value=make_response(status_code=201, text="", body=None)
        )
        provider.update_role_by_id_async = AsyncMock(return_value=None)
        provider.delete_role_by_id_async = AsyncMock(
            return_value=make_response(status_code=204, text="", body=None)
        )
        provider.delete_role_by_name_async = AsyncMock(
            return_value=make_response(status_code=204, text="", body=None)
        )
        provider.update_role_by_name_async = AsyncMock(
            return_value=make_response(status_code=204, text="", body=None)
        )
        provider.assign_role_async = AsyncMock(
            return_value=make_response(status_code=204, text="", body=None)
        )
        provider.unassign_role_async = AsyncMock(
            return_value=make_response(status_code=204, text="", body=None)
        )
        provider.get_client_roles_of_user_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body=[])
        )
        provider.get_composite_client_roles_of_user_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body=[])
        )
        provider.get_available_client_roles_of_user_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body=[])
        )
        provider.get_user_roles_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body=[])
        )

        service = RolesService(provider=provider, validator=validator)
        role_id = uuid4()
        await service.get_client_roles_async()
        await service.get_role_by_name_async("role")
        await service.create_role_async(payload=RolePayload(name="role"))
        await service.update_role_by_id_async(
            role_id=role_id, payload=RolePayload(name="role")
        )
        await service.delete_role_by_id_async(role_id=role_id)
        await service.delete_role_by_name_async("role")
        await service.update_role_by_name_async(
            "role", payload=RolePayload(name="role")
        )
        await service.assign_role_async(
            user_id="u1", roles=[RoleAssignPayload(id="1", name="r")]
        )
        await service.unassign_role_async(
            user_id="u1", roles=[RoleAssignPayload(id="1", name="r")]
        )
        await service.get_client_roles_of_user_async(user_id="u1")
        await service.get_composite_client_roles_of_user_async(user_id="u1")
        await service.get_available_client_roles_of_user_async(user_id="u1")
        await service.get_user_roles_async(user_id="u1")


class TestClientsAndAuthzServices:
    async def test_clients_authz_and_well_known(self):
        validator = MagicMock()
        validator.validate = MagicMock(return_value=None)

        clients_provider = MagicMock()
        clients_provider.get_client_async = AsyncMock(
            return_value=make_response(
                status_code=200, text="ok", body={"id": "c1", "clientId": "cid-1"}
            )
        )
        clients_provider.get_clients_async = AsyncMock(
            return_value=make_response(
                status_code=200, text="ok", body=[{"id": "c1", "clientId": "cid-1"}]
            )
        )
        clients_service = ClientsService(provider=clients_provider, validator=validator)
        one = await clients_service.get_client_async()
        many = await clients_service.get_clients_async()
        assert one.id == "c1"
        assert one.client_id == "cid-1"
        assert len(many) == 1

        authz_provider = MagicMock()
        authz_provider.get_client_authz_settings = AsyncMock(
            return_value=make_response(
                status_code=200,
                text="ok",
                body={"allowRemoteResourceManagement": True},
            )
        )
        authz_service = AuthzService(provider=authz_provider, validator=validator)
        settings = await authz_service.get_client_authz_settings_async()
        assert settings.allow_remote_resource_management is True

        authz_resource_provider = MagicMock()
        authz_resource_provider.get_resources_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body=[])
        )
        authz_resource_provider.create_resource_async = AsyncMock(
            return_value=make_response(status_code=201, text="", body=None)
        )
        authz_resource_provider.get_resource_by_id_async = AsyncMock(
            return_value=make_response(
                status_code=200, text="ok", body={"id": "res1", "name": "r"}
            )
        )
        authz_resource_provider.delete_resource_by_id_async = AsyncMock(
            return_value=make_response(status_code=204, text="", body=None)
        )
        authz_resource_provider.get_resource_permissions_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body=[])
        )
        authz_resource_service = AuthzResourceService(
            provider=authz_resource_provider, validator=validator
        )
        await authz_resource_service.get_resources_async()
        await authz_resource_service.create_resource_async(
            payload=ResourcePayload(name="r")
        )
        resource = await authz_resource_service.get_resource_by_id_async("res1")
        await authz_resource_service.delete_resource_by_id_async("res1")
        await authz_resource_service.get_resource_permissions_async("res1")
        assert resource.id == "res1"

        authz_scope_provider = MagicMock()
        authz_scope_provider.get_client_authz_scopes_async = AsyncMock(
            return_value=make_response(
                status_code=200, text="ok", body=[{"id": "s1", "name": "scope"}]
            )
        )
        authz_scope_service = AuthzScopeService(
            provider=authz_scope_provider, validator=validator
        )
        scopes = await authz_scope_service.get_client_authz_scopes_async()
        assert len(scopes) == 1
        assert scopes[0].id == "s1"

        authz_perm_provider = MagicMock()
        authz_perm_provider.create_client_authz_permission_based_on_resource_async = (
            AsyncMock(return_value=make_response(status_code=201, text="", body=None))
        )
        authz_perm_provider.create_client_authz_permission_based_on_scope_async = (
            AsyncMock(return_value=make_response(status_code=201, text="", body=None))
        )
        authz_perm_provider.get_permissions_async = AsyncMock(
            return_value=make_response(
                status_code=200, text="ok", body=[{"id": "p1", "name": "perm"}]
            )
        )
        authz_perm_provider.get_permission_based_on_scope_by_id_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body={"id": "p1"})
        )
        authz_perm_provider.get_permission_based_on_resource_by_id_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body={"id": "p1"})
        )
        authz_perm_provider.delete_permission_async = AsyncMock(
            return_value=make_response(status_code=204, text="", body=None)
        )
        authz_perm_provider.update_permission_scopes_async = AsyncMock(
            return_value=make_response(status_code=204, text="", body=None)
        )
        authz_perm_service = AuthzPermissionService(
            provider=authz_perm_provider, validator=validator
        )
        await authz_perm_service.create_client_authz_permission_based_on_resource_async(
            payload=PermissionPayload(name="p")
        )
        await authz_perm_service.create_client_authz_permission_based_on_scope_async(
            payload=PermissionPayload(name="p")
        )
        permissions = await authz_perm_service.get_permissions_async()
        await authz_perm_service.get_permission_based_on_scope_by_id_async("p1")
        await authz_perm_service.get_permission_based_on_resource_by_id_async("p1")
        await authz_perm_service.delete_permission_async("p1")
        await authz_perm_service.update_permission_scopes_async(
            "p1", payload=PermissionScopesPayload(name="p")
        )
        assert len(permissions) == 1

        authz_policy_provider = MagicMock()
        authz_policy_provider.create_policy_role_async = AsyncMock(
            return_value=make_response(status_code=201, text="", body=None)
        )
        authz_policy_provider.delete_policy_async = AsyncMock(
            return_value=make_response(status_code=204, text="", body=None)
        )
        authz_policy_provider.create_policy_async = AsyncMock(
            return_value=make_response(status_code=201, text="", body=None)
        )
        authz_policy_provider.get_policy_by_name_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body=[])
        )
        authz_policy_provider.get_associated_roles_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body=[])
        )
        authz_policy_provider.get_policy_authorisation_scopes_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body=[])
        )
        authz_policy_provider.get_policies_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body=[])
        )
        authz_policy_service = AuthzPolicyService(
            provider=authz_policy_provider, validator=validator
        )
        await authz_policy_service.create_policy_role_async(
            payload=RolePolicyPayload(name="rp")
        )
        await authz_policy_service.delete_policy_async("id")
        await authz_policy_service.create_policy_async(
            payload=PermissionPayload(name="p")
        )
        await authz_policy_service.get_policy_by_name_async(
            query=FilterFindPolicyParams(name="p")
        )
        await authz_policy_service.get_associated_roles_async("id")
        await authz_policy_service.get_policy_authorisation_scopes_async("id")
        await authz_policy_service.get_policies_async()

        wk_provider = MagicMock()
        wk_provider.get_certs_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body={})
        )
        wk_provider.get_openid_configuration_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body={})
        )
        wk_provider.get_uma2_configuration_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body={})
        )
        wk_provider.get_issuer_async = AsyncMock(
            return_value=make_response(status_code=200, text="ok", body={})
        )
        wk_service = WellKnownService(provider=wk_provider, validator=validator)
        await wk_service.get_certs_async()
        await wk_service.get_openid_configuration_async()
        await wk_service.get_uma2_configuration_async()
        await wk_service.get_issuer()
