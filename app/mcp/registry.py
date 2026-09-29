from app.settings import settings

def _remote_server(url: str | None, token: str | None, transport: str):
    if not url:
        return None
    if transport not in {"http", "sse"}:
        raise ValueError(f"Unsupported MCP transport: {transport}; use http or sse")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return {"type": transport, "url": url, "headers": headers}

def configured_servers() -> dict:
    servers = {"engineering": {"type": "sse", "url": settings.mcp_gateway_url.replace("/mcp", "/sse"), "headers": {}}}
    for name, url, token, transport in [
        ("git", settings.git_mcp_url, settings.git_mcp_auth_token, settings.git_mcp_transport),
        ("jira", settings.jira_mcp_url, settings.jira_mcp_auth_token, settings.jira_mcp_transport),
        ("ci", settings.ci_mcp_url, settings.ci_mcp_auth_token, settings.ci_mcp_transport),
    ]:
        server = _remote_server(url, token, transport)
        if server:
            servers[name] = server
    return servers

def public_status() -> list[dict]:
    return [{"name": name, "transport": config["type"], "url": config["url"], "configured": True}
            for name, config in configured_servers().items()]
