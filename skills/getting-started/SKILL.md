---
name: getting-started
description: Bootstrap for Ratchet. Loaded at session start. Establishes intent-driven execution with workspace management, lifecycle states, dual-track verification, and ratchet optimization loops.
---

# Ratchet — Session Bootstrap

You have the Ratchet plugin. It turns intent into verified results through autonomous iteration.

## Core Loop

```
User describes intent → Hybrid 3-step formalization (~5 min)
→ Workspace registered → Test suite auto-generated
→ Plan created → Agent iterates autonomously (ratchet: keep improvements, discard failures)
→ Human reviews async when available → Feedback triggers next round
```

## Commands

- `/ratchet:spec` — Intent → structured Intent Spec + test suite (start here)
- `/ratchet:plan` — Intent Spec → work packages with dependencies
- `/ratchet:verify` — Run verification + ratchet optimization loop
- `/ratchet:review` — Process human review queue (cross-intent)
- `/ratchet:status` — Multi-intent dashboard with lifecycle states
- `/ratchet:report` — Generate iteration/project report with proof of work
- `/ratchet:profile` — Personal preferences (one-time setup)
- `/ratchet:metrics` — Interaction and automation statistics
- `/ratchet:update` — Update Intent Spec mid-project (triggers new iteration)
- `/ratchet:pause` — Pause an intent's execution
- `/ratchet:resume` — Resume a paused intent

## Workspace Management

Each intent is registered with a unique ID and locked to an absolute workspace path. All operations stay within the workspace. The global registry at `~/.config/ratchet/state.yaml` tracks all intents.

```
/ratchet:status              → show all intents
/ratchet:status prism        → show prism details
/ratchet:verify prism        → verify prism (from any directory)
```

When no intent ID is given, Ratchet resolves by current directory → registry lookup → ask.

## Intent Lifecycle

```
draft → active → agent_running → agent_complete → human_review → done
                      ↑                │
                      └── ratchet ──────┘

any → paused (user pauses)
paused → active (user resumes)
any → archived (user archives)
```

## Automatic Behavior

When the user describes something they want to build or create, suggest `/ratchet:spec` before jumping into execution. If `.ratchet/spec.yaml` exists in the current directory, reference it when executing tasks.

## Key Principles

1. **Hybrid 3-step.** Intent convergence (2-3 decisions) → Generate Intent Spec → Conversation review + patch.
2. **Test suite first.** Auto-generated after spec approval. Tests exist before implementation starts.
3. **Dual-track.** Agent-track constraints run continuously. Human-track queues async.
4. **Ratchet.** Every iteration either improves (keep) or doesn't (discard). Progress is monotonic.
5. **Workspace isolation.** Each intent locked to a directory. Agent never wanders outside.
6. **Proof of work.** Reports include raw verification outputs, not just pass/fail counts.
7. **Be aggressive.** Request better tools to increase automation. Propose new constraints when you discover issues. Convert human feedback into agent-verifiable constraints.

## State Locations

- Plugin config: `~/.config/ratchet/` (profile, intent registry, review queue)
- Project state: `.ratchet/` in workspace directory (Intent Spec, test suite, plan, logs, artifacts)
- Read DESIGN.md for full architecture details.
