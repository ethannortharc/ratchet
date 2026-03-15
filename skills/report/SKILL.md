---
name: report
description: Generate iteration reports (after each ratchet round) and project reports (at completion or on demand). Includes proof of work — raw verification outputs, not just pass/fail summaries. Workspace-aware, accepts optional intent ID.
---

# Report — Iteration & Project Reports

## Workspace Resolution

1. If intent ID provided → use that intent's workspace
2. If current directory is inside a registered workspace → use that intent
3. If ambiguous → ask user to choose

## Report Types

### Iteration Report (generated automatically after each round)

Save to `.ratchet/reports/iter-{NNN}.md`:

```markdown
## Iteration Report — [intent-id], Round [N]
Intent: [name] │ Workspace: [path]
Time: [start] → [end] ([duration], [human interventions] human interactions)
Intent Spec version: v[N]
Trigger: [what started this round — initial / human feedback / spec update]

### Progress
| WP | Iterations | Score | Δ | Status |
|----|-----------|-------|---|--------|
| wp-03 | 4 | 0.72 → 0.95 | +0.23 | ✅ agent pass |
| wp-04 | 3 | 0.60 → 0.88 | +0.28 | ✅ agent pass |
| wp-05 | 5 | 0.45 → 0.70 | +0.25 | ⚠️ budget exhausted |

### Proof of Work

#### Auto Verifications
- INV-01 (builds): ✅ `npm run build` exit code 0
  ```
  Build output: 47 modules, 0 errors, 0 warnings
  Bundle size: 142KB gzipped
  ```
- INV-03 (scoring): ✅ 12/12 test cases passed
  ```
  PASS src/scoring.test.ts (0.8s)
    ✓ type 1 full score → primary type 1
    ✓ tie between type 2 and 3 → alphabetical tiebreak
    ...
  ```

#### AI Reviews
- QD-01 (description quality): ai_review score 4.2/5
  ```
  Type 1 description is accurate and specific.
  Type 5 description could use more behavioral examples.
  ```

#### Human Review Items (pending)
- QD-02 (visual design): screenshot at .ratchet/artifacts/screenshots/results-page.png
- INV-07 (usability): test instructions at .ratchet/test-suite/INV-07.checklist.md

### Key Decisions by Agent
- wp-03 iter 2: Switched from LIKE to FTS5, 10x perf improvement
- wp-04 iter 3: Refactored tag storage from flat to hierarchical

### Constraints Discovered
- [sug-001]: SQLite WAL mode needed [pending human review]

### Blocking Items
- wp-05: Markdown export format validation failing, needs direction

### Agent Track Summary
  Passed: [N]/[total] | Best composite: [score]

### Human Track Queue
  New items queued: [N]
  Items still pending from previous rounds: [N]
```

### Project Report (generated on completion or `/ratchet:report`)

Save to `.ratchet/reports/final.md`:

```markdown
## Project Report — [intent-id]
Intent: [name] │ Workspace: [path]
Total time: [duration] across [N] days
Human total investment: ~[minutes] ([N] interactions)
Intent Spec versions: [N] (v1 → v[N])
Total ratchet iterations: [N]

### Optimization Trajectory
Round 1: composite [X] → Round 2: [Y] → ... → Final: [Z]
[ASCII chart if possible]

### Complete Proof of Work
[All auto verification outputs from final passing round]
[All ai_review scores with justifications]
[Human review outcomes]

### Intent Spec Evolution
v1 → v2: [change + trigger]
v2 → v3: [change + trigger]
Source breakdown: [N] from human, [N] from agent suggestions, [N] from review feedback

### Verification Summary
Agent track: [N] constraints, [N] passed
Human track: [N] constraints, [N] passed
Constraints converted from human→agent during project: [N]

### Reusable Insights
- [insight applicable to future projects]
- [insight applicable to future projects]
→ These can be added to profile or inquiry protocols

### Metrics
Autonomy ratio: [agent time / total time]
First-pass rate: [constraints passing on first try]
Avg iterations to pass: [N]
```

## Rules
1. Always generate iteration report automatically — don't wait for user to ask.
2. **Include proof of work** — raw outputs, not just pass/fail counts.
3. Keep iteration reports concise — one page max (truncate raw output if needed, keep key lines).
4. Project reports can be longer — they're reference documents.
5. Include reusable insights — these feed the learning loop.
6. Include intent ID and workspace path in report headers.
