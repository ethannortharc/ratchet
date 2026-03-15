---
name: verify
description: Run three-tier verification with ratchet optimization loop. Executes auto verifiers, runs ai_review, queues human items. Captures raw verification output for proof of work in reports. On failure, automatically retries within budget (ratchet loop) before escalating. Workspace-aware — accepts optional intent ID.
---

# Verify — Three-Tier Verification + Ratchet Loop

## Prerequisites
`.ratchet/spec.yaml` (Intent Spec) must exist. Artifacts to verify must be present.

## Workspace Resolution

1. If intent ID provided → look up workspace in `~/.config/ratchet/state.yaml`
2. If current directory is inside a registered workspace → use that intent
3. If ambiguous → ask user to choose

ALL verification commands must run within the resolved workspace directory.

## Intent State

On starting verification: set intent status to `agent_running` in state.yaml.

## Verification Order

### 1. Auto Verifiers (agent track)
Execute check commands, capture exit codes AND raw output (stdout + stderr). Pass = 0, fail = non-zero.
If check fails due to missing tool: record as `skipped`, suggest installation.

**Capture raw output** for proof of work:
```yaml
# Store in review_log alongside pass/fail
raw_output: |
  PASS src/scoring.test.ts (0.8s)
    ✓ type 1 full score → primary type 1
    ✓ tie between type 2 and 3 → alphabetical tiebreak
    ...
```

Use test files from `.ratchet/test-suite/` when available (check manifest.yaml).

### 2. AI Review Verifiers (agent track)
For each `verifier: ai_review` constraint:
- Load the review prompt from `.ratchet/test-suite/QD-XX.review.md` if available
- Otherwise construct from artifact + rubric + project context
- Use the constraint's `test_method` to guide evaluation focus
- Evaluate critically (don't rubber-stamp)
- Produce: score, pass/fail, justification, specific issues
- **Capture full review response** for proof of work

Use this review prompt template:
```
CONSTRAINT: [claim]
RUBRIC: [rubric text]
THRESHOLD: [minimum score]
TEST METHOD: [test_method — what specifically to evaluate]
ARTIFACT: [content]
CONTEXT: [Intent Spec excerpts, agent_guidance]

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
  intent_id: {intent-id}
  project: {name}
  project_path: {workspace path}
  wp: {wp-id}
  constraint_id: {constraint}
  summary: {one-line description}
  artifact: {path to artifact}
  checklist: {path to .ratchet/test-suite/XX.checklist.md if exists}
  priority: high | normal  # high if blocking downstream WPs
  queued_at: {datetime}
```

## Ratchet Loop

When agent-track verification fails AND ratchet is enabled:

```
best_score = current_composite_score
for attempt in range(budget):

    # Feed failure details as context, include agent_guidance
    feedback = format_failures(failed_constraints)
    result = re_execute(wp, additional_context=feedback + agent_guidance)

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

On completion: update intent status in state.yaml:
- All agent-track pass → `agent_complete`
- Human items queued → `human_review`

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
  intent_id: string
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
  raw_output: string       # Captured stdout/stderr or review response (for proof of work)
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
  proposed_tools_required:
    - id: string
      install: string
      agent_can_install: bool
  urgency: high | normal
  action_taken: string  # What you did as a temporary fix
```

These appear in `/ratchet:review` for human approval.

## Rules
1. **Never block on human-track items.** Queue them and continue.
2. **Always classify failure reason.** This is non-negotiable for the feedback loop.
3. **Be genuinely critical in ai_review.** Finding real issues early saves iteration cycles.
4. **Propose constraints you discover.** Don't silently fix things — capture them for the Intent Spec.
5. **Capture raw output.** Every verification result must include the actual output for proof of work.
6. **Stay in workspace.** All operations within the registered workspace path.
