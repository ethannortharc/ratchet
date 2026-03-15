---
name: verify
description: Run three-tier verification with ratchet optimization loop. Executes auto verifiers, runs ai_review, queues human items. On failure, automatically retries within budget (ratchet loop) before escalating. Use after executing work packages, or when checking quality. Triggers on "check this", "is this done", "verify", "does this meet spec".
---

# Verify — Three-Tier Verification + Ratchet Loop

## Prerequisites
`.ratchet/spec.yaml` (Intent Spec) must exist. Artifacts to verify must be present.

## Verification Order

### 1. Auto Verifiers (agent track)
Execute check commands, capture exit codes. Pass = 0, fail = non-zero.
If check fails due to missing tool: record as `skipped`, suggest installation.

### 2. AI Review Verifiers (agent track)
For each `verifier: ai_review` constraint:
- Load artifact + rubric + project context
- Use the constraint's `test_method` to guide evaluation focus
- Evaluate critically (don't rubber-stamp)
- Produce: score, pass/fail, justification, specific issues

Use this review prompt template:
```
CONSTRAINT: [claim]
RUBRIC: [rubric text]
THRESHOLD: [minimum score]
TEST METHOD: [test_method — what specifically to evaluate]
ARTIFACT: [content]
CONTEXT: [Intent Spec excerpts, settings docs]

Evaluate honestly. Output:
SCORE: [number]
PASS: [yes/no]
JUSTIFICATION: [2-3 sentences]
ISSUES: [specific issues or "none"]
```

### 3. Human Verifiers (human track)
Do NOT run these inline. Queue them to `~/.config/ratchet/review_queue.yaml`:
```yaml
- id: rev-{timestamp}
  project: {name}
  project_path: {path}
  wp: {wp-id}
  constraint_id: {constraint}
  summary: {one-line description}
  artifact: {path to artifact}
  priority: high | normal  # high if blocking downstream WPs
  queued_at: {datetime}
```

## Ratchet Loop

When agent-track verification fails AND ratchet is enabled:

```
best_score = current_composite_score
for attempt in range(budget):

    # Feed failure details as context
    feedback = format_failures(failed_constraints)
    result = re_execute(wp, additional_context=feedback)

    # Re-verify agent-track only
    scores = verify_agent_track(result)
    composite = calculate_composite(scores)

    if all_agent_pass(scores):
        git_commit("wp-{id}: all agent verifications passed")
        mark_status("agent_complete")
        queue_human_track_items()
        break

    elif composite > best_score:
        git_commit("wp-{id}: improved {best_score:.2f} → {composite:.2f}")
        best_score = composite
        # Continue iterating

    else:
        git_reset()
        # Try different approach next iteration

if not all_agent_pass after budget:
    notify_human("wp-{id}: {budget} iterations, best score {best_score}")
    queue_for_human_review_with_context()
```

### Git Ratchet (for projects with .git)
- Each WP iterates on a branch: `ratchet/{wp-id}/iter`
- Commit on improvement, reset on no improvement
- Merge to main when all agent constraints pass

### Filesystem Ratchet (for non-git projects)
- `artifacts/staging/` = current attempt
- `artifacts/current/` = best so far
- Improved → copy staging to current, old current to history
- Not improved → clear staging

## Recording Results

Append to `.ratchet/review_log.yaml`:
```yaml
- timestamp: datetime
  project: string
  wp: string
  constraint_id: string
  track: agent | human
  verifier_type: auto | ai_review | human
  result: pass | fail | revise | skipped
  score: number
  iteration: int           # Which ratchet iteration
  reason: string           # ONLY on fail/revise:
    # spec_ambiguity | decomposition_error | execution_error | quality_gap
  detail: string
  issues: [string]
  could_be_auto: bool
  missing_capability: string
```

## Constraint Discovery

During execution and verification, if you discover issues NOT covered by any Intent Spec constraint:

Append to `.ratchet/suggested_constraints.yaml`:
```yaml
- id: sug-{N}
  discovered_during: {wp-id}
  type: invariant | quality_dimension
  claim: string
  rationale: string
  proposed_track: agent | human
  proposed_verifier: auto | ai_review | human
  proposed_check: string
  proposed_test_method: string
  proposed_tools_required: [string]
  urgency: high | normal
  action_taken: string  # What you did as a temporary fix
```

These appear in `/ratchet:review` for human approval.

## Rules
1. **Never block on human-track items.** Queue them and continue.
2. **Always classify failure reason.** This is non-negotiable for the feedback loop.
3. **Be genuinely critical in ai_review.** Finding real issues early saves iteration cycles.
4. **Propose constraints you discover.** Don't silently fix things — capture them for the Intent Spec.
