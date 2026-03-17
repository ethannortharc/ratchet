---
name: execute
description: Orchestrate the ratchet execution loop. For each work package, spawns wp-executor and verifier subagents, makes keep/discard decisions based on composite score, manages git commits/resets, and spawns report-writer on completion. Called automatically by spec skill after planning — users don't invoke this directly.
---

# Execute — Ratchet Loop Orchestration

## Prerequisites

- `.ratchet/{intent-id}/spec.yaml` (Intent Spec) must exist
- `.ratchet/{intent-id}/plan.yaml` (work package plan) must exist
- `.ratchet/{intent-id}/test-suite/` (generated test suite) must exist
- `.ratchet/{intent-id}/pre-validation.log` should confirm no blockers

## Workspace Resolution

1. If intent ID provided → look up workspace in `~/.config/ratchet/state.yaml`
2. If current directory is inside a registered workspace → use that intent
3. If ambiguous → ask user to choose

## Intent State

On starting execution: set intent status to `agent_running` in state.yaml.

## Execution Loop

For each parallel group of WPs (respecting dependency order from plan.yaml):

### Per-WP Ratchet Cycle

```
best_score = 0.0
score_history = []
failure_history = {}  # constraint_id → [error signatures]
wp_start_time = now()
wp_total_tokens = 0

for iteration in range(1, budget + 1):

    0. Check stuck detectors (see Stuck Detection section below)
       → If stuck: add strategy change hints to executor context
       → If escalate_to_human: break early, queue for human review

    1. Spawn wp-executor subagent (sonnet)
       → Input: WP definition, workspace, spec.yaml, test files, iteration feedback + stuck hints
       → Output: implemented code within workspace

    2. Spawn verifier subagent (sonnet)
       → Input: WP acceptance criteria, workspace, spec.yaml, manifest, iteration #
       → Output: verification results with composite score + recommendation
       Note: Verifier short-circuits — Level 1 fail returns immediately with score 0.0

    3. Track history + resources:
       → score_history.append(composite_score)
       → update failure_history with per-constraint error signatures
       → wp_total_tokens += executor_tokens + verifier_tokens
       → record iteration wall time and token usage in review_log.yaml

    4. Ratchet decision (based on verifier output):
       - all_agent_pass → git commit "wp-{id}: all agent constraints passed"
                        → tag: ratchet/wp-{id}/passed
                        → mark WP status: agent_complete
                        → queue human-track items to review_queue.yaml
                        → break
       - composite > best_score → git commit "wp-{id}: improved {best:.2f} → {composite:.2f}"
                                → best_score = composite
                                → continue
       - composite <= best_score → git reset (discard changes)
                                 → continue with different approach hint

    5. If budget exhausted without all_agent_pass:
       → tag: ratchet/wp-{id}/best
       → notify human: "wp-{id}: {budget} iterations, best score {best_score:.2f}"
       → queue for human review with full context
```

## Stuck Detection

The ratchet loop includes two stuck detectors that trigger before budget exhaustion:

### Detector 1: Repeated Failure (same constraint, similar error)

Track failure reasons per constraint across iterations. If a constraint fails **3 consecutive times** with the same `reason` category (e.g., `execution_error`) and similar `raw_output` (same error message or test failure):

**Action — escalate in stages:**
1. **Iteration 3 of same failure:** Add exploration hint to wp-executor context: "Previous 3 attempts failed on [constraint] with [error pattern]. Try a fundamentally different approach — different algorithm, different library, different data structure."
2. **Iteration 5 of same failure:** Suggest re-decomposition to main agent: "WP {id} may be too large or have a hidden dependency. Consider splitting or re-ordering."
3. **Budget - 1 with same failure:** Escalate to human early: "WP {id} is stuck on [constraint]. [N] attempts with same failure pattern. May need human guidance."

### Detector 2: Score Oscillation (lateral movement)

Track composite scores across iterations. If the **last 3 scores** have:
- Variance < 0.01 (scores are nearly identical), AND
- Mean has not increased compared to 3 iterations ago

Then the agent is making lateral moves, not progress.

**Action:** Add strategy change hint to wp-executor: "Score has plateaued at ~{mean:.2f} for 3 iterations. The current approach has hit its ceiling. Try: (a) different architecture, (b) simplify to pass more constraints even if some are weaker, (c) focus on the lowest-scoring constraint first."

### Implementation

The orchestrator (this skill) tracks:
```yaml
stuck_tracking:
  wp-01:
    failure_history:
      INV-03:
        - {iteration: 1, reason: execution_error, error_sig: "TypeError: Cannot read property 'score'"}
        - {iteration: 2, reason: execution_error, error_sig: "TypeError: Cannot read property 'score'"}
        - {iteration: 3, reason: execution_error, error_sig: "TypeError: Cannot read property 'score'"}
        # → Detector 1 fires: 3 consecutive same-signature failures
    score_history: [0.45, 0.62, 0.61, 0.63, 0.62]
    # → Detector 2 fires: last 3 scores [0.61, 0.63, 0.62] variance < 0.01, mean ≈ same as 3 ago
```

This tracking is in-memory during execution (not persisted to disk). The execute skill maintains it across iterations for each WP.

### After Each WP Completes

Spawn report-writer subagent (haiku) for that WP's results:
- Input: intent ID, workspace, review_log.yaml, spec.yaml, WP ID
- Output: `.ratchet/{intent-id}/reports/wp-{id}.md`

### After All WPs in a Parallel Group Complete

- Spawn report-writer subagent (haiku) in **summary** mode:
  - Input: intent ID, workspace, review_log.yaml, spec.yaml, round number, trigger
  - Output: `.ratchet/{intent-id}/reports/iter-{NNN}.md` (references per-WP reports)
- Update intent status based on results:
  - All WPs agent_complete, no human items → `agent_complete`
  - Human items queued → `human_review`
- Notify user: "Ready for /ratchet:review"

## Git Strategy

- Single execution branch: `ratchet/execute`
- Tag checkpoints per WP: `ratchet/wp-{id}/passed` or `ratchet/wp-{id}/best`
- Commit on improvement, reset on no improvement
- Merge to main when all agent constraints pass across all WPs

### Filesystem Ratchet (for non-git projects)

- `artifacts/staging/` = current attempt
- `artifacts/current/` = best so far
- Improved → copy staging to current, old current to history
- Not improved → clear staging

## Resource Tracking

Track wall time, token consumption, and model for every subagent call. This data feeds into reports and cross-project metrics.

**How to capture:** When the Agent tool returns, its result includes `<usage>` metadata with `total_tokens` and `duration_ms`. Extract these values after each subagent call:

```
Before spawning subagent: record start_time = now()

After subagent returns:
  wall_time = now() - start_time
  tokens = [extract total_tokens from Agent tool return metadata]
  model = [the model parameter used when spawning the subagent]
```

Per iteration, write to `.ratchet/{intent-id}/review_log.yaml`:
```yaml
- wp: wp-01
  iteration: 1
  executor:
    model: sonnet
    wall_time_ms: 45000
    tokens: 32000
  verifier:
    model: sonnet
    wall_time_ms: 12000
    tokens: 8500
```

Per WP, aggregate and include in report-writer input:
- `wp_wall_time`: total elapsed time (start to completion)
- `wp_total_tokens`: sum of all executor + verifier tokens across iterations
- `wp_iterations`: number of ratchet iterations
- `wp_models`: models used (for cost analysis)

**This data is REQUIRED in every report.** If resource data is missing from review_log.yaml, the report-writer must note "Resource data not captured" rather than silently omitting the section.

## Rules

1. **Respect dependency order.** Only start a WP when its `depends_on` WPs are complete.
2. **Parallel where possible.** Independent WPs in the same parallel group run simultaneously.
3. **One verifier per executor.** Always verify before making ratchet decisions.
4. **Report per WP.** Spawn report-writer after each WP, not just at the end.
5. **Stay in workspace.** All operations within the registered workspace path.
6. **Track resources.** Record wall time and token usage for every subagent call.
