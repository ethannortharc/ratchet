---
name: review
description: Process the human-track review queue across all intents. Shows pending items sorted by priority (blocking items first), with intent ID and workspace for each. Handles feedback and converts subjective input into agent-verifiable constraints when possible. Use when the user says "review", "what needs my attention", "any pending items", or after agent notifies of completed work.
---

# Review — Human-Track Async Queue

## Workflow

### Step 1: Load Queue
Read `~/.config/ratchet/review_queue.yaml`. If empty, report "No pending reviews."

### Step 2: Show Queue (sorted by priority)

```
📋 Review Queue ([N] items across [M] intents)

🔴 [high] prism / WP description
   Intent: prism │ Workspace: /Users/coder/projects/prism
   Constraint: [claim]
   📎 [artifact path or inline preview]
   📝 [checklist path if exists]

⚪ [normal] note-cli / WP description
   Intent: note-cli │ Workspace: /Users/coder/projects/note-cli
   Constraint: [claim]
   📎 [artifact path]

🔧 Auto-upgrade opportunities ([N] items)
   These items are currently human-track but COULD be auto-verified:
   1. [prism] QD-03: "responsive layout" — install Playwright to auto-verify
   2. [note-cli] INV-05: "CLI outputs valid JSON" — can be auto-tested with jq

💡 Agent Suggestions ([N] items)
   1. [prism]: [proposed constraint] — [rationale]
```

**Auto-upgrade section**: For any review item where `could_be_auto: true`, show what tool is missing and what it would unlock. If the user approves, install the tool and convert the constraint from human-track to agent-track.

### Step 3: Process Reviews

For each item the user reviews:

**Pass**: Mark constraint as verified, remove from queue. If this unblocks downstream WPs, note it.

**Revise**: Ask for specific feedback. Then:
1. Try to convert feedback into an agent-verifiable constraint
2. Show the conversion: "You said '[subjective feedback]'. I'll add this constraint: '[objective version]' with test_method: '[how to test it]'. Does this capture it?"
3. If confirmed: add to Intent Spec (with test_method + tools_required), increment version, regenerate test in `.ratchet/test-suite/`, trigger new iteration
4. If not captured well: keep as human-track, add to agent_guidance

**Fail**: Ask what's fundamentally wrong. Determine if it's an Intent Spec issue (need to change direction) or an execution issue (need to try harder in same direction).

### Step 4: Process Agent Suggestions

For each suggested constraint:
- Show the suggestion with rationale and proposed test_method
- Options: Adopt (add to Intent Spec) | Ignore | Modify then adopt
- Adopted suggestions increment spec version

### Step 5: Update State

Remove processed items from queue. Update intent state in `~/.config/ratchet/state.yaml`:
- If all human reviews pass → set status to `done`
- If feedback triggers new round → set status to `agent_running`
- Update `current_blocker` field (clear if resolved, set if new blockers)

## The Feedback Conversion Engine

This is the most important part of review. Every piece of human feedback is an opportunity to shrink the human track:

```
Human says              → Agent converts to
"feels slow"            → "response time < 200ms" (auto)
"code is messy"         → "golangci-lint passes" (auto)
"tone shifts in ch3"    → "tone consistency score ≥ 4" (ai_review)
"navigation confusing"  → "max 2 clicks to any feature" (auto)
"story is boring"       → harder — add to agent_guidance, keep human
```

Not everything can be converted. "Story is boring" has no good proxy. That's fine — add direction to `agent_guidance` ("try increasing conflict density, add a plot twist in ch3") and keep the quality dimension as human-track.

## Direct Feedback (outside /ratchet:review)

Users don't need to use this command to give feedback. When a user reports an issue directly in conversation (e.g., "the results page has encoding errors"), the agent should:

1. Run the feedback conversion engine immediately
2. Determine if this is a basic functionality issue (should have been auto-caught) or a subjective quality issue
3. For basic functionality: fix immediately + add as auto-verifiable constraint + add integration test
4. For quality issues: convert to constraint if possible, update Intent Spec, trigger new iteration

This is equivalent to processing a review inline — same engine, just without the formal queue.

## Rules
1. **Always attempt feedback conversion.** Even partial conversion is valuable.
2. **Show conversion before applying.** Human must confirm the objective version captures their intent.
3. **High-priority items first.** They're blocking agent work.
4. **Don't overwhelm.** If >10 items in queue, show top 5 and ask if user wants to see rest.
5. **Show intent ID and workspace** for every review item.
6. **Surface auto-upgrade opportunities.** Every `could_be_auto` item should come with a tool recommendation.
7. **Basic functionality bugs = agent failure.** If a human finds a broken button or encoding error, acknowledge this should have been caught automatically, fix it, and add an integration test to prevent recurrence.
