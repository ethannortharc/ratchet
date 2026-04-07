---
name: execute
description: Orchestrate the ratchet execution loop using Python tools for all process management. Spawns wp-executor and verifier subagents for creative work. Python tools handle state, gates, ratchet decisions, regression, and agent tracking.
---

# Execute — Ratchet Loop Orchestration (v6)

## Prerequisites

Before starting, verify gates:

```bash
python tools/ratchet.py gate check {sprint_id} planning
```

Must pass before execution begins.

## Execution Protocol

**Critical: Follow this recipe exactly. Python tools handle consistency.**

### Sprint Setup

```bash
python tools/ratchet.py step start {sprint_id} execution
python tools/ratchet.py sprint lock {sprint_id}
```

### Per-WP Ratchet Cycle

For each WP in dependency order from plan.yaml:

```bash
# 1. Start WP
python tools/ratchet.py wp start {sprint_id} {wp_id}
```

For each iteration (up to budget):

```bash
# 2. Register executor agent
python tools/ratchet.py agent register {sprint_id} wp_executor "WP-{id} Executor" --model sonnet
```

Spawn wp-executor subagent:
```
Agent(subagent_type="general-purpose", model="sonnet",
      prompt="[executor prompt with WP definition, spec, test files, iteration feedback]")
```

```bash
# 3. Register verifier agent
python tools/ratchet.py agent register {sprint_id} verifier "WP-{id} Verifier" --model sonnet
```

Spawn verifier subagent:
```
Agent(subagent_type="general-purpose", model="sonnet",
      prompt="[verifier prompt with WP acceptance criteria]")
```

```bash
# 4. Ratchet decision (DETERMINISTIC — Python decides, not you)
python tools/ratchet.py ratchet decide {sprint_id} {wp_id} --score={composite_score}
# Exit 0 = KEEP → git commit
# Exit 1 = DISCARD → git reset
```

```bash
# 5. Regression test (MANDATORY — Python triggers, not you)
python tools/ratchet.py regression run {sprint_id}
# If regression fails → git reset, ratchet discard
```

```bash
# 6. Update WP
python tools/ratchet.py wp update {sprint_id} {wp_id} --iteration={N} --score={score}
```

If all constraints pass:
```bash
python tools/ratchet.py wp update {sprint_id} {wp_id} --status=done
```

If agent encounters unresolvable item:
```bash
# Don't stop! Create backlog item and continue.
python tools/ratchet.py backlog add "description" --type=unresolved --source=execution --sprint={sprint_id} --wp={wp_id}
```

### After All WPs Complete

```bash
python tools/ratchet.py step complete {sprint_id} execution
python tools/ratchet.py gate check {sprint_id} execution
```

### Regression

```bash
python tools/ratchet.py step start {sprint_id} regression
python tools/ratchet.py regression run
python tools/ratchet.py regression register {sprint_id}
python tools/ratchet.py gate check {sprint_id} regression
python tools/ratchet.py step complete {sprint_id} regression
```

### Acceptance Review

```bash
python tools/ratchet.py step start {sprint_id} acceptance
```

Spawn parallel acceptance agents (one per active role from roles.yaml).
Each reviews actual output against their original perspective document.
Gaps → `python tools/ratchet.py backlog add --type=improvement --source=acceptance_review`

Spawn PM acceptance summary agent (Opus).

```bash
python tools/ratchet.py gate check {sprint_id} acceptance
python tools/ratchet.py step complete {sprint_id} acceptance
```

### Finalize

```bash
python tools/ratchet.py step start {sprint_id} finalize
python tools/ratchet.py gate check {sprint_id} finalize
# Merge to main
python tools/ratchet.py sprint unlock {sprint_id}
python tools/ratchet.py step complete {sprint_id} finalize
```

Update sprint status:
```bash
python tools/ratchet.py sprint update {sprint_id} --status=done
```

Notify user: "Sprint {id} complete. /ratchet:review to see results."

Check for next sprint:
```bash
python tools/ratchet.py backlog list --status=new --priority=must
```

If must items exist → suggest next sprint. If not → notify user.

## Stuck Detection

Track in-memory during execution (same as before):
- Repeated failure (3x same error) → change strategy hint
- Score oscillation (variance < 0.01 over 3 iterations) → different approach hint

## Git Strategy

Same as before: single `ratchet/execute` branch, commit on keep, reset on discard, tag checkpoints.

## Rules

1. **Always use Python tools for state.** Never update state files directly.
2. **Gate check before every step transition.** `python tools/ratchet.py gate check` must pass.
3. **Ratchet decision by Python.** Don't judge scores yourself — let the tool compare.
4. **Regression after every WP.** Non-negotiable. Python triggers it.
5. **Unresolvable → backlog.** Never block execution. Create backlog item and continue.
6. **Lock sprint.** Acquire lock at start, release at end or on crash recovery.
7. **Heartbeat during long execution.** `python tools/ratchet.py sprint heartbeat {sprint_id}` periodically.
