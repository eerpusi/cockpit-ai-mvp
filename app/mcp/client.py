import json
from contextlib import asynccontextmanager
from mcp import ClientSession
from mcp.client.sse import sse_client
from app.settings import settings

@asynccontextmanager
async def session():
    async with sse_client(settings.mcp_gateway_url.replace("/mcp", "/sse")) as (read, write):
        async with ClientSession(read, write) as client:
            await client.initialize()
            yield client

async def call(name: str, arguments: dict):
    async with session() as client:
        result = await client.call_tool(name, arguments)
        parts = getattr(result, "content", [])
        return "\n".join(getattr(p, "text", str(p)) for p in parts)
