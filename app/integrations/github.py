import asyncio, base64, json
from urllib.request import Request, urlopen
from app.settings import settings

API = "https://api.github.com"
def _request(method, path, body=None):
    if not settings.github_token: raise RuntimeError("GitHub token is not configured")
    req=Request(API+path, method=method, headers={"Authorization":f"Bearer {settings.github_token}","Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","Content-Type":"application/json"}, data=json.dumps(body).encode() if body is not None else None)
    with urlopen(req, timeout=30) as r: return json.loads(r.read().decode()) if r.status != 204 else {}

def _context_sync():
    repo=settings.github_repo
    meta=_request("GET",f"/repos/{repo}")
    tree=_request("GET",f"/repos/{repo}/git/trees/{settings.github_default_branch}?recursive=1")
    paths=[x["path"] for x in tree.get("tree",[]) if x.get("type")=="blob"][:120]
    return {"repo":meta.get("full_name"),"default_branch":settings.github_default_branch,"visibility":meta.get("visibility"),"files":paths}
async def get_context(): return await asyncio.to_thread(_context_sync)

def _runs_sync(): return _request("GET",f"/repos/{settings.github_repo}/actions/runs?per_page=5")
async def get_recent_runs(): return await asyncio.to_thread(_runs_sync)

def _dispatch_sync(): return _request("POST",f"/repos/{settings.github_repo}/actions/workflows/{settings.github_workflow.split('/')[-1]}/dispatches",{"ref":settings.github_default_branch})
async def dispatch_ci(): return await asyncio.to_thread(_dispatch_sync)
