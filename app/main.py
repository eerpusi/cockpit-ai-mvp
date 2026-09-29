import asyncio, subprocess, sys
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.settings import settings
from app.storage.runs import create_run, get_run
from app.mcp.registry import public_status
from app.workflows.code_review import execute

_gateway_process = None

@asynccontextmanager
async def lifespan(app):
    global _gateway_process
    # The Gateway is a real external MCP process, started for local development.
    _gateway_process = subprocess.Popen([sys.executable, "-m", "app.mcp.gateway"], cwd=str(settings.workspace))
    for _ in range(30):
        try:
            reader, writer = await asyncio.open_connection("127.0.0.1", 8090)
            writer.close(); await writer.wait_closed()
            break
        except OSError:
            await asyncio.sleep(0.2)
    yield
    if _gateway_process and _gateway_process.poll() is None:
        _gateway_process.terminate()
        try: _gateway_process.wait(timeout=5)
        except subprocess.TimeoutExpired: _gateway_process.kill()

app = FastAPI(title="Cockpit AI MVP", version="0.3.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

class ReviewRequest(BaseModel):
    issue_id: str
    prompt: str
    resume_session_id: str | None = None

@app.get("/", include_in_schema=False)
def index(): return FileResponse(Path(__file__).parent / "web/index.html")
@app.get("/health")
def health(): return {"status": "ok", "workspace": str(settings.workspace), "mcp": public_status()}
@app.post("/workflow/code-review", status_code=202)
async def start_review(request: ReviewRequest):
    run_id = create_run(request.issue_id, request.prompt, request.resume_session_id)
    asyncio.create_task(execute(run_id, request.issue_id, request.prompt, request.resume_session_id))
    return {"run_id": run_id, "status": "queued"}
@app.get("/workflow/runs/{run_id}")
def read_run(run_id: str):
    run = get_run(run_id)
    if not run: raise HTTPException(status_code=404, detail="run not found")
    return run

def run():
    import uvicorn; uvicorn.run("app.main:app", host="127.0.0.1", port=8080, reload=False)
