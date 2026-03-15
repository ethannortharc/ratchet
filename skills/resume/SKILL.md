---
name: resume
description: Resume a paused intent's execution. Sets status back to "active" so agent can continue. Use when user says "resume", "continue", "unpause", "start again".
---

# Resume — Resume Paused Intent

## Usage

```
/ratchet:resume prism
/ratchet:resume          # resolves by current workspace
```

## Workflow

1. Resolve intent ID (argument → workspace → ask)
2. Read `~/.config/ratchet/state.yaml`
3. Verify intent is in `paused` state
4. Set intent status to `active`
5. Update `last_activity` timestamp
6. Show brief status: "▶ Resumed intent '[name]'. Current state: [progress summary]"
7. Suggest next action based on where it left off

## Rules
- Can only resume from `paused` state
- If intent is not paused, inform user of current state and suggest appropriate action
