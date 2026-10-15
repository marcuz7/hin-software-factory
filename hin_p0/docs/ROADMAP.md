# HIN software factory — Orca integration roadmap

## P0 (this draft PR)
- Independent local state machine, not a replacement for existing Orca services
- Task lifecycle and lease/heartbeat primitives
- Independent review-state gate
- PRD-to-four-artifact naming scaffold
- Unittest coverage and CLI demonstration

## P1 — Orca adapter (requires code audit)
- Identify Orca CLI interfaces and existing task/worktree contracts
- Integrate only through supported interfaces, avoiding a competing global scheduler
- Map projects, work packages, worker identities and worktrees to Orca records
- Build fail-closed authorization: repository/file scope, tool allowlists, budgets
- Restrict unattended execution to disposable or isolated environments
- Record actual test evidence and immutable run receipts
- Support interrupt/retry without duplicate commits or side effects

## P2 — Autonomous task DAG
- Concurrency-safe DB transactions and durable scheduler, terminal statuses
- Retry/backoff with bounded attempts, lease fencing tokens, multi-process correctness
- Worker pool registry, capability routing and quota awareness
- Approved PR generation and independent review
- Audit log, metrics, alerts and recovery tests

## P3 — HIN spec compiler
- Parse approved versioned PRDs with traceable requirement IDs
- Emit validated API contract, schema/migration, UI spec and executable task packages
- Detect conflicting authorities and request approval rather than silently deciding
- Add integration tests against Ithaca sample work package

## Acceptance gate
No automated merging, deployment, secret escalation or unsafe no-approval harness mode.
P0 code is a research prototype: it does not claim unattended execution.
