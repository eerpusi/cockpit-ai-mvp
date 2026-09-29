import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from app.settings import settings

def _path(run_id: str) -> Path:
    return Path(settings.run_store_path) / f"{run_id}.json"

def _now() -> str: return datetime.now(timezone.utc).isoformat()

def create_run(issue_id: str, prompt: str, session_id: str | None = None) -> str:
    run_id = str(uuid4()); Path(settings.run_store_path).mkdir(parents=True, exist_ok=True)
    _path(run_id).write_text(json.dumps({"id": run_id, "issue_id": issue_id, "prompt": prompt,
        "status": "queued", "session_id": session_id, "created_at": _now(), "messages": []},
        ensure_ascii=False, indent=2), encoding="utf-8")
    return run_id

def get_run(run_id: str) -> dict | None:
    file = _path(run_id)
    return json.loads(file.read_text(encoding="utf-8")) if file.exists() else None

def update_run(run_id: str, **fields):
    data = get_run(run_id)
    if not data: return
    data.update(fields); _path(run_id).write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

def append_event(run_id: str, event: dict):
    data = get_run(run_id)
    if not data: return
    data["messages"].append({"at": _now(), **event})
    _path(run_id).write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

def finish_run(run_id: str, status: str, **fields):
    update_run(run_id, status=status, finished_at=_now(), **fields)
