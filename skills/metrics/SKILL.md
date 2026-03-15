---
name: metrics
description: Track and display human interaction count, automation time, verification coverage, and ratchet effectiveness. Shows per-project and cross-project trends. Use when user asks "how efficient was this", "how many times did I intervene", "show metrics", or for retrospective analysis.
---

# Metrics — Interaction & Automation Tracking

## Key Metrics

### Per-Project
- **Human interactions**: Total times user provided input (across all phases)
- **Autonomy ratio**: agent autonomous time / total elapsed time
- **Auto-verification coverage**: agent-track constraints / total constraints
- **First-pass rate**: constraints passing on first ratchet iteration
- **Avg iterations to pass**: mean ratchet cycles before agent-track pass
- **Human→agent conversions**: constraints converted from human to agent track via feedback
- **Ratchet effectiveness**: improvement per iteration (composite score delta)

### Cross-Project (stored in `~/.config/ratchet/global_metrics.yaml`)
- Trends in autonomy ratio across projects
- Most common failure reasons
- Average human investment per project type
- Tools that would most improve automation

## Display

```
📊 Metrics for [project]

⏱  Time: [total] elapsed, [agent time] autonomous ([X]%)
🤝 Human: [N] interactions ([breakdown by phase])
✅ Verification: [N]% auto coverage, [N]% first-pass rate
🔄 Ratchet: [N] total iterations, avg [X] per WP
📈 Score trajectory: [start] → [current] (+[delta])
💡 [N] constraints converted from human→agent track

/metrics --global  for cross-project trends
```

## Recording
Other skills append to `.ratchet/metrics.yaml` at phase completion. This skill reads and presents, also calculates derived metrics and generates suggestions.
