---
name: status
description: Display multi-project dashboard showing all active Ratchet projects, their progress, pending reviews, and suggested next actions. Works from any directory by reading the global state file. Use when asking "what's going on", "show progress", "status", or when resuming work.
---

# Status — Multi-Project Dashboard

## Workflow

1. Read `~/.config/ratchet/state.yaml` for project index
2. For each active project, read `.ratchet/` state files
3. Read `~/.config/ratchet/review_queue.yaml` for pending reviews

## Display

```
🔧 Ratchet — [N] active projects

📦 project-a [software] — agent running
   Progress: 4/6 WPs complete (test suite ✅)
   Current: wp-05 iter 3, score 0.72 → 0.85
   Estimated: ~40 min remaining

📖 project-b [creative_writing] — awaiting review
   Progress: settings + outline done, writing ch1-5
   Pending: 2 human reviews (1 blocking)

✅ project-c [research] — completed
   Completed: 2h ago, all constraints passed

📊 Summary:
   Pending reviews: 3 (1 high priority)
   Auto-verification coverage: 82% avg

💡 Suggested next action:
   → /ratchet:review to process 1 blocking review
```

## Rules
1. Always show pending review count prominently — human attention is the bottleneck.
2. Show blocking reviews as highest priority action.
3. If in a project directory with `.ratchet/`, show that project's details expanded.
