---
name: getting-started
description: Bootstrap for Ratchet. Loaded at session start. Establishes the story-first model — humans align through narrative (story), then specify constraints (spec), then agent executes autonomously. Includes intent routing, session resumption, and phase detection.
---

# Ratchet — Session Bootstrap

You have the Ratchet plugin. It turns intent into verified results through autonomous iteration.

## How It Works

```
/ratchet:story "describe what you want to build"
  → Role selection (end-user, developer, DevOps, QA, security...)
  → Parallel perspective agents analyze from each role's angle
  → PM synthesizes into unified requirements
  → You confirm with all perspectives visible
  → Manager sequences into specs/phases
  → Auto-transitions to spec phase

Spec phase (usually automatic):
  → Reads story artifacts, extracts constraints
  → You confirm → Agent runs everything autonomously
  → Agent notifies when ready for review

/ratchet:review
  → See results with proof of work
  → Give feedback → triggers another autonomous round
  → Or just say feedback directly in conversation
```

Story + review. Two touchpoints for most workflows.

## Intent Routing

When the user describes work, determine what to do:

```
User says something → Agent determines:

  Mentions existing intent name/keyword?
    → Route to that intent
    → If status=done: reactivate, enter modification chain
       (story update → spec re-derive → test update → execute → verify)
    → If status=agent_running: queue modification for next iteration
    → If status=paused: suggest /ratchet:resume, then apply changes
    → If status=draft: continue story or spec workflow
    → If ambiguous: ask which intent

  Describes something new?
    → /ratchet:story to create new intent

  Asks about progress?
    → /ratchet:status

  Asks about coverage?
    → /ratchet:coverage

  Gives feedback on results?
    → /ratchet:review flow (or direct modification chain)
```

### Routing Details

1. Read `~/.config/ratchet/state.yaml` to see registered intents
2. Match the user's description against existing intents (by name, workspace, tags, or description)
3. Route accordingly

**Never create a new intent when the user is describing changes to an existing project.**

### When to Create a New Intent vs Update

- **Update existing:** Same product, same or evolved acceptance criteria. Bug fixes, polish, feature additions within the same scope.
- **New intent:** Fundamentally new work with its own acceptance criteria. Two intents can share the same workspace directory.

## Session Resumption

Every new session, detect state and resume:

```
Read ~/.config/ratchet/state.yaml
  → Find all intents and their phases

For current workspace's intent:

  Case A: Story in progress (story files exist, no spec)
    → "We were discussing [name]'s user journey.
       Last confirmed: [artifacts].
       Still need to confirm: [artifacts].
       Let's continue."
    → Load story files into context

  Case B: Spec confirmed, execution not started
    → "[Name] spec is ready. Starting execution."
    → Begin autonomous execution

  Case C: Execution in progress (execution-state.yaml exists)
    → "[Name]: [N]/[total] WPs complete.
       WP-[id] was at iteration [N], score [X].
       Resuming from checkpoint."
    → Continue execution from checkpoint

  Case D: Phase complete, next phase pending
    → "[Name] Phase [N] complete!
       Phase [N+1] is next. Ready to start story phase?"

  Case E: All phases done
    → "[Name] is complete. All phases done.
       Want to review, check coverage, or make modifications?"

  If multiple intents exist and not in a specific workspace:
    → Show summary of all intents
    → Ask which one to work on
```

## When to Use Ratchet

Not everything needs the full story → spec → plan → execute pipeline.

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

**Simple standalone spec (skip story):**
- When the user already has a clear technical spec or requirements
- `/ratchet:spec` directly, no story phase needed

**Rule of thumb:** If you need verification that the fix actually works across multiple scenarios, use Ratchet. If it's a one-liner, just fix it. If it's a new product, start with `/ratchet:story`.

## Commands

**User-facing (daily use):**

| Command | When to use |
|---------|-------------|
| `/ratchet:story` | Start something new — align on what to build |
| `/ratchet:spec` | Convert story to constraints (usually auto), or standalone for simple projects |
| `/ratchet:review` | Evaluate completed work, give feedback |
| `/ratchet:coverage` | View story/scenario/test coverage dashboard |
| `/ratchet:status` | Check progress across intents |
| `/ratchet:profile` | Set personal preferences (one-time) |

**Also available:**

| Command | When to use |
|---------|-------------|
| `/ratchet:pause` | Pause execution |
| `/ratchet:resume` | Resume execution |

**Internal (agent calls automatically):**
- **plan** — decompose spec into work packages
- **verify** — three-tier verification after any code change
- **execute** — ratchet loop orchestration
- **report** — iteration reports with proof of work
- **metrics** — time, tokens, automation stats
- **update** — process story/spec modifications from conversation

## Giving Feedback

Two equally valid ways:

**In conversation:** Just say it — "the results page has encoding errors" or "make the quiz questions bigger." Agent automatically converts feedback to constraints, updates spec, and re-executes.

**Via `/ratchet:review`:** For processing accumulated review items, especially across multiple intents or after a break.

## What Happens After Story Confirmation

The agent automatically chains:
1. **Spec generation** — reads PM synthesis + role perspectives, extracts role-tagged constraints, generates Intent Spec
2. **Spec review** — HTML review page for section-by-section confirmation
3. **Session boundary** — for phases, suggest new session for execution

After spec confirmation:
4. Environment preparation (install tools, scaffold, discover capabilities)
5. Test suite generation (from spec constraints)
6. Pipeline validation (verify infrastructure works)
7. Plan decomposition (work packages with dependencies)
8. Ratchet execution (implement → verify → keep/discard → repeat)
9. Report generation (with proof of work and resource usage)
10. Human review queue (only subjective/taste items)

## Key Principles

1. **Story first.** Align understanding through narrative before writing constraints.
1.5. **Multi-perspective.** Story gathers perspectives from relevant roles (end-user, developer, DevOps, QA, security), synthesized by PM. Features built from a single viewpoint have blind spots.
2. **Human provides direction and taste.** Agent does everything else.
3. **Spec review is thorough.** No time limit. The more you invest here, the less rework.
4. **Maximum coverage.** Agent aggressively maximizes auto-verification. Basic functionality is never left to human review.
5. **EVA.** Verify that the testing infrastructure works BEFORE execution.
6. **Ratchet.** Every iteration either improves (keep) or doesn't (discard). Progress is monotonic.
7. **Proof of work.** Reports include actual test output, not just pass/fail.
8. **Sessions are disposable.** Files are the single source of truth. Any session can resume from where any previous session left off.
9. **Auto-verify on every change.** Any code modification triggers full verification — non-negotiable.

## State Locations

- Global: `~/.config/ratchet/` (profile, intent registry, review queue)
- Per-intent: `.ratchet/{intent-id}/` in workspace (spec, test suite, plan, logs, reports)
- Story: `.ratchet/story/` (top-level) or `.ratchet/phases/{phase}/story/` (per-phase)
- Multiple intents can share the same workspace — each gets its own subdirectory
