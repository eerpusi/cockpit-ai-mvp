import asyncio, json
from mcp.server.mcpserver import MCPServer
from app.settings import settings
from app.integrations.jira import get_issue, issue_context, add_comment
from app.integrations.github import get_context, get_recent_runs, dispatch_ci

server = MCPServer(name="cockpit-engineering", version="0.1.0", instructions="真实研发系统 MCP Gateway：Jira、GitHub 和 CI。")

@server.tool(name="jira_get_issue", description="读取真实 Jira Issue 的标题、描述和状态。")
async def jira_get_issue(issue_key: str) -> str:
    return issue_context(await get_issue(issue_key))

@server.tool(name="jira_add_comment", description="向真实 Jira Issue 写入评论。")
async def jira_add_comment(issue_key: str, comment: str) -> str:
    result = await add_comment(issue_key, comment)
    return json.dumps({"ok": True, "issue_key": issue_key, "comment_id": result.get("id")}, ensure_ascii=False)

@server.tool(name="github_get_repository_context", description="读取真实 GitHub 仓库元信息和文件树。")
async def github_get_repository_context() -> str:
    return json.dumps(await get_context(), ensure_ascii=False)

@server.tool(name="ci_get_recent_runs", description="读取真实 GitHub Actions 最近运行记录。")
async def ci_get_recent_runs() -> str:
    return json.dumps(await get_recent_runs(), ensure_ascii=False)

@server.tool(name="ci_dispatch", description="触发真实 GitHub Actions CI。")
async def ci_dispatch() -> str:
    await dispatch_ci()
    return json.dumps({"ok": True, "repository": settings.github_repo, "workflow": settings.github_workflow}, ensure_ascii=False)

async def main():
    await server.run_sse_async(host="127.0.0.1", port=8090, sse_path="/sse", message_path="/messages/")

if __name__ == "__main__":
    asyncio.run(main())
