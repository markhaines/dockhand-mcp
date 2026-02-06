# Dockhand MCP Server

An MCP (Model Context Protocol) server that provides tools for managing Docker containers, compose stacks, images, volumes, and networks through the [Dockhand](https://dockhand.pro/) REST API.

## Features

- **Containers** — list, create, start, stop, restart, remove, view logs
- **Compose Stacks** — list, create, start, stop, remove
- **Images** — list, pull, remove, vulnerability scan
- **Volumes** — list, create, remove
- **Networks** — list, create, remove
- **Monitoring** — activity log, dashboard stats, scheduled tasks, environments

## Installation

### With pip

```bash
pip install -e /path/to/dockhand-mcp
```

### With uv (recommended)

```bash
uv pip install -e /path/to/dockhand-mcp
```

## Configuration

Set these environment variables:

| Variable | Required | Description |
|---|---|---|
| `DOCKHAND_URL` | Yes | Dockhand instance URL (e.g. `http://192.168.1.100:3000`) |
| `DOCKHAND_USER` | If auth enabled | Login username |
| `DOCKHAND_PASS` | If auth enabled | Login password |

## Claude Desktop Setup

Add this to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "dockhand": {
      "command": "python",
      "args": ["-m", "dockhand_mcp.server"],
      "env": {
        "DOCKHAND_URL": "http://your-dockhand-host:3000",
        "DOCKHAND_USER": "your-username",
        "DOCKHAND_PASS": "your-password"
      }
    }
  }
}
```

Or if installed with uv:

```json
{
  "mcpServers": {
    "dockhand": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/dockhand-mcp", "dockhand-mcp"],
      "env": {
        "DOCKHAND_URL": "http://your-dockhand-host:3000",
        "DOCKHAND_USER": "your-username",
        "DOCKHAND_PASS": "your-password"
      }
    }
  }
}
```

## Available Tools

### Environments
- `list_environments` — List all Docker environments
- `get_dashboard_stats` — Get dashboard statistics

### Containers
- `list_containers` — List all containers
- `get_container` — Get container details
- `create_container` — Create a new container
- `start_container` — Start a container
- `stop_container` — Stop a container
- `restart_container` — Restart a container
- `remove_container` — Remove a container
- `get_container_logs` — View container logs

### Compose Stacks
- `list_stacks` — List compose stacks
- `create_stack` — Create a stack from YAML
- `start_stack` — Start/deploy a stack
- `stop_stack` — Stop a stack
- `remove_stack` — Remove a stack

### Images
- `list_images` — List all images
- `pull_image` — Pull from registry
- `remove_image` — Remove an image
- `scan_image` — Vulnerability scan

### Volumes & Networks
- `list_volumes` / `create_volume` / `remove_volume`
- `list_networks` / `create_network` / `remove_network`

### Activity & Schedules
- `get_activity_log` — Docker event log
- `list_schedules` — Scheduled tasks

All tools accept an optional `env` parameter to target a specific Docker environment.
