"""Dockhand API client with session-based authentication."""

import httpx
from typing import Any


class DockhandClient:
    """HTTP client for the Dockhand REST API."""

    def __init__(self, base_url: str, username: str | None = None, password: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            follow_redirects=True,
        )
        self._authenticated = False

    async def _ensure_auth(self) -> None:
        """Authenticate with Dockhand if credentials are provided and not yet logged in."""
        if self._authenticated or not self.username:
            return
        resp = await self._client.post(
            "/api/auth/login",
            json={"username": self.username, "password": self.password},
        )
        resp.raise_for_status()
        self._authenticated = True

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        """Make an authenticated request and return JSON response."""
        await self._ensure_auth()
        resp = await self._client.request(method, path, **kwargs)
        resp.raise_for_status()
        if resp.status_code == 204:
            return {"status": "ok"}
        try:
            return resp.json()
        except Exception:
            return {"status": "ok", "text": resp.text}

    async def get(self, path: str, **kwargs: Any) -> Any:
        return await self._request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> Any:
        return await self._request("POST", path, **kwargs)

    async def delete(self, path: str, **kwargs: Any) -> Any:
        return await self._request("DELETE", path, **kwargs)

    async def close(self) -> None:
        await self._client.aclose()
