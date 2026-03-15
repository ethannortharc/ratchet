---
name: status
description: Display multi-intent dashboard showing all Ratchet intents with lifecycle state, progress, pending reviews, blockers, and suggested next actions. Accepts optional intent ID for detailed view. Works from any directory using global state registry.
---

# Status — Multi-Intent Dashboard

## Workspace Resolution

1. If intent ID provided → show detailed view for that intent
2. If current directory is inside a registered workspace → show that intent expanded, others summarized
3. If no intent ID and not in workspace → show all intents overview

## Workflow

1. Read `~/.config/ratchet/state.yaml` for intent registry
2. For each active intent, read `.ratchet/` state files from its workspace
3. Read `~/.config/ratchet/review_queue.yaml` for pending reviews

## Display

### Overview (all intents)

```
🔧 Ratchet — [N] intents

📦 prism [software] ● agent_running     priority: normal
   "Static site for personality tests, starting with Enneagram"
   Workspace: /Users/coder/projects/prism
   Progress: 4/6 WPs complete (test suite ✅)
   Current: wp-05 iter 3, score 0.72 → 0.85
   Tags: frontend, chinese, mvp

📖 novel [creative_writing] ⏸ paused
   "Historical fiction novel set in 1920s Shanghai"
   Workspace: /Users/coder/projects/novel
   Progress: outline done, ch1-3 written
   ⚠️ Blocker: human review needed for QD-02

✅ note-cli [software] ● done
   Workspace: /Users/coder/projects/note-cli
   Completed: 2h ago, all constraints passed

📊 Summary:
   Pending reviews: 3 (1 blocking)
   Auto-verification coverage: 82% avg

💡 Suggested next action:
   → /ratchet:review to process 1 blocking review for "novel"
```

### Detailed View (single intent)

When intent ID is provided or user is in a workspace:

```
📦 prism [software] ● agent_running

   Intent Spec v2 │ Created: 2026-03-14 │ Last activity: 5 min ago
   Workspace: /Users/coder/projects/prism
   Tags: frontend, chinese, mvp
   Priority: normal

   📋 Constraints: 7 invariants, 4 quality dimensions
      Agent track: 9 (auto: 6, ai_review: 3)
      Human track: 2

   📦 Work Packages:
      ✅ wp-00  Environment prep          done
      ✅ wp-01  Core quiz component        done (3 iterations)
      ✅ wp-02  Scoring engine             done (2 iterations)
      🔄 wp-03  Results display            iter 3, score 0.85
      ⬜ wp-04  Responsive layout          pending
      ⬜ wp-05  Polish & accessibility     pending

   📊 Ratchet: 8 total iterations, avg 2.7 per WP
   🎯 Verification: 85% auto coverage

   Pending reviews: 1 (QD-02: visual design)
   Suggestions: 2 agent-proposed constraints

   💡 Next: wp-03 should complete in ~2 iterations
```

## Lifecycle State Icons

| State | Icon | Color hint |
|-------|------|------------|
| draft | 📝 | gray |
| active | 📋 | blue |
| agent_running | 🔄 | green |
| agent_complete | ✅ | green |
| human_review | 👤 | yellow |
| done | ✅ | green |
| paused | ⏸ | gray |
| archived | 📦 | gray |

## Rules
1. Always show pending review count prominently — human attention is the bottleneck.
2. Show blocking reviews and `current_blocker` as highest priority action.
3. Show intent ID, workspace path, and lifecycle state for every intent.
4. If in a registered workspace, auto-expand that intent's details.
5. Hide archived intents unless explicitly asked.
