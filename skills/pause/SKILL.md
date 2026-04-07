---
name: pause
description: Pause sprint execution.
---

# Pause

Run: `python tools/ratchet.py sprint pause {sprint_id}`

This releases the sprint lock and sets status to paused.

All work-in-progress state is preserved. Resume with `/ratchet:resume`.
