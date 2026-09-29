<<<<<<< HEAD
# Cockpit AI MVP（开发环境真实链路）

这是一个可直接启动的开发环境 vertical slice，不包含 Mock 工具层：

- Claude Agent SDK 执行真实 Agent
- `.claude/skills/` 加载真实 Skill
- `PLUGIN_PATHS` 加载本地 Plugin
- Git / Jira / CI 通过真实 HTTP 或 SSE MCP 接入
- Session、工具消息、结构化结果落到 `.data/runs/`
- 内置最小 Web 页面和 REST API

## 运行环境

需要 Python 3.11+。Claude Agent SDK 会启动其 bundled Claude Code CLI，因此还需要可用的 Anthropic/Claude Code 凭据。

```bash
cp .env.example .env
# 必填：MVP_WORKSPACE、ANTHROPIC_API_KEY
# 按实际开发环境填写 GIT/JIRA/CI MCP 地址和 token
python3.11 -m pip install -e .
uvicorn app.main:app --reload --port 8080
```

浏览器打开 http://127.0.0.1:8080/ 即可发起真实评审。

## API

```bash
curl http://127.0.0.1:8080/health
curl -X POST http://127.0.0.1:8080/workflow/code-review \
  -H 'content-type: application/json' \
  -d '{"issue_id":"COCKPIT-101","prompt":"请读取该需求和相关代码，完成代码评审并生成测试建议。"}'
curl http://127.0.0.1:8080/workflow/runs/<run_id>
```

## MCP transport

每个 MCP 服务可以通过环境变量选择：

```bash
GIT_MCP_TRANSPORT=http
# 或 GIT_MCP_TRANSPORT=sse
```

MCP 工具名由真实服务发现，不在业务代码里伪造固定返回值。若某服务未配置，Agent 不会假装它存在；执行结果会记录失败原因。

## 当前闭环

```text
真实 Issue / Prompt
  → Claude Agent SDK
  → Code Review + Test Generation Skills
  → Git/Jira/CI MCP
  → 结构化评审结果
  → 可回放的 Run 记录
```
=======
# cockpit-ai-mvp
Private
>>>>>>> origin/main
