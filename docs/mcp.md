# MCP Server

This repo includes `mcp_server.py`, which exposes dynamic access to PyKeycloak services via MCP tools.

## Smoke check

```bash
make mcp-smoke
```

## Run

```bash
uv run python mcp_server.py
```

## Runtime env vars

- `MCP_TRANSPORT`: `stdio` (default), `sse`, or `streamable-http`
- `MCP_HOST`: default `127.0.0.1`
- `MCP_PORT`: default `8000`
- `KEYCLOAK_BASE_URL`: your Keycloak base URL

## Codex config example

```toml
[mcp_servers.pykeycloak]
command = "uv"
args = ["run", "python", "mcp_server.py"]
cwd = "/Users/tonynazarov/Development/Work/PyKeycloak"

[mcp_servers.pykeycloak.env]
MCP_TRANSPORT = "stdio"
MCP_HOST = "127.0.0.1"
MCP_PORT = "8000"
KEYCLOAK_BASE_URL = "http://127.0.0.1:8080"
```

## Core MCP tools

- `health`
- `keycloak_register`
- `keycloak_register_from_env`
- `keycloak_list_keys`
- `keycloak_list_methods`
- `keycloak_call`
- `keycloak_close_all`
