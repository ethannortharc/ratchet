---
name: metrics
description: Display project metrics from DB queries. Sprint progress, backlog stats, agent activity, and regression status.
---

# Metrics — DB-Driven Dashboard

All metrics come from the Python tools querying the SQLite database.

## Commands

Sprint metrics: `python tools/ratchet.py sprint status {sprint_id}`

Backlog stats: `python tools/ratchet.py backlog stats`

Agent activity: `python tools/ratchet.py events`

Regression status: `python tools/ratchet.py regression status`

Overall status: `python tools/ratchet.py status`

## Display

```
Metrics:
  Sprint: [sprint_id] | Status: [status]
  WPs: [N] total | [N] done | [N] running | [N] pending

  Backlog: [N] total | [N] bugs | [N] improvements | [N] features
  Blocked: [N] | Prioritized: [N] | Completed: [N]

  Regression: [N] tests | [N] passing | [N] failing

  Recent Events: [last N events with timestamps]
```

## Rules

1. All data comes from DB via Python tools — no separate metrics files.
2. Show the most relevant metrics first based on current project state.
3. For cross-sprint trends, query events across multiple sprints.
