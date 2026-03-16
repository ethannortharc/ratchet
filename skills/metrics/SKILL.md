---
name: metrics
description: Track and display human interaction count, automation time, verification coverage, and ratchet effectiveness. Shows per-intent and cross-intent trends. Workspace-aware — accepts optional intent ID.
---

# Metrics — Interaction & Automation Tracking

## Workspace Resolution

1. If intent ID provided → show metrics for that intent
2. If current directory is inside a registered workspace → show that intent's metrics
3. If no intent specified → show cross-intent trends

## Key Metrics

### Per-Intent
- **Human interactions**: Total times user provided input (across all phases)
- **Autonomy ratio**: agent autonomous time / total elapsed time
- **Auto-verification coverage**: agent-track constraints / total constraints
- **First-pass rate**: constraints passing on first ratchet iteration
- **Avg iterations to pass**: mean ratchet cycles before agent-track pass
- **Human→agent conversions**: constraints converted from human to agent track via feedback
- **Ratchet effectiveness**: improvement per iteration (composite score delta)

### Cross-Intent (stored in `~/.config/ratchet/global_metrics.yaml`)
- Trends in autonomy ratio across intents
- Most common failure reasons
- Average human investment by project type
- Tools that would most improve automation

## Display

```
📊 Metrics for [intent-id] ([name])
   Workspace: [path]

⏱  Time: [total] elapsed, [agent time] autonomous ([X]%)
🤝 Human: [N] interactions ([breakdown by phase])
✅ Verification: [N]% auto coverage, [N]% first-pass rate
🔄 Ratchet: [N] total iterations, avg [X] per WP
📈 Score trajectory: [start] → [current] (+[delta])
💡 [N] constraints converted from human→agent track

/ratchet:metrics --global  for cross-intent trends
```

## Recording
Other skills append to `.ratchet/{intent-id}/metrics.yaml` at phase completion. This skill reads and presents, also calculates derived metrics and generates suggestions.
