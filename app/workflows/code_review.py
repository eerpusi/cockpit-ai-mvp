from dataclasses import asdict, is_dataclass
from app.agents.runtime import run_code_review
from app.integrations.jira import get_issue, issue_context, add_comment
from app.integrations.github import get_context, get_recent_runs
from app.storage.runs import append_event, finish_run, update_run

def serialize(value):
    if is_dataclass(value): return asdict(value)
    if hasattr(value, "model_dump"): return value.model_dump()
    if hasattr(value, "__dict__"): return value.__dict__
    return {"value": str(value)}

async def execute(run_id: str, issue_id: str, prompt: str, resume: str | None = None):
    try:
        update_run(run_id, status="running")
        jira_context = ""
        github_context = ""
        try:
            jira_context = issue_context(await get_issue(issue_id))
            update_run(run_id, jira_issue_loaded=True)
        except Exception as jira_error:
            update_run(run_id, jira_issue_loaded=False, jira_error=str(jira_error))
        try:
            gh = await get_context()
            github_context = "GitHub repository: " + str(gh)
            update_run(run_id, github_loaded=True)
        except Exception as github_error:
            update_run(run_id, github_loaded=False, github_error=str(github_error))
        enriched_prompt = f"{jira_context}\n\n{github_context}\n\nUser instructions:\n{prompt}"
        async for message in run_code_review(issue_id, enriched_prompt, resume):
            event = serialize(message)
            append_event(run_id, event)
            if event.get("session_id"): update_run(run_id, session_id=event["session_id"])
            if event.get("structured_output") is not None:
                update_run(run_id, result=event["structured_output"])
            elif event.get("result") is not None:
                update_run(run_id, result=event["result"])
        current = __import__("app.storage.runs", fromlist=["get_run"]).get_run(run_id)
        final_status = "failed" if current and current.get("error") else "completed"
        if final_status == "completed" and current and current.get("result"):
            result = current["result"]
            comment = "AI 代码评审结果（开发环境）\n\n" + str(result.get("summary", result))
            try:
                await add_comment(issue_id, comment)
                update_run(run_id, jira_comment_written=True)
            except Exception as comment_error:
                update_run(run_id, jira_comment_written=False, jira_comment_error=str(comment_error))
        finish_run(run_id, final_status)
    except Exception as exc:
        finish_run(run_id, "failed", error=f"{type(exc).__name__}: {exc}")
