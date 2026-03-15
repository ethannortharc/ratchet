---
name: getting-started
description: Bootstrap for Ratchet. Loaded at session start. Establishes intent-driven execution with dual-track verification and ratchet optimization loops.
---

# Ratchet — Session Bootstrap

You have the Ratchet plugin. It turns intent into verified results through autonomous iteration.

## Core Loop

```
User describes intent → Intent Spec generated (hybrid 3-step, ~5 min)
→ Test suite generated → Agent iterates autonomously (ratchet: keep improvements, discard failures)
→ Human reviews async when available → Feedback triggers next round
```

## Commands

- `/ratchet:spec` — Intent → structured Intent Spec (start here)
- `/ratchet:plan` — Intent Spec → work packages with test suite + dependencies
- `/ratchet:verify` — Run verification + ratchet optimization loop
- `/ratchet:review` — Process human review queue (cross-project)
- `/ratchet:status` — Multi-project dashboard
- `/ratchet:report` — Generate iteration/project report
- `/ratchet:profile` — Personal preferences (one-time setup)
- `/ratchet:metrics` — Interaction and automation statistics
- `/ratchet:update` — Update Intent Spec mid-project (triggers new iteration)

## Automatic Behavior

When the user describes something they want to build or create, suggest `/ratchet:spec` before jumping into execution. If `.ratchet/spec.yaml` exists in the current directory, reference it when executing tasks.

## Key Principles

1. **Hybrid 3-step.** Intent convergence (2-3 decisions) → Generate Intent Spec → Conversation review + patch.
2. **Test suite first.** Plan generates tests before implementation so the ratchet loop has real signals from iteration 1.
3. **Dual-track.** Agent-track constraints run continuously. Human-track queues async.
4. **Ratchet.** Every iteration either improves (keep) or doesn't (discard). Progress is monotonic.
5. **Be aggressive.** Request better tools to increase automation. Propose new constraints when you discover issues. Convert human feedback into agent-verifiable constraints.

## State Locations

- Plugin config: `~/.config/ratchet/` (profile, global state, review queue)
- Project state: `.ratchet/` in project directory (Intent Spec, plan, logs, artifacts)
- Read DESIGN.md for full architecture details.
