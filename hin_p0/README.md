# HIN Software Factory — P0 sandbox prototype

HIN = **Hyper Intelligence Network**. This package is a small, additive prototype in the Orca fork. It does **not** replace Orca's scheduling/UI/CLI implementation, modify its runtime, bypass agent permissions, spawn coding agents, or access Ithaca.

## Scope
- SQLite-backed tasks and dependency-aware READY queue
- Atomic worker claim, lease and heartbeat
- Evidence submission and independent reviewer gate
- Source-linked specification *scaffold*, not a fully implemented compiler

## Quickstart
From the repository root (Python 3.11+):

```bash
python -m unittest discover -s hin_p0/tests -v
python -m hin_p0.cli --db /tmp/hin-p0.db demo
python -m hin_p0.cli --db /tmp/hin-p0.db list
```

## Boundaries
- Orca remains HIN's **single control plane**. Do not start Ruflo/Herdr schedulers alongside it.
- A work package is authorized for unattended work only within an isolated worktree and explicitly allowed commands/files. Underlying harness permission prompts still apply.
- Publishing, merging, deployments, deleting shared data, granting secrets and exceeding budgets require approval.
- This P0 never launches workers; integrate via a reviewed Orca adapter in P1.
- Proof of concept only; not production hardened, not a substitute for CI, secrets isolation or per-project authorization.

See [implementation roadmap](docs/ROADMAP.md).
