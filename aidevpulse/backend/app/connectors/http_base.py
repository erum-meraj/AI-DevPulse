import asyncio
import time
from collections import defaultdict
from typing import Any
from urllib.parse import urlparse

import httpx
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.connectors.base import Connector
from app.core.constants import (
    HTTP_MIN_REQUEST_INTERVAL_SECONDS,
    HTTP_RETRY_ATTEMPTS,
    HTTP_RETRY_BACKOFF_MAX_SECONDS,
    HTTP_RETRY_BACKOFF_MIN_SECONDS,
    HTTP_TIMEOUT_SECONDS,
    HTTP_USER_AGENT,
)


class HTTPConnector(Connector):
    """Shared HTTP behavior for API and RSS connectors."""

    _host_locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
    _host_last_request_at: dict[str, float] = {}

    def __init__(self, client: httpx.AsyncClient | None = None):
        self._client = client
        self._owns_client = client is None

    async def close(self) -> None:
        if self._client is not None and self._owns_client:
            await self._client.aclose()
            self._client = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=HTTP_TIMEOUT_SECONDS,
                follow_redirects=True,
                headers={"User-Agent": HTTP_USER_AGENT},
            )
            self._owns_client = True
        return self._client

    async def _get_json(self, url: str) -> Any:
        response = await self._request("GET", url)
        return response.json()

    async def _get_text(self, url: str) -> str:
        response = await self._request("GET", url)
        return response.text

    async def _request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(HTTP_RETRY_ATTEMPTS),
            wait=wait_exponential(
                min=HTTP_RETRY_BACKOFF_MIN_SECONDS,
                max=HTTP_RETRY_BACKOFF_MAX_SECONDS,
            ),
            retry=retry_if_exception_type(httpx.HTTPError),
            reraise=True,
        ):
            with attempt:
                client = await self._get_client()
                await self._respect_rate_limit(url)
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                return response

        raise RuntimeError("Retry loop exited unexpectedly")

    async def _respect_rate_limit(self, url: str) -> None:
        host = urlparse(url).netloc
        lock = self._host_locks[host]
        async with lock:
            now = time.monotonic()
            last_request_at = self._host_last_request_at.get(host)
            if last_request_at is not None:
                elapsed = now - last_request_at
                if elapsed < HTTP_MIN_REQUEST_INTERVAL_SECONDS:
                    await asyncio.sleep(HTTP_MIN_REQUEST_INTERVAL_SECONDS - elapsed)
            self._host_last_request_at[host] = time.monotonic()
