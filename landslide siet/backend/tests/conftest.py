import asyncio

import httpx
import pytest

from backend.main import app


@pytest.fixture
def api_request():
    def request(method: str, path: str, **kwargs):
        async def send():
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app),
                base_url="http://testserver",
            ) as client:
                return await client.request(method, path, **kwargs)

        return asyncio.run(send())

    return request