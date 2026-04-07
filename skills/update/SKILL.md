---
name: update
description: "Process modifications to an existing project. Changes flow to the backlog for the next sprint. Story-level changes run affected perspectives first; small changes and bugs go directly to backlog."
---

# Update — Living Backlog Model

## Usage

Invoked when user describes changes to an existing project:

```
/ratchet:update "add markdown export feature"
/ratchet:update "fix the encoding error on results page"
```

## Change Classification

### Story-Level Change (needs perspectives)
User describes something that changes the product experience:
- "Add growth advice to the results page"
- "Support dark mode"
- "Let users share via WeChat"

**Process:**
1. Run affected perspectives (mini-story) to understand impact
2. PM re-synthesizes requirements from updated perspectives
3. New requirements become backlog items:
   ```
   python tools/ratchet.py backlog add --type=feature --source=user_request
   ```
4. Items get picked up in the next sprint

### Small Change (direct backlog entry)
User describes a contained improvement:
- "Tighten test coverage to 90%"
- "Search must complete in < 200ms"

**Process:**
```
python tools/ratchet.py backlog add --type=improvement --source=user_request
```

### Bug Report
User describes a specific bug:
- "Fix the encoding error on the results page"
- "The share button doesn't work"

**Process:**
```
python tools/ratchet.py backlog add --type=bug --source=user_report
```

## Converting Subjective Feedback

When the user's update is subjective ("search feels slow", "code is messy"), try to convert:

```
User: "search feels slow"
-> Backlog item: "Search completes in < 200ms for 1000 notes"
   type: improvement, verifier: auto
```

Always show the conversion and ask if it captures what they meant.

## Rules

1. **Changes go to backlog.** No immediate cascade — the next sprint picks them up.
2. **Story-level changes need perspectives.** Run affected perspectives to understand the full impact before creating backlog items.
3. **Show what will be added.** Before creating backlog items, show the user what you plan to add.
4. **Bugs get high priority.** Bug reports are prioritized in the backlog.
5. **Don't regenerate from scratch.** Incrementally update story artifacts if needed, then create targeted backlog items.
