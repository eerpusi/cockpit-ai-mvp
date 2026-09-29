from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    mvp_workspace: str
    anthropic_api_key: str | None = None
    model: str | None = None
    max_turns: int = 20
    max_budget_usd: float | None = None
    git_mcp_url: str | None = None
    git_mcp_transport: str = "http"
    git_mcp_auth_token: str | None = None
    jira_base_url: str | None = None
    jira_project_key: str = "COCKPIT"
    jira_email: str | None = None
    atlassian_api_token: str | None = None
    github_token: str | None = None
    github_repo: str = "eerpusi/cockpit-ai-mvp"
    github_default_branch: str = "main"
    github_workflow: str = ".github/workflows/ci.yml"
    mcp_gateway_url: str = "http://127.0.0.1:8090/mcp"
    jira_mcp_url: str | None = None
    jira_mcp_transport: str = "http"
    jira_mcp_auth_token: str | None = None
    ci_mcp_url: str | None = None
    ci_mcp_transport: str = "http"
    ci_mcp_auth_token: str | None = None
    plugin_paths: str = ""
    run_store_path: str = ".data/runs"

    @property
    def workspace(self) -> Path:
        return Path(self.mvp_workspace).expanduser().resolve()

    @property
    def plugins(self) -> list[dict]:
        return [{"type": "local", "path": p.strip()} for p in self.plugin_paths.split(",") if p.strip()]

settings = Settings()

# Ensure the bundled Claude Code subprocess inherits the DeepSeek-compatible endpoint.
if os.getenv("DEEPSEEK_API_KEY") and not os.getenv("ANTHROPIC_AUTH_TOKEN"):
    os.environ["ANTHROPIC_AUTH_TOKEN"] = os.environ["DEEPSEEK_API_KEY"]
if os.getenv("DEEPSEEK_BASE_URL") and not os.getenv("ANTHROPIC_BASE_URL"):
    os.environ["ANTHROPIC_BASE_URL"] = os.environ["DEEPSEEK_BASE_URL"].rstrip("/") + "/anthropic"
if os.getenv("DEEPSEEK_MODEL") and not os.getenv("ANTHROPIC_MODEL"):
    os.environ["ANTHROPIC_MODEL"] = "claude-sonnet-4-5"
