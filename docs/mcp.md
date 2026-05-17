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
cwd = "path/to/PyKeycloak"

[mcp_servers.pykeycloak.env]
MCP_TRANSPORT = "stdio"
MCP_HOST = "127.0.0.1"
MCP_PORT = "8000"
KEYCLOAK_BASE_URL = "http://127.0.0.1:8080"
```

Set `cwd` to your local repository path.

## Core MCP tools

- `health`
- `keycloak_register`
- `keycloak_register_from_env`
- `keycloak_list_keys`
- `keycloak_list_methods`
- `keycloak_call`
- `keycloak_close_all`

## Examples for 5 AI agents

1. Codex (`~/.codex/config.toml`)

```toml
[mcp_servers.pykeycloak]
command = "uv"
args = ["run", "python", "mcp_server.py"]
cwd = "path/to/PyKeycloak"

[mcp_servers.pykeycloak.env]
MCP_TRANSPORT = "stdio"
KEYCLOAK_BASE_URL = "http://127.0.0.1:8080"
```

2. Claude Desktop (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "pykeycloak": {
      "command": "uv",
      "args": ["run", "python", "mcp_server.py"],
      "cwd": "path/to/PyKeycloak",
      "env": {
        "MCP_TRANSPORT": "stdio",
        "KEYCLOAK_BASE_URL": "http://127.0.0.1:8080"
      }
    }
  }
}
```

3. Cursor (MCP JSON config)

```json
{
  "mcpServers": {
    "pykeycloak": {
      "command": "uv",
      "args": ["run", "python", "mcp_server.py"],
      "cwd": "path/to/PyKeycloak",
      "env": {
        "MCP_TRANSPORT": "stdio",
        "KEYCLOAK_BASE_URL": "http://127.0.0.1:8080"
      }
    }
  }
}
```

4. Cline (MCP JSON config)

```json
{
  "mcpServers": {
    "pykeycloak": {
      "command": "uv",
      "args": ["run", "python", "mcp_server.py"],
      "cwd": "path/to/PyKeycloak",
      "env": {
        "MCP_TRANSPORT": "stdio",
        "KEYCLOAK_BASE_URL": "http://127.0.0.1:8080"
      }
    }
  }
}
```

5. Continue (MCP JSON config)

```json
{
  "mcpServers": {
    "pykeycloak": {
      "command": "uv",
      "args": ["run", "python", "mcp_server.py"],
      "cwd": "path/to/PyKeycloak",
      "env": {
        "MCP_TRANSPORT": "stdio",
        "KEYCLOAK_BASE_URL": "http://127.0.0.1:8080"
      }
    }
  }
}
```

After connecting any agent, test with:

1. `health`
2. `keycloak_register_from_env` (or `keycloak_register`)
3. `keycloak_list_methods`
4. `keycloak_call`
