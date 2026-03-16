---
name: getting-started
description: Bootstrap for Ratchet. Loaded at session start. Establishes the two-touchpoint model — humans provide direction (spec) and evaluate results (review), agent handles everything else.
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
1. Environment preparation (install tools, scaffold)
2. Test suite generation (from spec constraints)
3. Pipeline validation (verify infrastructure works)
4. Plan decomposition (work packages with dependencies)
5. Ratchet execution (implement → verify → keep/discard → repeat)
6. Report generation (with proof of work)
7. Human review queue (only subjective/taste items)

Uses subagents for parallel execution where possible.

## Key Principles

1. **Human provides direction and taste.** Agent does everything else.
2. **Spec review is thorough.** No time limit. The more you invest here, the less rework.
3. **Maximum coverage.** Agent aggressively maximizes auto-verification. Basic functionality is never left to human review.
4. **EVA.** Verify that the testing infrastructure works BEFORE execution.
5. **Ratchet.** Every iteration either improves (keep) or doesn't (discard). Progress is monotonic.
6. **Proof of work.** Reports include actual test output, not just pass/fail.

## State Locations

- Global: `~/.config/ratchet/` (profile, intent registry, review queue)
- Per-intent: `.ratchet/` in workspace (spec, test suite, plan, logs, reports)
