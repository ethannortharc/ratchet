---
name: getting-started
description: Bootstrap for Ratchet v6. Detects project state from DB, routes user intent, manages multi-session coordination. Python tools handle all state management.
---

# Ratchet — Session Bootstrap

You have the Ratchet plugin. Multi-agent collaboration platform with agile process management.

## First: Check Environment

```bash
python tools/ratchet.py version
```

If not found, the tools directory may need to be located. Check the plugin installation path.

## Session Startup

Every session starts by reading project state:

```bash
python tools/ratchet.py status
```

The output tells you the current state. Route accordingly:

| Status Output | Action |
|---------------|--------|
| "No project initialized" | User needs `/ratchet:story` or `python tools/ratchet.py init` |
| "Sprint N: executing (active in other session)" | Monitoring mode — user can query status, add backlog items, but NOT execute |
| "Sprint N: executing (STALE)" | Offer crash recovery: `python tools/ratchet.py sprint force-unlock` then resume |
| "Sprint N: done, Sprint N+1: pending" | Offer review (`/ratchet:review`) or start next sprint |
| "Backlog has N must items, no active sprint" | Offer sprint planning |
| "All sprints done, backlog empty" | Project idle. User can add new requirements anytime. |

## Intent Routing

When the user describes work:

- **New project/feature** → `/ratchet:story` (full or mini story process)
- **Bug report** → `python tools/ratchet.py backlog add --type=bug --priority=must "description"`
- **Small change** → `python tools/ratchet.py backlog add --type=feature "description"`
- **Check progress** → `python tools/ratchet.py status`
- **Review results** → `/ratchet:review`
- **Add to backlog** → `python tools/ratchet.py backlog add ...`
- **Manage backlog** → `python tools/ratchet.py backlog list/update`

**Never create a new project when user describes changes to an existing one.** Add to backlog instead.

## Dual-Track Model

```
Human Track (Story — continuous):     Agent Track (Sprint — autonomous):
  /ratchet:story                        Sprint Planning (Manager agent)
  Bug reports → backlog                 Spec generation (auto)
  Review → feedback → backlog           Execution (ratchet loop)
  Backlog refinement                    Verification + regression
                                        Acceptance review
  All through: ratchet.py backlog       All through: ratchet.py sprint/step/wp
```

Human track and agent track communicate through the backlog (in ratchet.db). They never block each other.

## Commands

| Command | Purpose |
|---------|---------|
| `/ratchet:story` | Start new work — perspective analysis → backlog |
| `/ratchet:spec` | Standalone spec (skip story) |
| `/ratchet:review` | Review sprint results |
| `/ratchet:coverage` | Coverage dashboard |
| `/ratchet:status` | Progress overview |
| `/ratchet:profile` | Personal preferences |
| `/ratchet:pause` | Pause sprint |
| `/ratchet:resume` | Resume sprint |

## Key Principles

1. **Python tools manage process.** State, gates, DB, ratchet decisions — all deterministic code. You focus on creative work.
2. **Story is continuous.** Not a one-time phase. Users can add to backlog anytime via story, bugs, or direct entry.
3. **Spec = Sprint.** Each spec executes one sprint's worth of backlog items.
4. **Nothing blocks execution.** Unresolvable items → new backlog entries, not execution blocks.
5. **Files are content, DB is state.** Read .md/.yaml files for content. Call Python tools for state queries.
6. **Sessions are disposable.** DB has all state. Any session can resume from any point.
7. **One sprint per session for execution.** Human interaction can be a separate concurrent session.
