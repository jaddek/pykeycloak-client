from http import HTTPStatus
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from ..core.exceptions import (
    KeycloakBadRequestError,
    KeycloakConflictError,
    KeycloakError,
    KeycloakException,
    KeycloakForbiddenError,
    KeycloakMethodNotAllowedError,
    KeycloakNotFoundError,
    KeycloakServerError,
    KeycloakUnauthorisedError,
    KeycloakUnprocessableEntityError,
)
from .exceptions import KeycloakUnsupportedMediaTypeError
from .protocols import KeycloakResponseProtocol, KeycloakResponseValidatorProtocol


class KeycloakResponseValidator:
    _EXCEPTION_MAP: dict[int, type[KeycloakError]] = {
        HTTPStatus.NOT_FOUND: KeycloakNotFoundError,
        HTTPStatus.CONFLICT: KeycloakConflictError,
        HTTPStatus.BAD_REQUEST: KeycloakBadRequestError,
        HTTPStatus.UNAUTHORIZED: KeycloakUnauthorisedError,
        HTTPStatus.FORBIDDEN: KeycloakForbiddenError,
        HTTPStatus.UNPROCESSABLE_ENTITY: KeycloakUnprocessableEntityError,
        HTTPStatus.METHOD_NOT_ALLOWED: KeycloakMethodNotAllowedError,
        HTTPStatus.UNSUPPORTED_MEDIA_TYPE: KeycloakUnsupportedMediaTypeError,
    }

    _SUCCESS_STATUSES = {HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.NO_CONTENT}

    def validate(self, response: KeycloakResponseProtocol) -> None:
        if response.status_code not in self._SUCCESS_STATUSES:
            raise self._create_error(response)

    def _create_error(self, response: KeycloakResponseProtocol) -> KeycloakException:
        status = response.status_code
        error = self._EXCEPTION_MAP.get(status, KeycloakServerError)

        error_detail = response.text or "No detail provided"
        endpoint = self._extract_endpoint(response)
        request_id = self._extract_request_id(response)
        realm = self._extract_realm(endpoint)
        retriable = self._is_retriable(status)
        return error(
            message=f"Keycloak {status}: {error_detail}",
            status_code=status,
            content=response.content,
            endpoint=endpoint,
            realm=realm,
            request_id=request_id,
            retriable=retriable,
        )

    @staticmethod
    def _extract_endpoint(response: KeycloakResponseProtocol) -> str | None:
        request = getattr(response, "request", None)
        if request is None:
            return None
        url = getattr(request, "url", None)
        if url is None:
            return None
        return str(url)

    @staticmethod
    def _extract_request_id(response: KeycloakResponseProtocol) -> str | None:
        if not response.headers:
            return None

        headers = {str(k).lower(): str(v) for k, v in dict(response.headers).items()}
        return (
            headers.get("traceparent")
            or headers.get("x-request-id")
            or headers.get("x-correlation-id")
            or headers.get("x-cloud-trace-context")
            or headers.get("request-id")
            or headers.get("x-ms-request-id")
            or headers.get("x-amzn-trace-id")
        )

    @staticmethod
    def _extract_realm(endpoint: str | None) -> str | None:
        if not endpoint:
            return None

        path = urlparse(endpoint).path
        parts = [part for part in path.split("/") if part]
        for index, part in enumerate(parts):
            if part == "realms" and index + 1 < len(parts):
                return parts[index + 1]
        return None

    @staticmethod
    def _is_retriable(status_code: int) -> bool:
        return (
            status_code
            in {
                HTTPStatus.REQUEST_TIMEOUT,
                HTTPStatus.TOO_MANY_REQUESTS,
                HTTPStatus.BAD_GATEWAY,
                HTTPStatus.SERVICE_UNAVAILABLE,
                HTTPStatus.GATEWAY_TIMEOUT,
            }
            or 500 <= status_code <= 599
        )


if TYPE_CHECKING:
    _: KeycloakResponseValidatorProtocol = type[KeycloakResponseValidator]
