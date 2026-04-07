---
name: report
description: Generate human-readable reports from DB data and file content. Combines verification events, proofs, and acceptance results into iteration and project reports.
---

# Report — Sprint & Project Reports

## Data Sources

- Verification events: `python tools/ratchet.py events --sprint={sprint_id}`
- Proof documents: `.ratchet/sprints/{sprint}/proofs/`
- Acceptance results: `.ratchet/sprints/{sprint}/acceptance/`
- Sprint status: `python tools/ratchet.py sprint status {sprint_id}`

## Report Types

### Sprint Report

Gather data from DB and files, then generate `.ratchet/sprints/{sprint}/report.md`:

```markdown
## Sprint Report — Sprint {id}
Time: [start] -> [end] ([duration])

### Progress
| WP | Iterations | Score | Status |
|----|-----------|-------|--------|
| wp-01 | 3 | 0.95 | pass |
| wp-02 | 5 | 0.70 | budget exhausted |

### Proof of Work
[Read from .ratchet/sprints/{sprint}/proofs/ — include raw verification outputs]

### Acceptance Review
[Read from .ratchet/sprints/{sprint}/acceptance/summary.md]

### Key Events
[From python tools/ratchet.py events --sprint={sprint_id}]
```

### Project Report (on demand)

Aggregate across all sprints:

```markdown
## Project Report
Total sprints: [N]
Total time: [duration]

### Sprint History
[Summary of each sprint's outcomes]

### Backlog Status
[From python tools/ratchet.py backlog stats]

### Regression Status
[From python tools/ratchet.py regression status]
```

## Rules

1. **Include proof of work** — raw outputs, not just pass/fail counts.
2. Keep sprint reports concise — one page max (truncate raw output if needed, keep key lines).
3. Project reports can be longer — they're reference documents.
4. Always read actual file content from proofs/ and acceptance/ directories.
