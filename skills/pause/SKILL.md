---
name: pause
description: Pause an intent's execution. Sets status to "paused" in global state. Agent stops executing work packages for this intent. Use when user says "pause", "stop working on", "hold off on".
---

# Pause — Pause Intent Execution

## Usage

```
/ratchet:pause prism
/ratchet:pause           # resolves by current workspace
```

## Workflow

1. Resolve intent ID (argument → workspace → ask)
2. Read `~/.config/ratchet/state.yaml`
3. Set intent status to `paused`
4. Update `last_activity` timestamp
5. Confirm: "⏸ Paused intent '[name]'. Use `/ratchet:resume [id]` to continue."

## Rules
- Can pause from any state except `done` and `archived`
- If the intent has running work packages, note that progress will stop
- Does not discard any work — current best state is preserved
