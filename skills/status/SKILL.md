---
name: status
description: Show project status from DB. Thin wrapper around Python tools.
---

# Status

Run: `python tools/ratchet.py status`

Display the output to the user.

For JSON format: `python tools/ratchet.py status --json`

For sprint detail: `python tools/ratchet.py sprint status {sprint_id}`

For agent activity: `python tools/ratchet.py events --sprint={sprint_id} --limit=20`

For active agents: `python tools/ratchet.py agent list --status=running`
