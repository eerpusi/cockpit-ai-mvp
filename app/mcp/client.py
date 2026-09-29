import asyncio, json
from urllib.request import Request, urlopen
from app.settings import settings

async def _post(payload: dict) -> dict:
    def send():
        req = Request(settings.mcp_gateway_url, data=json.dumps(payload).encode(), method="POST", headers={"Content-Type":"application/json", "Accept":"application/json, text/event-stream"})
        with urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode())
    return await asyncio.to_thread(send)

async def call(name: str, arguments: dict):
    await _post({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"cockpit-mvp","version":"0.3.0"}}})
    result = await _post({"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":name,"arguments":arguments}})
    if "error" in result:
        raise RuntimeError(result["error"].get("message", str(result["error"])))
    content = result.get("result", {}).get("content", [])
    return "\n".join(item.get("text", str(item)) for item in content)
