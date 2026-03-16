---
name: status
description: Display multi-intent dashboard with lifecycle state, WP progress, metrics, pending reviews, blockers, and suggested next actions. Folds in metrics display. Accepts optional intent ID for detailed view.
---

# Status — Multi-Intent Dashboard

## Workspace Resolution

1. If intent ID provided → detailed view for that intent
2. If in registered workspace → expand that intent, summarize others
3. Otherwise → overview of all intents

## Display

### Overview

```
🔧 Ratchet — [N] intents

🔄 prism [software/web_app] agent_running     normal
   "Static site for personality tests, Enneagram"
   Progress: 4/6 WPs │ wp-05 iter 3 score 0.85
   Metrics: 82% auto coverage │ 2.7 avg iterations
   Tags: frontend, chinese, mvp

⏸ novel [creative_writing] paused
   "Historical fiction, 1920s Shanghai"
   ⚠️ Blocker: human review for QD-02
   Metrics: 45% auto coverage │ 3.1 avg iterations

✅ note-cli [software/cli] done
   Completed 2h ago │ Autonomy: 91%

📊 Summary:
   Pending reviews: 3 (1 blocking)
   Avg auto coverage: 72%

💡 → /ratchet:review to process blocking review for "novel"
```

### Detailed View (single intent)

```
📦 prism [software/web_app] 🔄 agent_running

   Spec v2 │ Created: 2026-03-14 │ Last: 5 min ago
   Workspace: /Users/coder/projects/prism
   Tags: frontend, chinese, mvp

   📋 Constraints: 7 INV + 4 QD = 11 total
      Agent: 9 (auto: 6, ai_review: 3) │ Human: 2

   📦 Work Packages:
      ✅ wp-00  Environment prep          done
      ✅ wp-01  Core quiz component        done (3 iter)
      ✅ wp-02  Scoring engine             done (2 iter)
      🔄 wp-03  Results display            iter 3, score 0.85
      ⬜ wp-04  Responsive layout          pending
      ⬜ wp-05  Polish                     pending

   📊 Metrics:
      ⏱  Elapsed: 1h 20m │ Agent autonomous: 1h 15m (94%)
      ✅ Auto coverage: 82% │ First-pass: 60%
      🔄 Total iterations: 8 │ Avg per WP: 2.7
      💡 2 constraints converted human→agent

   Reviews: 1 pending (QD-02) │ Suggestions: 2

   💡 wp-03 should pass in ~1 iteration
```

## Rules
1. Always show blockers and pending reviews prominently.
2. Include metrics inline — no separate /ratchet:metrics needed.
3. Hide archived intents unless asked.
