---
name: getting-started
description: Bootstrap for Ratchet. Loaded at session start. Establishes the two-touchpoint model — humans provide direction (spec) and evaluate results (review), agent handles everything else. Includes intent routing and usage guidance.
---

# Ratchet — Session Bootstrap

You have the Ratchet plugin. It turns intent into verified results through autonomous iteration.

## How It Works

```
/ratchet:spec "describe what you want"
  → Guided conversation to define intent (~5-30 min, as thorough as needed)
  → Confirm → Agent runs everything autonomously
  → Agent notifies when ready for review

/ratchet:review
  → See results with proof of work
  → Give feedback → triggers another autonomous round
  → Or just say the feedback directly in conversation
```

That's it. Two commands for most workflows.

## Intent Routing

When the user describes work, determine if it targets an existing intent before creating a new one.

1. Read `~/.config/ratchet/state.yaml` to see registered intents
2. Match the user's description against existing intents (by name, workspace, tags, or description)
3. Route:

```
User describes work
  ├─ Matches existing intent
  │   ├─ Status: done → reactivate (set status to active), invoke update skill
  │   ├─ Status: agent_running → invoke update skill (changes apply next iteration)
  │   ├─ Status: paused → suggest /ratchet:resume, then apply changes
  │   └─ Status: draft → continue spec workflow
  │
  ├─ Clearly new work → /ratchet:spec
  │
  └─ Ambiguous → ask: "Is this a change to [intent-name], or something new?"
```

**Never create a new intent when the user is describing changes to an existing project.**

### When to Create a New Intent vs Update

- **Update existing:** Same product, same or evolved acceptance criteria. Bug fixes, polish, feature additions within the same scope. E.g., "fix the sharing on the personality test site"
- **New intent:** Fundamentally new work with its own acceptance criteria. E.g., "add MBTI test" (new quiz, scoring, results — all independent of existing Enneagram test). Two intents can share the same workspace directory.

## When to Use Ratchet

Not everything needs the full spec → plan → execute pipeline.

**Direct fix (no Ratchet):**
- Single bug, clear cause, few minutes to fix
- "This button doesn't work" → just fix it, add a test to prevent recurrence
- If the project has an existing Ratchet intent, add the test to its test suite

**One intent, multiple WPs:**
- Batch of related bugs or features in the same project
- "Fix these 5 issues with the website" → one intent, one WP per issue
- Ratchet ensures all are fixed and verified

**One intent, quantified goal:**
- Systemic issues with measurable targets
- "Lighthouse score 60 → 90" or "reduce bundle size by 50%"
- Perfect for ratchet loop — each iteration measurably improves

**Rule of thumb:** If you need verification that the fix actually works across multiple scenarios, use Ratchet. If it's a one-liner, just fix it.

## Commands

| Command | When to use |
|---------|-------------|
| `/ratchet:spec` | Start something new |
| `/ratchet:review` | Evaluate completed work |
| `/ratchet:status` | Check progress anytime |
| `/ratchet:pause` | Pause execution |
| `/ratchet:resume` | Resume execution |

## Giving Feedback

Two equally valid ways:

**In conversation:** Just say it — "the results page has encoding errors" or "make the quiz questions bigger." Agent automatically converts feedback to constraints, updates spec, and re-executes.

**Via `/ratchet:review`:** For processing accumulated review items, especially across multiple intents or after a break.

## What Happens After Spec Confirmation

The agent automatically chains (no human intervention needed):
1. Environment preparation (install tools, scaffold, discover capabilities)
2. Test suite generation (from spec constraints)
3. Pipeline validation (verify infrastructure works)
4. Plan decomposition (work packages with dependencies)
5. Ratchet execution (implement → verify → keep/discard → repeat)
6. Report generation (with proof of work and resource usage)
7. Human review queue (only subjective/taste items)

Uses subagents for parallel execution where possible.

## Key Principles

1. **Human provides direction and taste.** Agent does everything else.
2. **Spec review is thorough.** No time limit. The more you invest here, the less rework.
3. **Maximum coverage.** Agent aggressively maximizes auto-verification. Basic functionality is never left to human review.
4. **EVA.** Verify that the testing infrastructure works BEFORE execution. Discover verification capabilities, test headless mode, validate all tools.
5. **Ratchet.** Every iteration either improves (keep) or doesn't (discard). Progress is monotonic.
6. **Proof of work.** Reports include actual test output, not just pass/fail.

## State Locations

- Global: `~/.config/ratchet/` (profile, intent registry, review queue)
- Per-intent: `.ratchet/` in workspace (spec, test suite, plan, logs, reports)
