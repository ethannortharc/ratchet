---
name: review
description: Process the human-track review queue across all projects. Shows pending items sorted by priority (blocking items first). Handles feedback and converts subjective input into agent-verifiable constraints when possible. Use when the user says "review", "what needs my attention", "any pending items", or after agent notifies of completed work.
---

# Review — Human-Track Async Queue

## Workflow

### Step 1: Load Queue
Read `~/.config/ratchet/review_queue.yaml`. If empty, report "No pending reviews."

### Step 2: Show Queue (sorted by priority)

```
📋 Review Queue ([N] items)

🔴 [high] project-name / WP description
   ← Agent blocked: downstream WPs waiting on this
   Constraint: [claim]
   📎 [artifact path or inline preview]

⚪ [normal] project-name / WP description
   Constraint: [claim]
   📎 [artifact path]

💡 Agent Suggestions ([N] items)
   1. [project]: [proposed constraint] — [rationale]
```

### Step 3: Process Reviews

For each item the user reviews:

**Pass**: Mark constraint as verified, remove from queue. If this unblocks downstream WPs, note it.

**Revise**: Ask for specific feedback. Then:
1. Try to convert feedback into an agent-verifiable constraint
2. Show the conversion: "You said '[subjective feedback]'. I'll add this constraint: '[objective version]'. Does this capture it?"
3. If confirmed: add to spec, increment version, trigger new iteration
4. If not captured well: keep as human-track, add exploration_hint

**Fail**: Ask what's fundamentally wrong. Determine if it's a spec issue (need to change direction) or an execution issue (need to try harder in same direction).

### Step 4: Process Agent Suggestions

For each suggested constraint:
- Show the suggestion with rationale
- Options: Adopt (add to spec) | Ignore | Modify then adopt
- Adopted suggestions increment spec version

### Step 5: Update State

Remove processed items from queue. Update project state. If spec changed, log in changelog.

## The Feedback Conversion Engine

This is the most important part of review. Every piece of human feedback is an opportunity to shrink the human track:

```
Human says              → Agent converts to
"feels slow"            → "response time < 200ms" (auto)
"code is messy"         → "golangci-lint passes" (auto)
"tone shifts in ch3"    → "tone consistency score ≥ 4" (ai_review)
"navigation confusing"  → "max 2 clicks to any feature" (auto)
"story is boring"       → harder — add exploration_hint, keep human
```

Not everything can be converted. "Story is boring" has no good proxy. That's fine — add it as exploration_hint ("try increasing conflict density, add a plot twist in ch3") and keep the quality dimension as human-track.

## Rules
1. **Always attempt feedback conversion.** Even partial conversion is valuable.
2. **Show conversion before applying.** Human must confirm the objective version captures their intent.
3. **High-priority items first.** They're blocking agent work.
4. **Don't overwhelm.** If >10 items in queue, show top 5 and ask if user wants to see rest.
