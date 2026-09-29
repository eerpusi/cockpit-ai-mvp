from claude_agent_sdk import ClaudeAgentOptions, query
from app.mcp.registry import configured_servers
from app.settings import settings

async def run_code_review(issue_id: str, prompt: str, resume: str | None = None):
    options = ClaudeAgentOptions(
        cwd=settings.workspace,
        model=settings.model,
        resume=resume,
        skills=["cockpit-code-review", "cockpit-test-generation"],
        plugins=settings.plugins,
        mcp_servers=configured_servers(),
        allowed_tools=["Read", "Glob", "Grep", "Bash", "mcp__engineering__*"],
        permission_mode="default",
        max_turns=settings.max_turns,
        max_budget_usd=settings.max_budget_usd,
        output_format={"type": "json_schema", "schema": {
            "type": "object", "properties": {
                "summary": {"type": "string"}, "findings": {"type": "array"},
                "recommended_tests": {"type": "array"}, "executed_tests": {"type": "array"},
                "changed_files": {"type": "array"}},
            "required": ["summary", "findings", "recommended_tests", "executed_tests", "changed_files"]}},
    )
    instruction = ("你是智能座舱研发代码评审 Agent。所有面向用户的总结、问题描述、修复建议和测试说明必须使用简体中文。"
                   "只有真实执行过的测试才能放入 executed_tests；没有执行的只能放入 recommended_tests。"
                   "只有实际修改过的文件才能放入 changed_files，本次只读评审通常应为空。"
                   "每个问题必须给出文件、行号和代码证据；不确定的判断标记为待确认。\n\n")
    async for message in query(prompt=f"{instruction}Jira 任务：{issue_id}\n\n{prompt}", options=options):
        yield message
