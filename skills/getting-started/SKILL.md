---
name: getting-started
description: Bootstrap for Ratchet. Loaded at session start. Establishes intent-driven execution with dual-track verification and ratchet optimization loops.
---

# Ratchet — Session Bootstrap

You have the Ratchet plugin. It turns intent into verified results through autonomous iteration.

## Core Loop

```
User describes intent → Spec generated (user confirms in ~3 min)
→ Agent iterates autonomously (ratchet: keep improvements, discard failures)
→ Human reviews async when available → Feedback triggers next round
```

## Commands

- `/ratchet:spec` — Intent → structured spec (start here)
- `/ratchet:plan` — Spec → work packages with dependencies
- `/ratchet:verify` — Run verification + ratchet optimization loop
- `/ratchet:review` — Process human review queue (cross-project)
- `/ratchet:status` — Multi-project dashboard
- `/ratchet:report` — Generate iteration/project report
- `/ratchet:profile` — Personal preferences (one-time setup)
- `/ratchet:metrics` — Interaction and automation statistics
- `/ratchet:update` — Update spec mid-project (triggers new iteration)

## Automatic Behavior

When the user describes something they want to build or create, suggest `/ratchet:spec` before jumping into execution. If `.ratchet/spec.yaml` exists in the current directory, reference it when executing tasks.

## Key Principles

1. **Generate first, ask later.** Produce a complete spec draft, ask only about low-confidence areas.
2. **Dual-track.** Agent-track constraints run continuously. Human-track queues async.
3. **Ratchet.** Every iteration either improves (keep) or doesn't (discard). Progress is monotonic.
4. **Be aggressive.** Request better tools to increase automation. Propose new constraints when you discover issues. Convert human feedback into agent-verifiable constraints.

## State Locations

- Plugin config: `~/.config/ratchet/` (profile, global state, review queue)
- Project state: `.ratchet/` in project directory (spec, plan, logs, artifacts)
- Read DESIGN.md for full architecture details.
