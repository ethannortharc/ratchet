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

## Verification Order (Multi-Level)

Verification runs in levels, from fastest/simplest to most comprehensive:

### Level 1: Static Checks (agent track)
Build, lint, type-check. Catches syntax errors and obvious issues.
```bash
# Examples:
npm run build          # Compiles
npm run lint           # Linting
tsc --noEmit           # Type checking
```

### Level 2: Unit Tests (agent track)
Execute check commands from test suite, capture exit codes AND raw output (stdout + stderr). Pass = 0, fail = non-zero.

**Capture raw output** for proof of work:
```yaml
raw_output: |
  PASS src/scoring.test.ts (0.8s)
    ✓ type 1 full score → primary type 1
    ✓ tie between type 2 and 3 → alphabetical tiebreak
    ...
```

Use test files from `.ratchet/test-suite/` when available (check manifest.yaml).

### Level 3: Integration / Smoke Tests (agent track)
**Actually run the artifact and verify basic functionality.** This is the level that catches encoding errors, broken buttons, pages not rendering — issues that unit tests miss.

The approach depends on what the project produces:

| Artifact | How to verify | Tool |
|----------|--------------|------|
| Web app | Start dev server + Playwright tests | Playwright |
| CLI | Run with known inputs, check output | shell |
| API | Start server + curl endpoints | curl |
| Library | Run example/integration code | runtime |
| Document | Validate structure, completeness | shell + LLM |

**If Level 3 tools are missing:** Record as `skipped` with `missing_capability` set. Suggest installation. Do NOT silently downgrade to human review — explicitly flag that basic functionality verification was skipped.

```yaml
# Example Level 3 for web project:
# 1. Start dev server in background
# 2. Wait for server ready
# 3. Run Playwright tests: page loads, navigation works, buttons clickable, no console errors
# 4. Kill dev server
```

**Key rule: Basic functionality issues must be caught at Level 3, not by human review.** If an encoding error, broken button, or navigation failure reaches the human, the verification system has failed.

If check fails due to missing tool: record as `skipped`, suggest installation.

### 2. AI Review Verifiers (agent track — only after all auto levels pass)
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

The ratchet loop (retry on failure, keep improvements, discard regressions) is orchestrated by the **execute** skill. See `skills/execute/SKILL.md` for the full loop logic, including stuck detection and early escalation.

This skill (verify) is called BY the execute skill's loop — the verifier subagent runs verification, returns results, and the execute skill makes the keep/discard decision based on composite score.

On completion: the execute skill updates intent status in state.yaml:
- All agent-track pass → `agent_complete`
- Human items queued → `human_review`

### Git Ratchet (for projects with .git)
- Single execution branch: `ratchet/execute`
- Commit on improvement, reset on no improvement
- Tag checkpoints: `ratchet/wp-{id}/passed` (all constraints pass) or `ratchet/wp-{id}/best` (budget exhausted, best score)
- Merge `ratchet/execute` to main when all WPs complete with all agent constraints passing

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
7. **Run all three levels.** Static → Unit → Integration. Don't stop at unit tests. If Level 3 tools are available, USE them.
8. **Auto-upgrade suggestions.** When queuing a human-track item, check: could this be auto-verified with a tool? If yes, set `could_be_auto: true` and `missing_capability` with the tool name. Suggest the upgrade in `/ratchet:review`.
9. **Basic functionality = agent responsibility.** Encoding errors, broken buttons, pages not rendering, navigation failures — these are NEVER acceptable as human review items. They must be caught by Level 3 integration tests.
10. **Short-circuit on auto failure.** If any auto level (1/2/3) fails, do NOT run ai_review. Return the failure immediately so the ratchet loop can retry faster. AI review only runs when all auto verifications pass — evaluating quality on broken code wastes tokens and produces misleading scores.
