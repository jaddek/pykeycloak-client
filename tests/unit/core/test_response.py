# SPDX-License-Identifier: MIT
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from httpx import Headers

from pykeycloak_client.core.exceptions import KeycloakDecodingError
from pykeycloak_client.core.response import KeycloakResponse, KeycloakResponseBuilder


class TestKeycloakResponse:
    def test_status_and_ok(self):
        response = KeycloakResponse(
            status_code=200,
            headers=Headers({"X-Test": "1"}),
            body={"a": 1},
            text="{}",
            content=b"{}",
        )
        assert response.status == HTTPStatus.OK
        assert response.ok is True

    def test_header_getitem_get(self):
        response = KeycloakResponse(
            status_code=404,
            headers=Headers({"X-Test": "1"}),
            body={"a": 1},
            text="{}",
            content=b"{}",
        )
        assert response.header("X-Test") == "1"
        assert response["a"] == 1
        assert response.get("a") == 1
        assert response.get("missing", "d") == "d"

    def test_getitem_raises_for_non_mapping_body(self):
        response = KeycloakResponse(
            status_code=200,
            headers=Headers(),
            body=["a"],
            text="[]",
            content=b"[]",
        )
        with pytest.raises(TypeError, match="body is not a mapping"):
            _ = response["a"]


class TestKeycloakResponseBuilder:
    def test_build_response_parses_json(self):
        raw = MagicMock()
        raw.status_code = 200
        raw.text = '{"ok": true}'
        raw.content = b'{"ok": true}'
        raw.headers = Headers({})
        raw.json.return_value = {"ok": True}

        result = KeycloakResponseBuilder().build_response(raw)
        assert result.body == {"ok": True}

    def test_build_response_raises_decoding_error_on_bad_json(self):
        raw = MagicMock()
        raw.status_code = 200
        raw.text = "not-json"
        raw.content = b"not-json"
        raw.headers = Headers({})
        raw.json.side_effect = ValueError("bad json")

        with pytest.raises(KeycloakDecodingError, match="Malformed JSON"):
            KeycloakResponseBuilder().build_response(raw)
