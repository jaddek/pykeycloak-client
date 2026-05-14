# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Anton "Tony" Nazarov <tonynazarov+dev@gmail.com>


class KeycloakException(Exception):
    def __init__(
        self,
        message: str = "",
    ) -> None:
        self.message = message

    def __str__(self) -> str:
        return f"{self.message}"


class AccessTokenIsRequiredError(KeycloakException): ...


class KeycloakDecodingError(KeycloakException): ...


class KeycloakUnexpectedBehaviourException(KeycloakException):
    def __init__(
        self,
        message: str = "",
        description: str = "",
        affected_versions: list[str] | None = None,
    ) -> None:
        self.message = message
        self.description = description
        self.versions = affected_versions

    def __str__(self) -> str:
        return f"v:[{self.versions}]{self.message}: {self.description}"


class KeycloakHTTPException(KeycloakException):
    def __init__(
        self,
        message: str = "",
        status_code: int | None = None,
        content: bytes | None = None,
        endpoint: str | None = None,
        realm: str | None = None,
        request_id: str | None = None,
        retriable: bool = False,
    ) -> None:
        Exception.__init__(self, message)

        self.status_code = status_code
        self.content = content
        self.message = message
        self.endpoint = endpoint
        self.realm = realm
        self.request_id = request_id
        self.retriable = retriable

    def __str__(self) -> str:
        prefix = f"{self.status_code}: " if self.status_code is not None else ""
        details = []
        if self.endpoint:
            details.append(f"endpoint={self.endpoint}")
        if self.realm:
            details.append(f"realm={self.realm}")
        if self.request_id:
            details.append(f"request_id={self.request_id}")
        details.append(f"retriable={self.retriable}")

        details_suffix = f" ({', '.join(details)})" if details else ""
        return f"{prefix}{self.message}{details_suffix}"


class KeycloakError(KeycloakHTTPException): ...


class KeycloakConflictError(KeycloakError): ...


class KeycloakNotFoundError(KeycloakError): ...


class KeycloakBadRequestError(KeycloakError): ...


class KeycloakUnprocessableEntityError(KeycloakError): ...


class KeycloakUnsupportedMediaTypeError(KeycloakError): ...


class KeycloakUnauthorisedError(KeycloakError): ...


class KeycloakForbiddenError(KeycloakError): ...


class KeycloakMethodNotAllowedError(KeycloakError): ...


class KeycloakServerError(KeycloakError): ...
