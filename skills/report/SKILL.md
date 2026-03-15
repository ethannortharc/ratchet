---
name: report
description: Generate iteration reports (after each ratchet round) and project reports (at completion or on demand). Shows optimization trajectory, key decisions, agent discoveries, and actionable insights. Use after iterations complete, at project end, or when user asks "what happened", "show me results", "generate report".
---

# Report — Iteration & Project Reports

## Report Types

### Iteration Report (generated automatically after each round)

Save to `.ratchet/reports/iter-{NNN}.md`:

```markdown
## Iteration Report — [project], Round [N]
Time: [start] → [end] ([duration], [human interventions] human interactions)
Intent Spec version: v[N]
Trigger: [what started this round — initial / human feedback / spec update]

### Progress
| WP | Iterations | Score | Δ | Status |
|----|-----------|-------|---|--------|
| wp-01 (test suite) | 1 | 1.0 | — | ✅ done |
| wp-03 | 4 | 0.72 → 0.95 | +0.23 | ✅ agent pass |
| wp-04 | 3 | 0.60 → 0.88 | +0.28 | ✅ agent pass |
| wp-05 | 5 | 0.45 → 0.70 | +0.25 | ⚠️ budget exhausted |

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
## Project Report — [project]
Total time: [duration] across [N] days
Human total investment: ~[minutes] ([N] interactions)
Intent Spec versions: [N] (v1 → v[N])
Total ratchet iterations: [N]

### Optimization Trajectory
Round 1: composite [X] → Round 2: [Y] → ... → Final: [Z]
[Or if possible, generate a simple ASCII chart]

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
2. Keep iteration reports concise — one page max.
3. Project reports can be longer — they're reference documents.
4. Include reusable insights — these feed the learning loop.
