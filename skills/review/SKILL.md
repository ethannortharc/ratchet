---
name: review
description: Process blocked backlog items needing human decision. Shows items from DB sorted by priority, handles feedback conversion into backlog entries. Use when the user says "review", "what needs my attention", or after agent notifies of completed work.
---

# Review — Human Decision Queue

## Workflow

### Step 1: Show Blocked Items

Run: `python tools/ratchet.py backlog list --status=blocked`

Display items needing human decision, sorted by priority (blocking items first).

If no blocked items, report "No items need your attention."

### Step 2: Show Acceptance Review Summary

If a sprint has completed acceptance review, show summary:

Read `.ratchet/sprints/{sprint}/acceptance/summary.md`

```
Acceptance Review Summary:
  | Role | Rating | Key Gap |
  |------|--------|---------|
  | [role] | satisfied/concerns/unsatisfied | [gap or "-"] |

  - [N]/[total] Must requirements delivered
  - [N]/[total] role perspectives fully satisfied
  - [N] gaps found
  - PM verdict: [ready / ready with caveats / needs iteration]
```

### Step 3: Process Items

For each item the user reviews:

**Confirm unresolved item** — user makes a decision:
```
python tools/ratchet.py backlog update {id} --decision="..." --status=prioritized
```

**User gives feedback** — convert to new backlog item:
```
python tools/ratchet.py backlog add --type=improvement --source=user_report
```

**Pass**: Mark as resolved, note if this unblocks downstream work.

**Revise**: Ask for specific feedback, then run the Feedback Conversion Engine.

### Step 4: Feedback Conversion Engine

Every piece of human feedback is an opportunity to create actionable backlog items.

**Process:**
1. Match feedback against domain-specific patterns
2. Try to convert subjective feedback into concrete, verifiable backlog items
3. Show conversion to user: "You said '[feedback]'. I'll create this backlog item: '[objective version]'. Does this capture it?"
4. If confirmed: `python tools/ratchet.py backlog add --type=improvement --source=user_report`
5. If not captured well: refine and try again, or add as-is with notes

Not everything converts cleanly. Subjective items are still valid backlog entries — they just get human-track verification.

## Direct Feedback (outside /ratchet:review)

When a user reports an issue directly in conversation:

1. Run the feedback conversion engine immediately
2. Determine if this is a bug or improvement
3. For bugs: `python tools/ratchet.py backlog add --type=bug --source=user_report`
4. For improvements: `python tools/ratchet.py backlog add --type=improvement --source=user_report`
5. Items enter the backlog and get picked up in the next sprint

## Rules

1. **Always attempt feedback conversion.** Even partial conversion is valuable.
2. **Show conversion before applying.** Human must confirm the objective version captures their intent.
3. **High-priority items first.** They're blocking agent work.
4. **Don't overwhelm.** If >10 items, show top 5 and ask if user wants to see rest.
5. **Basic functionality bugs = agent failure.** Acknowledge this should have been caught, create a bug backlog item with high priority.
