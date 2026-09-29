import asyncio
import base64
import json
from urllib.request import Request, urlopen
from app.settings import settings

def _get_issue_sync(issue_key: str) -> dict:
    if not settings.jira_base_url or not settings.jira_email or not settings.atlassian_api_token:
        raise RuntimeError("Jira is not configured: JIRA_BASE_URL, JIRA_EMAIL, ATLASSIAN_API_TOKEN are required")
    raw = f"{settings.jira_email}:{settings.atlassian_api_token}".encode()
    req = Request(
        f"{settings.jira_base_url.rstrip('/')}/rest/api/3/issue/{issue_key}",
        headers={"Authorization": "Basic " + base64.b64encode(raw).decode(), "Accept": "application/json"},
    )
    with urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode())

async def get_issue(issue_key: str) -> dict:
    return await asyncio.to_thread(_get_issue_sync, issue_key)

def issue_context(issue: dict) -> str:
    fields = issue.get("fields", {})
    description = fields.get("description")
    if isinstance(description, dict):
        description = _adf_text(description)
    return (f"Jira issue: {issue.get('key')}\n"
            f"Summary: {fields.get('summary', '')}\n"
            f"Status: {(fields.get('status') or {}).get('name', '')}\n"
            f"Description:\n{description or '(empty)'}")

def _adf_text(node) -> str:
    if isinstance(node, dict):
        parts = [node.get("text", "")]
        parts.extend(_adf_text(x) for x in node.get("content", []))
        return " ".join(x for x in parts if x).strip()
    if isinstance(node, list): return " ".join(_adf_text(x) for x in node)
    return str(node or "")


def _post_comment_sync(issue_key: str, body: str):
    if not settings.jira_base_url or not settings.jira_email or not settings.atlassian_api_token:
        raise RuntimeError("Jira is not configured")
    raw = f"{settings.jira_email}:{settings.atlassian_api_token}".encode()
    payload = json.dumps({"body": {"version": 1, "type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": body[:30000]}]}]}}).encode()
    req = Request(f"{settings.jira_base_url.rstrip('/')}/rest/api/3/issue/{issue_key}/comment", data=payload, method="POST", headers={"Authorization": "Basic " + base64.b64encode(raw).decode(), "Accept": "application/json", "Content-Type": "application/json"})
    with urlopen(req, timeout=30) as response: return json.loads(response.read().decode())

async def add_comment(issue_key: str, body: str) -> dict:
    return await asyncio.to_thread(_post_comment_sync, issue_key, body)


def _search_issues_sync(jql: str):
    if not settings.jira_base_url or not settings.jira_email or not settings.atlassian_api_token:
        raise RuntimeError("Jira is not configured")
    raw = f"{settings.jira_email}:{settings.atlassian_api_token}".encode()
    payload = json.dumps({"jql": jql, "maxResults": 50, "fields": ["summary", "status", "description", "updated"]}).encode()
    req = Request(f"{settings.jira_base_url.rstrip('/')}/rest/api/3/search/jql", data=payload, method="POST", headers={"Authorization": "Basic " + base64.b64encode(raw).decode(), "Accept": "application/json", "Content-Type": "application/json"})
    with urlopen(req, timeout=30) as response: return json.loads(response.read().decode())

async def search_issues(jql: str) -> dict:
    return await asyncio.to_thread(_search_issues_sync, jql)
