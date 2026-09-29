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
