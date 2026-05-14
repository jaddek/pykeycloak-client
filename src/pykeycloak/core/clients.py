# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Anton "Tony" Nazarov <tonynazarov+dev@gmail.com>
import asyncio
import os
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from http import HTTPStatus
from types import TracebackType
from typing import Any, Self, cast

from httpx import (
    AsyncClient,
    RequestError,
)

from .. import logger
from .constants import (
    KEYCLOAK_HTTP_RETRY_BASE_DELAY_SECONDS_DEFAULT,
    KEYCLOAK_HTTP_RETRY_ENABLED_DEFAULT,
    KEYCLOAK_HTTP_RETRY_JITTER_SECONDS_DEFAULT,
    KEYCLOAK_HTTP_RETRY_MAX_ATTEMPTS_DEFAULT,
    KEYCLOAK_HTTP_RETRY_MAX_DELAY_SECONDS_DEFAULT,
)
from .helpers import getenv_bool, getenv_float, getenv_int, getenv_optional
from .protocols import KeycloakResponseProtocol


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class KeycloakHttpClientSync: ...


@dataclass(frozen=True, slots=True)
class ClientDiagnostics:
    timeout: Any
    base_url: str
    default_headers: Any
    max_connections: int | str | None = None
    max_keepalive_connections: int | str | None = None
    keepalive_expiry: float | str | None = None


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    enabled: bool = KEYCLOAK_HTTP_RETRY_ENABLED_DEFAULT
    max_attempts: int = KEYCLOAK_HTTP_RETRY_MAX_ATTEMPTS_DEFAULT
    base_delay_seconds: float = KEYCLOAK_HTTP_RETRY_BASE_DELAY_SECONDS_DEFAULT
    max_delay_seconds: float = KEYCLOAK_HTTP_RETRY_MAX_DELAY_SECONDS_DEFAULT
    jitter_seconds: float = KEYCLOAK_HTTP_RETRY_JITTER_SECONDS_DEFAULT
    retry_status_codes: frozenset[int] = frozenset(
        {
            HTTPStatus.REQUEST_TIMEOUT,
            HTTPStatus.TOO_MANY_REQUESTS,
            HTTPStatus.INTERNAL_SERVER_ERROR,
            HTTPStatus.BAD_GATEWAY,
            HTTPStatus.SERVICE_UNAVAILABLE,
            HTTPStatus.GATEWAY_TIMEOUT,
        }
    )
    retry_methods: frozenset[str] = frozenset({"GET", "HEAD", "OPTIONS", "DELETE"})

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        if self.base_delay_seconds < 0:
            raise ValueError("base_delay_seconds must be >= 0")
        if self.max_delay_seconds < 0:
            raise ValueError("max_delay_seconds must be >= 0")
        if self.jitter_seconds < 0:
            raise ValueError("jitter_seconds must be >= 0")

    @classmethod
    def with_env(cls) -> "RetryPolicy":
        methods = getenv_optional("KEYCLOAK_HTTP_RETRY_METHODS")
        parsed_methods = (
            frozenset(m.strip().upper() for m in methods.split(",") if m and m.strip())
            if methods
            else frozenset({"GET", "HEAD", "OPTIONS", "DELETE"})
        )
        return cls(
            enabled=getenv_bool(
                "KEYCLOAK_HTTP_RETRY_ENABLED", KEYCLOAK_HTTP_RETRY_ENABLED_DEFAULT
            ),
            max_attempts=getenv_int(
                "KEYCLOAK_HTTP_RETRY_MAX_ATTEMPTS",
                KEYCLOAK_HTTP_RETRY_MAX_ATTEMPTS_DEFAULT,
            ),
            base_delay_seconds=getenv_float(
                "KEYCLOAK_HTTP_RETRY_BASE_DELAY_SECONDS",
                KEYCLOAK_HTTP_RETRY_BASE_DELAY_SECONDS_DEFAULT,
            ),
            max_delay_seconds=getenv_float(
                "KEYCLOAK_HTTP_RETRY_MAX_DELAY_SECONDS",
                KEYCLOAK_HTTP_RETRY_MAX_DELAY_SECONDS_DEFAULT,
            ),
            jitter_seconds=getenv_float(
                "KEYCLOAK_HTTP_RETRY_JITTER_SECONDS",
                KEYCLOAK_HTTP_RETRY_JITTER_SECONDS_DEFAULT,
            ),
            retry_methods=parsed_methods,
        )


class KeycloakHttpClientAsync:
    def __init__(
        self,
        client: AsyncClient,
        retry_policy: RetryPolicy | None = None,
        diagnostics_provider: Callable[[], ClientDiagnostics] | None = None,
    ):
        self._client = client
        self._retry_policy = retry_policy or RetryPolicy.with_env()
        self._diagnostics_provider = diagnostics_provider

    @property
    def client(self) -> AsyncClient:
        return self._client

    @staticmethod
    def init_default_client(
        client: AsyncClient,
        retry_policy: RetryPolicy | None = None,
        diagnostics_provider: Callable[[], ClientDiagnostics] | None = None,
    ) -> "KeycloakHttpClientAsync":
        return KeycloakHttpClientAsync(
            client=client,
            retry_policy=retry_policy,
            diagnostics_provider=diagnostics_provider,
        )

    def _should_retry_method(self, method: HttpMethod) -> bool:
        return method.value in self._retry_policy.retry_methods

    def _should_retry_status(
        self, method: HttpMethod, status_code: int, attempt: int
    ) -> bool:
        if not self._retry_policy.enabled:
            return False
        if not self._should_retry_method(method):
            return False
        if attempt >= self._retry_policy.max_attempts:
            return False
        return status_code in self._retry_policy.retry_status_codes

    def _should_retry_exception(self, method: HttpMethod, attempt: int) -> bool:
        if not self._retry_policy.enabled:
            return False
        if not self._should_retry_method(method):
            return False
        return attempt < self._retry_policy.max_attempts

    def _compute_retry_delay(self, attempt: int) -> float:
        backoff: float = float(self._retry_policy.base_delay_seconds) * float(
            2 ** (attempt - 1)
        )
        jitter: float = 0.0
        if self._retry_policy.jitter_seconds > 0:
            random_bytes = os.urandom(2)
            random_int = int.from_bytes(random_bytes, "big")
            random_part: float = random_int / 65535.0
            jitter = random_part * self._retry_policy.jitter_seconds
        return float(min(float(self._retry_policy.max_delay_seconds), backoff + jitter))

    def log_client_config_before_request(self) -> None:
        diagnostics = (
            self._diagnostics_provider()
            if self._diagnostics_provider is not None
            else ClientDiagnostics(
                timeout=self.client.timeout,
                base_url=str(self.client.base_url),
                default_headers=self.client.headers,
                max_connections="N/A",
                max_keepalive_connections="N/A",
                keepalive_expiry="N/A",
            )
        )

        logger.debug(
            "HTTPX\n=========================================\n"
            " HTTPX Client Configuration:\n"
            " timeouts=%s, max_connections=%s, max_keepalive=%s, keepalive_expiry=%s,\n"
            " base_url=%s, default_headers=%s\n"
            "=========================================",
            diagnostics.timeout,
            diagnostics.max_connections,
            diagnostics.max_keepalive_connections,
            diagnostics.keepalive_expiry,
            diagnostics.base_url,
            diagnostics.default_headers,
        )

    def build_full_url(self, path: str, query: str) -> str:
        return f"{self.client.base_url}{path}?{query}"

    async def request_async(
        self, method: HttpMethod, url: str, raise_exception: bool = False, **kwargs: Any
    ) -> KeycloakResponseProtocol:
        logger.debug(
            "Request method: %s, url: %s", method, url, extra={"content": kwargs}
        )

        self.log_client_config_before_request()

        attempt = 1
        while True:
            try:
                response = await self.client.request(
                    method=method.value, url=url, **kwargs
                )
            except RequestError:
                if not self._should_retry_exception(method=method, attempt=attempt):
                    raise
                delay = self._compute_retry_delay(attempt)
                logger.warning(
                    "Retrying failed request (%s %s), attempt %s/%s in %.3fs",
                    method.value,
                    url,
                    attempt + 1,
                    self._retry_policy.max_attempts,
                    delay,
                )
                await asyncio.sleep(delay)
                attempt += 1
                continue

            if self._should_retry_status(
                method=method, status_code=response.status_code, attempt=attempt
            ):
                delay = self._compute_retry_delay(attempt)
                logger.warning(
                    "Retrying response status %s for (%s %s), attempt %s/%s in %.3fs",
                    response.status_code,
                    method.value,
                    url,
                    attempt + 1,
                    self._retry_policy.max_attempts,
                    delay,
                )
                await asyncio.sleep(delay)
                attempt += 1
                continue

            if raise_exception:
                response.raise_for_status()

            return cast(KeycloakResponseProtocol, response)

    async def __aenter__(self) -> Self:
        await self._client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: TracebackType | None = None,
    ) -> None:
        await self._client.__aexit__(exc_type, exc_value, traceback)

    async def close_async(self) -> None:
        await self._client.aclose()
