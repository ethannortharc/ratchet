---
name: verify
description: "Three-tier verification for work packages. Executes static checks, unit tests, integration tests, AI review, and QA review. Returns results to execute skill which handles ratchet decisions via Python tools. Agent focuses on creative verification work."
---

# Verify — Three-Tier Verification (v6)

## Overview

Verify is the creative verification engine. It runs multi-level checks on work packages and returns results. The **execute** skill orchestrates the ratchet loop and records all state via Python tools — verify focuses purely on running checks and producing honest assessments.

## Agent Registration

When spawned as a verifier subagent, the execute skill has already registered this agent:

```bash
python tools/ratchet.py agent register {sprint_id} verifier "Verifier WP-{id}" --model sonnet
```

## Auto-Verification Rule

**Any code change triggers automatic full verification.** This is non-negotiable.

After ANY code modification (regardless of source — WP execution, bug fix, spec update, manual edit), run the complete verification chain below. Do not skip levels. Do not wait for user to request verification.

## Verification Order (Multi-Level)

Verification runs in levels, from fastest/simplest to most comprehensive:

### Level 1: Static Checks (agent track)
Build, lint, type-check, format-check. Catches syntax errors and obvious issues. **Must pass before proceeding to Level 2.**

```yaml
# By project type — install during environment preparation:

web_app (React/TypeScript):
  - tsc --noEmit              # Type checking
  - eslint .                  # Linting
  - prettier --check .        # Format check
  - npm run build             # Compilation

go:
  - go vet ./...              # Static analysis
  - golangci-lint run         # Comprehensive linting

python:
  - ruff check .              # Linting (replaces flake8+isort+pyupgrade)
  - mypy .                    # Type checking

rust:
  - cargo clippy              # Linting
  - cargo fmt --check         # Format check
  - cargo build               # Compilation
```

These tools are installed during environment preparation (env-preparer agent) and run as part of every Level 1 check. If a lint tool is not configured for the project, note it as a gap but don't block on it.

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

Use test files from `.ratchet/{intent-id}/test-suite/` when available (check manifest.yaml).

### Level 3: Integration / Smoke Tests (agent track)
**Actually run the artifact and verify basic functionality.** This is the level that catches encoding errors, broken buttons, pages not rendering — issues that unit tests miss.

Read `.ratchet/{intent-id}/pre-validation.log` to determine what verification capabilities are available (written by env-preparer). Use the discovered capabilities to decide HOW to verify — do not rely on a hardcoded tool table. Common strategies:

- **Has browser testing capability** → run in headless mode (no display required), verify pages render, interactions work, no console errors
- **Has HTTP client capability** → start server, hit endpoints, validate responses
- **Has container capability** → run full environment tests in container
- **No specialized tools** → run the artifact directly via shell, check output and exit codes

**"No display available" is NEVER a reason to skip Level 3.** Browser testing tools support headless mode by default. Check `pre-validation.log` for `headless: true` — if available, use it.

**If a needed capability is missing:** Record as `skipped` with `missing_capability` set. Suggest what capability is needed (not a specific tool). Do NOT silently downgrade to human review.

**Key rule: Basic functionality issues must be caught at Level 3, not by human review.** If an encoding error, broken button, or navigation failure reaches the human, the verification system has failed.

### AI Review Verifiers (agent track — only after all auto levels pass)
For each `verifier: ai_review` constraint:
- Load the review prompt from `.ratchet/{intent-id}/test-suite/QD-XX.review.md` if available
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

### QA Perspective Review (agent track — after all auto + ai_review pass)

After standard verification completes, the QA/Tester perspective agent reviews the overall test quality and scenario coverage. This runs on Sonnet.

**When to run:** Only when all auto levels (1+2+3) pass AND ai_review passes. Skipped during ratchet retry iterations to save time — only runs on the final passing iteration.

**QA agent reviews:**
1. **Scenario coverage**: Are all scenarios from `.ratchet/story/scenarios.md` (with source-role tags) tested?
2. **Edge case coverage**: Are the edge cases from the QA perspective document (`.ratchet/story/perspectives/qa-tester.md`) covered?
3. **Test quality**: Are tests actually testing meaningful behavior, or just asserting trivialities?
4. **Missing scenarios**: Did execution reveal behaviors that should have tests but don't?
5. **Regression risk**: Are there areas where changes could break existing functionality without test coverage?

**QA agent produces:**
```yaml
qa_review:
  scenario_coverage: [N]/[total]  # scenarios tested vs total from scenarios.md
  edge_cases_covered: [N]/[total] # from QA perspective document
  test_quality_score: [1-5]       # 5 = thorough, 1 = trivial assertions only
  missing_scenarios: [list]       # scenarios without tests
  recommendations: [list]         # suggested additional test cases
  sign_off: true | false          # QA perspective satisfied?
  concerns: [list]                # if sign_off is false
```

**Integration with composite score:**
QA review score is advisory — it does NOT affect the ratchet keep/discard decision. Instead:
- If `sign_off: false`, add QA concerns to the proof of completion document
- If `missing_scenarios` is non-empty, gaps become backlog items:
  ```bash
  python tools/ratchet.py backlog add "Missing test for scenario: {description}" --type=test_gap --source=qa_review --sprint={sprint_id}
  ```
- QA recommendations appear in the iteration report

### Human Verifiers (human track)

Do NOT run these inline. The execute skill queues them via Python tools:
```bash
python tools/ratchet.py backlog add "Human review: {constraint}" --type=human_review --priority={priority} --sprint={sprint_id} --wp={wp_id}
```

## Result Format

Verify returns results to the execute skill as a structured report. The execute skill handles all recording via Python tools — verify does NOT write to state files or the DB directly.

Return format:
```yaml
wp_id: wp-01
iteration: 3
levels:
  level_1:
    status: pass | fail
    details: [per-check results]
    raw_output: [captured stdout/stderr]
  level_2:
    status: pass | fail
    details: [per-test results]
    raw_output: [captured stdout/stderr]
  level_3:
    status: pass | fail | skipped
    details: [per-check results]
    raw_output: [captured output]
    missing_capability: [if skipped]
  ai_review:
    status: pass | fail | skipped
    details: [per-constraint scores]
  qa_review:
    status: pass | fail | skipped
    details: [qa agent output]
composite_score: 0.85
recommendation: keep | discard
issues: [list of specific issues found]
```

The execute skill then calls:
```bash
python tools/ratchet.py ratchet decide {sprint_id} {wp_id} --score={composite_score}
```

## Constraint Discovery

During verification, if you discover issues NOT covered by any spec constraint, report them to the execute skill which adds them to backlog:

```bash
python tools/ratchet.py backlog add "Discovered: {issue description}" --type=discovered_constraint --source=verification --sprint={sprint_id} --wp={wp_id}
```

## Perspective Acceptance Review (Post-Verification)

After ALL work packages in a sprint pass verification, the execute skill triggers a Perspective Acceptance Review. This is NOT part of per-WP verification — it runs once after the full sprint is verified.

### Purpose
Verification checks the **spec** (narrow constraints). Acceptance review checks the **story** (broad perspectives). An API can pass all invariants while the end-user experience is still poor. Acceptance review catches intent gaps that survived formalization.

### Acceptance Agents
For each active role from `.ratchet/story/roles.yaml`, the execute skill spawns a parallel acceptance agent (Sonnet):

```bash
# Execute skill registers each acceptance agent:
python tools/ratchet.py agent register {sprint_id} acceptance "{role_name} Acceptance" --model sonnet
```

**Input per agent:**
- Original perspective document (`.ratchet/story/perspectives/{role}.md`)
- PM synthesis document (`.ratchet/story/synthesis.md`)
- Proof of completion documents (`.ratchet/{intent}/proofs/`)
- Access to the actual built output (code, running app if applicable)

**Output per agent:** Acceptance review document for that role's perspective.

Gaps found by acceptance agents become backlog items:
```bash
python tools/ratchet.py backlog add "Acceptance gap: {description}" --type=improvement --source=acceptance_review --sprint={sprint_id}
```

### PM Acceptance Summary
After all acceptance agents complete, the execute skill spawns PM agent (Opus) to produce a summary verdict: "ready for human review" or "needs another iteration."

## Rules

1. **Be genuinely critical in ai_review.** Finding real issues early saves iteration cycles.
2. **Run all three levels.** Static → Unit → Integration. Don't stop at unit tests. If Level 3 tools are available, USE them.
3. **Basic functionality = agent responsibility.** Encoding errors, broken buttons, pages not rendering, navigation failures — these are NEVER acceptable as human review items. They must be caught by Level 3 integration tests.
4. **Short-circuit on auto failure.** If any auto level (1/2/3) fails, do NOT run ai_review. Return the failure immediately so the ratchet loop can retry faster.
5. **Auto-trigger on every change.** Verification is not optional or manual. Any code modification triggers the full chain automatically.
6. **Capture raw output.** Every verification result must include the actual output for proof of work.
7. **Never manage state.** Verify returns results. The execute skill handles state, recording, and ratchet decisions via Python tools.
8. **Propose constraints you discover.** Don't silently fix things — report discovered issues so they become backlog items.
9. **QA perspective on final pass.** After all verification passes, run QA perspective review for scenario coverage and test quality assessment. QA review is advisory — it enriches proof of completion but doesn't block the ratchet.
