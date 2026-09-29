---
name: cockpit-code-review
description: Review smart cockpit code changes for correctness, safety, resource handling, concurrency, and maintainability.
---

# Cockpit Code Review

Review the issue and relevant code before making changes. Focus on:

- lifecycle and resource cleanup
- concurrency, thread safety, and callback reentrancy
- error propagation and degraded behavior
- memory ownership and leaks in C/C++
- API compatibility and regression risk
- logging and privacy of vehicle/user data

Return structured findings with severity P0/P1/P2/P3, file, line, evidence, and a concrete fix.
Do not modify production or main branches. Do not claim a test passed unless it actually ran.


## 输出语言和证据

所有输出使用简体中文。每个问题必须包含文件、行号、代码证据、影响和建议。没有足够证据时标记“待确认”，不要把推测写成事实。

只读评审时 `changed_files` 必须为空；没有实际运行的测试不得写入已执行测试。
