"""Dockhand MCP Server — Docker management via the Dockhand REST API."""

import json
import os
import asyncio
from typing import Any

from mcp.server.fastmcp import FastMCP

from .client import DockhandClient

# ---------------------------------------------------------------------------
# Configuration from environment
# ---------------------------------------------------------------------------
DOCKHAND_URL = os.environ.get("DOCKHAND_URL", "http://localhost:3000")
DOCKHAND_USER = os.environ.get("DOCKHAND_USER", "")
DOCKHAND_PASS = os.environ.get("DOCKHAND_PASS", "")

# ---------------------------------------------------------------------------
# MCP server & shared client
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "dockhand",
    instructions="Manage Docker containers, stacks, images, volumes, and networks via Dockhand",
)

_client: DockhandClient | None = None


def _get_client() -> DockhandClient:
    global _client
    if _client is None:
        _client = DockhandClient(DOCKHAND_URL, DOCKHAND_USER, DOCKHAND_PASS)
    return _client


def _env_header(env: str | None) -> dict[str, Any]:
    """Build headers dict with optional env ID."""
    return {"headers": {"X-Environment-Id": env}} if env else {}


def _env_params(env: str | None) -> dict[str, Any]:
    """Build query params dict with optional env filter."""
    return {"params": {"env": env}} if env else {}


def _parse_port_bindings(ports: list[str] | None) -> dict[str, list[dict[str, str]]] | None:
    """Convert port strings like '8080:80' to Docker PortBinding format.
    
    Docker expects: {"80/tcp": [{"HostPort": "8080"}]}
    """
    if not ports:
        return None
    
    bindings = {}
    for port_str in ports:
        if ":" not in port_str:
            continue
        host_port, container_port = port_str.split(":", 1)
        # Assume TCP if no protocol specified
        if "/" not in container_port:
            container_port = f"{container_port}/tcp"
        bindings[container_port] = [{"HostPort": host_port}]
    return bindings


def _fmt(data: Any) -> str:
    """Format response data as readable JSON."""
    return json.dumps(data, indent=2, default=str)


# ===================================================================
# ENVIRONMENTS
# ===================================================================

@mcp.tool()
async def list_environments() -> str:
    """List all configured Docker environments in Dockhand."""
    data = await _get_client().get("/api/environments")
    return _fmt(data)


@mcp.tool()
async def get_dashboard_stats(env: str | None = None) -> str:
    """Get dashboard statistics, optionally filtered by environment.

    Args:
        env: Environment name to filter by (optional)
    """
    data = await _get_client().get("/api/dashboard/stats", **_env_params(env))
    return _fmt(data)


# ===================================================================
# CONTAINERS
# ===================================================================

@mcp.tool()
async def list_containers(env: str | None = None) -> str:
    """List all Docker containers.

    Args:
        env: Environment name to filter by (optional)
    """
    data = await _get_client().get("/api/containers", **_env_params(env))
    return _fmt(data)


@mcp.tool()
async def get_container(container_id: str, env: str | None = None) -> str:
    """Get detailed information about a specific container.

    Args:
        container_id: The container ID or name
        env: Environment name (optional)
    """
    data = await _get_client().get(f"/api/containers/{container_id}", **_env_params(env))
    return _fmt(data)


@mcp.tool()
async def create_container(
    name: str,
    image: str,
    env: str | None = None,
    ports: list[str] | None = None,
    volumes: list[str] | None = None,
    environment: dict[str, str] | None = None,
    restart_policy: str = "unless-stopped",
) -> str:
    """Create a new Docker container.

    Args:
        name: Container name
        image: Docker image (e.g. "nginx:latest")
        env: Target environment (optional)
        ports: Port mappings (e.g. ["8080:80", "443:443"])
        volumes: Volume mounts (e.g. ["/host/path:/container/path"])
        environment: Environment variables as key-value pairs
        restart_policy: Restart policy (no, always, unless-stopped, on-failure)
    """
    body: dict[str, Any] = {
        "name": name,
        "image": image,
        "restartPolicy": restart_policy  # camelCase!
    }
    if ports:
        body["portBindings"] = _parse_port_bindings(ports)  # camelCase!
    if volumes:
        body["binds"] = volumes  # camelCase! Uses Docker Binds format
    if environment:
        body["environment"] = environment
    
    data = await _get_client().post("/api/containers", json=body, **_env_params(env))
    return _fmt(data)


@mcp.tool()
async def start_container(container_id: str, env: str | None = None) -> str:
    """Start a stopped container.

    Args:
        container_id: The container ID or name
        env: Environment name (optional)
    """
    data = await _get_client().post(f"/api/containers/{container_id}/start", **_env_params(env))
    return _fmt(data)


@mcp.tool()
async def stop_container(container_id: str, env: str | None = None) -> str:
    """Stop a running container.

    Args:
        container_id: The container ID or name
        env: Environment name (optional)
    """
    data = await _get_client().post(f"/api/containers/{container_id}/stop", **_env_params(env))
    return _fmt(data)


@mcp.tool()
async def restart_container(container_id: str, env: str | None = None) -> str:
    """Restart a container.

    Args:
        container_id: The container ID or name
        env: Environment name (optional)
    """
    data = await _get_client().post(f"/api/containers/{container_id}/restart", **_env_params(env))
    return _fmt(data)


@mcp.tool()
async def remove_container(container_id: str, env: str | None = None) -> str:
    """Remove/delete a container.

    Args:
        container_id: The container ID or name
        env: Environment name (optional)
    """
    data = await _get_client().delete(f"/api/containers/{container_id}", **_env_params(env))
    return _fmt(data)


@mcp.tool()
async def get_container_logs(container_id: str, env: str | None = None, tail: int = 100) -> str:
    """Get logs from a container.

    Args:
        container_id: The container ID or name
        env: Environment name (optional)
        tail: Number of log lines to retrieve (default 100)
    """
    params: dict[str, Any] = {"tail": tail}
    if env:
        params["env"] = env
    data = await _get_client().get(f"/api/containers/{container_id}/logs", params=params)
    return _fmt(data)


# ===================================================================
# COMPOSE STACKS
# ===================================================================

@mcp.tool()
async def list_stacks(env: str | None = None) -> str:
    """List all Docker Compose stacks.

    Args:
        env: Environment name to filter by (optional)
    """
    data = await _get_client().get("/api/stacks", **_env_params(env))
    return _fmt(data)


@mcp.tool()
async def create_stack(name: str, compose: str, env: str | None = None) -> str:
    """Create a new Docker Compose stack.

    Args:
        name: Stack name
        compose: Docker Compose YAML content as a string
        env: Target environment (optional)
    """
    data = await _get_client().post(
        "/api/stacks",
        json={"name": name, "compose": compose},
        **_env_params(env),
    )
    return _fmt(data)


@mcp.tool()
async def start_stack(stack_name: str, env: str | None = None) -> str:
    """Start/deploy a compose stack.

    Args:
        stack_name: The stack name
        env: Environment name (optional)
    """
    data = await _get_client().post(f"/api/stacks/{stack_name}/start", **_env_params(env))
    return _fmt(data)


@mcp.tool()
async def stop_stack(stack_name: str, env: str | None = None) -> str:
    """Stop a running compose stack.

    Args:
        stack_name: The stack name
        env: Environment name (optional)
    """
    data = await _get_client().post(f"/api/stacks/{stack_name}/stop", **_env_params(env))
    return _fmt(data)


@mcp.tool()
async def remove_stack(stack_name: str, env: str | None = None) -> str:
    """Remove/delete a compose stack.

    Args:
        stack_name: The stack name
        env: Environment name (optional)
    """
    data = await _get_client().delete(f"/api/stacks/{stack_name}", **_env_params(env))
    return _fmt(data)


# ===================================================================
# IMAGES
# ===================================================================

@mcp.tool()
async def list_images(env: str | None = None) -> str:
    """List all Docker images.

    Args:
        env: Environment name to filter by (optional)
    """
    data = await _get_client().get("/api/images", **_env_params(env))
    return _fmt(data)


@mcp.tool()
async def pull_image(image: str, env: str | None = None) -> str:
    """Pull a Docker image from a registry.

    Args:
        image: Image name and tag (e.g. "nginx:latest")
        env: Target environment (optional)
    """
    body: dict[str, Any] = {"image": image}
    data = await _get_client().post("/api/images/pull", json=body, **_env_params(env))
    return _fmt(data)


@mcp.tool()
async def remove_image(image_id: str, env: str | None = None) -> str:
    """Remove a Docker image.

    Args:
        image_id: The image ID or name:tag
        env: Environment name (optional)
    """
    data = await _get_client().delete(f"/api/images/{image_id}", **_env_params(env))
    return _fmt(data)


@mcp.tool()
async def scan_image(image: str, env: str | None = None) -> str:
    """Scan a Docker image for vulnerabilities.

    Args:
        image: Image name and tag to scan
        env: Environment name (optional)
    """
    data = await _get_client().post("/api/images/scan", json={"image": image}, **_env_params(env))
    return _fmt(data)


# ===================================================================
# VOLUMES
# ===================================================================

@mcp.tool()
async def list_volumes(env: str | None = None) -> str:
    """List all Docker volumes.

    Args:
        env: Environment name to filter by (optional)
    """
    data = await _get_client().get("/api/volumes", **_env_params(env))
    return _fmt(data)


@mcp.tool()
async def create_volume(name: str, driver: str = "local", env: str | None = None) -> str:
    """Create a new Docker volume.

    Args:
        name: Volume name
        driver: Volume driver (default: "local")
        env: Target environment (optional)
    """
    data = await _get_client().post(
        "/api/volumes",
        json={"name": name, "driver": driver},
        **_env_params(env),
    )
    return _fmt(data)


@mcp.tool()
async def remove_volume(volume_name: str, env: str | None = None) -> str:
    """Remove a Docker volume.

    Args:
        volume_name: The volume name
        env: Environment name (optional)
    """
    data = await _get_client().delete(f"/api/volumes/{volume_name}", **_env_params(env))
    return _fmt(data)


# ===================================================================
# NETWORKS
# ===================================================================

@mcp.tool()
async def list_networks(env: str | None = None) -> str:
    """List all Docker networks.

    Args:
        env: Environment name to filter by (optional)
    """
    data = await _get_client().get("/api/networks", **_env_params(env))
    return _fmt(data)


@mcp.tool()
async def create_network(name: str, driver: str = "bridge", env: str | None = None) -> str:
    """Create a new Docker network.

    Args:
        name: Network name
        driver: Network driver (bridge, overlay, host, macvlan)
        env: Target environment (optional)
    """
    data = await _get_client().post(
        "/api/networks",
        json={"name": name, "driver": driver},
        **_env_params(env),
    )
    return _fmt(data)


@mcp.tool()
async def remove_network(network_id: str, env: str | None = None) -> str:
    """Remove a Docker network.

    Args:
        network_id: The network ID or name
        env: Environment name (optional)
    """
    data = await _get_client().delete(f"/api/networks/{network_id}", **_env_params(env))
    return _fmt(data)


# ===================================================================
# ACTIVITY & SCHEDULES
# ===================================================================

@mcp.tool()
async def get_activity_log(env: str | None = None) -> str:
    """Get the activity log of Docker events.

    Args:
        env: Environment name to filter by (optional)
    """
    data = await _get_client().get("/api/activity", **_env_params(env))
    return _fmt(data)


@mcp.tool()
async def list_schedules() -> str:
    """List all scheduled tasks (auto-updates, syncs, etc.)."""
    data = await _get_client().get("/api/schedules")
    return _fmt(data)


# ===================================================================
# ENTRY POINT
# ===================================================================

def main():
    """Run the Dockhand MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
