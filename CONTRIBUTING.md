# Contributing

Thank you for contributing to `pykeycloak-client`.

## Development setup

The project supports Python 3.12 through 3.14 and uses UV for dependency management.

```bash
cp .env.example .env.local
make install
```

Keep real Keycloak credentials in ignored local environment files. Do not commit `.env`, `.env.local`, or client secrets.

## Local workflow

Run the complete deterministic verification suite before opening a pull request:

```bash
make verify
make pre-commit
```

The test suite enforces a minimum 89% coverage threshold for the packaged `pykeycloak_client` source. Live Keycloak integration tests remain skipped unless their integration environment is configured.

Useful focused commands:

```bash
make test-unit
make mcp-smoke
make lint
make format-check
make typecheck
make audit
make build
```

Integration tests require a reachable Keycloak instance and the documented integration environment variables. They are skipped when integration testing is not enabled.

## MCP development

The MCP server is an optional package feature. Install the development environment with `make install`, or install the published extra with:

```bash
uv add "pykeycloak-client[mcp]"
```

Run the packaged server with:

```bash
uv run pykeycloak-mcp
```

Use `make mcp-smoke` to validate package import, registration, service discovery, and the MCP entry point without requiring a live Keycloak server.

## Pull requests

- Keep changes focused and explain behavior changes in the pull request description.
- Add or update tests for changed behavior.
- Update documentation and `CHANGELOG.md` when user-visible behavior changes.
- Do not include credentials, tokens, generated build artifacts, or local environment files.
- Ensure `make verify` and `make pre-commit` pass.

## Releases

Releases are tag-driven. Maintainers create a semantic-version tag in the form `vX.Y.Z`; CI synchronizes the package version, builds the artifacts, audits dependencies, publishes to PyPI, and creates the GitHub Release.
