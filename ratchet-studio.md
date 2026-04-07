# Ratchet Studio — Visual Collaboration Interface

## Vision

Ratchet Studio is the visual frontend for the Ratchet multi-agent collaboration platform. It provides real-time visibility into agent pipelines, backlog management, and project state — all built on top of `ratchet.db`.

```
Ratchet Studio is NOT a separate system.
It is a window into the same DB that Claude Code and the Python tools use.
Read ratchet.db → render visuals. Write ratchet.db → manage backlog.
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│           Ratchet Studio                │
│           (Web Application)             │
│                                         │
│  ┌──────────┐ ┌──────────┐ ┌─────────┐ │
│  │Dashboard │ │Sprint DAG│ │Agent    │ │
│  │          │ │          │ │Detail   │ │
│  └──────────┘ └──────────┘ └─────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌─────────┐ │
│  │Backlog   │ │Regression│ │Timeline │ │
│  │Board     │ │Dashboard │ │         │ │
│  └──────────┘ └──────────┘ └─────────┘ │
└─────────────────┬───────────────────────┘
                  │
          ┌───────▼────────┐
          │ Data Layer     │
          │                │
          │ Read: ratchet.db (SQLite, polling)
          │ Read: .ratchet/ files (content)
          │ Write: ratchet.db (backlog ops)
          └───────┬────────┘
                  │
          ┌───────▼────────┐
          │ .ratchet/      │  ← Shared with Claude Code + Python tools
          │ ratchet.db     │
          │ story/         │
          │ sprints/       │
          │ regression/    │
          └────────────────┘
```

### Tech Stack

```
Frontend: Single-page web app
  → React + TypeScript
  → Tailwind CSS for styling
  → D3.js or dagre-d3 for DAG rendering
  → Recharts for metrics visualization

Backend: Lightweight local server
  → Python (FastAPI) or Node.js
  → Reads ratchet.db directly (SQLite)
  → Reads .ratchet/ files for content
  → WebSocket for real-time updates (polls DB, pushes changes)

Packaging:
  → Option A: Tauri desktop app (lightweight, cross-platform)
  → Option B: Local web server launched via CLI (`ratchet studio`)
  → Option C: VS Code extension webview
```

---

## Views

### View 1: Project Dashboard

The entry point. Shows overall project health and current activity at a glance.

```
┌──────────────────────────────────────────────────────────────┐
│  Ratchet Studio — Task Management API                        │
│  Status: Active │ Mode: Existing │ Created: 2026-04-06       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─ Backlog ─────────────────────────────────────────────┐   │
│  │  Total: 25 items                                      │   │
│  │  ┌────────┬────────┬────────┬────────┐                │   │
│  │  │Must: 8 │Shld:10 │Could:5 │Wont: 2│                │   │
│  │  │████████│████████│████    │██      │                │   │
│  │  └────────┴────────┴────────┴────────┘                │   │
│  │  New: 6 │ In Flight: 5 │ Done: 12 │ Blocked: 2       │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─ Sprints ─────────────────────────────────────────────┐   │
│  │                                                       │   │
│  │  Sprint 1: Core API + Auth           ✓ Done           │   │
│  │  ├── 5/5 WPs │ 12 scenarios │ 3 days                 │   │
│  │                                                       │   │
│  │  Sprint 2: Search + Notifications    ⟳ Executing      │   │
│  │  ├── 2/4 WPs │ wp-03 running (iter 2, score 0.72)    │   │
│  │  ├── [████████░░░░░░░░] 50%                           │   │
│  │  └── ETA: ~2 hours remaining                          │   │
│  │                                                       │   │
│  │  Sprint 3: Polish + Performance      ○ Pending        │   │
│  │  └── 3 must items waiting                             │   │
│  │                                                       │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─ Regression ──────────────────────────────────────────┐   │
│  │  Scenarios: 15/22 tested │ Last run: all pass ✓       │   │
│  │  [████████████████░░░░░░] 68%                         │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─ Recent Activity ─────────────────────────────────────┐   │
│  │  14:32  wp-03 verified, score 0.72 → DISCARD          │   │
│  │  14:31  wp-03 executed, iteration 2                   │   │
│  │  14:30  regression: 15/15 pass ✓                      │   │
│  │  14:29  wp-02 verified, score 0.95 → KEEP ✓           │   │
│  │  14:28  backlog B-018 created (unresolved)            │   │
│  │  14:25  wp-02 executed, iteration 1                   │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Data sources:**
```sql
-- Backlog stats
SELECT priority, COUNT(*) FROM backlog WHERE status != 'wont_do' GROUP BY priority;
SELECT status, COUNT(*) FROM backlog GROUP BY status;

-- Sprint list
SELECT * FROM sprints ORDER BY id;

-- Current sprint progress
SELECT id, name, status, best_score, iteration FROM work_packages WHERE sprint_id = 'sprint-2';

-- Regression
SELECT COUNT(*) as total, SUM(CASE WHEN last_result='pass' THEN 1 ELSE 0 END) as passing 
FROM regression_tests;

-- Recent activity
SELECT * FROM agent_activity ORDER BY timestamp DESC LIMIT 20;
```

---

### View 2: Sprint Pipeline DAG

Interactive DAG visualization of a sprint's agent pipeline. Click any node to drill down.

```
┌──────────────────────────────────────────────────────────────┐
│  Sprint 2: Search + Notifications — Pipeline                 │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                                                         │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐                │ │
│  │  │End User  │ │Developer │ │QA Tester │                │ │
│  │  │ ✓ done   │ │ ✓ done   │ │ ✓ done   │                │ │
│  │  │ 42s      │ │ 38s      │ │ 35s      │                │ │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘                │ │
│  │       └─────────────┼───────────┘                       │ │
│  │                     ▼                                   │ │
│  │              ┌──────────┐                               │ │
│  │              │PM Synth  │                               │ │
│  │              │ ✓ done   │                               │ │
│  │              │ 1m 23s   │                               │ │
│  │              └────┬─────┘                               │ │
│  │                   │                                     │ │
│  │         ┌─────────┼─────────┐                           │ │
│  │         ▼                   ▼                           │ │
│  │  ┌──────────┐        ┌──────────┐                       │ │
│  │  │Env Prep  │        │Test Gen  │                       │ │
│  │  │ ✓ done   │        │ ✓ done   │                       │ │
│  │  └────┬─────┘        └────┬─────┘                       │ │
│  │       └──────────┬────────┘                             │ │
│  │                  ▼                                      │ │
│  │           ┌──────────┐                                  │ │
│  │           │   EVA    │                                  │ │
│  │           │ ✓ done   │                                  │ │
│  │           └────┬─────┘                                  │ │
│  │                ▼                                        │ │
│  │           ┌──────────┐                                  │ │
│  │           │ Planning │                                  │ │
│  │           │ ✓ done   │                                  │ │
│  │           └────┬─────┘                                  │ │
│  │                │                                        │ │
│  │    ┌───────────┼───────────┬───────────┐                │ │
│  │    ▼           ▼           ▼           ▼                │ │
│  │ ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐             │ │
│  │ │WP-01 │   │WP-02 │   │WP-03 │   │WP-04 │             │ │
│  │ │✓ done│   │✓ done│   │🔄 run│   │⏳ wait│             │ │
│  │ │3 iter│   │1 iter│   │iter 2│   │      │             │ │
│  │ │s:0.95│   │s:0.98│   │s:0.72│   │      │             │ │
│  │ └──┬───┘   └──┬───┘   └──┬───┘   └──────┘             │ │
│  │    ▼          ▼          ▼                              │ │
│  │ ┌──────┐   ┌──────┐   ┌──────┐                         │ │
│  │ │V:✓   │   │V:✓   │   │V:🔄  │  ← click to drill down │ │
│  │ └──────┘   └──────┘   └──────┘                         │ │
│  │                                                         │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  Legend: ✓ done │ 🔄 running │ ⏳ pending │ ✗ failed        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**DAG rendering:**
```sql
-- Nodes
SELECT id, agent_name, status, current_activity, progress, 
       duration_ms, group_id, model
FROM agent_nodes WHERE sprint_id = 'sprint-2';

-- Edges
SELECT from_agent, to_agent, edge_type, data_flow
FROM agent_edges 
WHERE from_agent IN (SELECT id FROM agent_nodes WHERE sprint_id = 'sprint-2');
```

**Interactions:**
- Click node → opens Agent Detail view
- Hover node → shows current_activity tooltip
- Color coding: green=done, blue=running, gray=pending, red=failed
- Animated edges show data flow direction
- Parallel groups shown side-by-side
- Running nodes pulse/glow

---

### View 3: Agent Detail (Drill-Down)

Detailed view of a single agent's work. Real-time activity stream + full work log.

```
┌──────────────────────────────────────────────────────────────┐
│  ← Back to DAG                                               │
│                                                              │
│  WP-03 Executor                                              │
│  Sprint 2 │ Model: sonnet │ Status: running                  │
│  Iteration: 2/8 │ Best Score: 0.72 │ Running: 3m 42s        │
│                                                              │
│  Current Activity: "Fixing pagination edge case"              │
│  Progress: "3/5 tests passing"                               │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─ Activity Stream (live) ──────────────────────────────┐   │
│  │                                                       │   │
│  │  14:32:05  writing_file   src/api/tasks.ts            │   │
│  │  14:31:50  running_test   pagination.test.ts          │   │
│  │            → 3/5 PASS, 2 FAIL                         │   │
│  │            ✓ basic pagination                         │   │
│  │            ✓ empty result set                         │   │
│  │            ✓ first page                               │   │
│  │            ✗ last page offset > count                  │   │
│  │            ✗ negative offset                          │   │
│  │  14:31:30  reading_file   spec.yaml (INV-05)          │   │
│  │  14:31:15  analyzing      "Previous iteration failed  │   │
│  │                            on offset > total_count"   │   │
│  │  14:31:00  started        Iteration 2                 │   │
│  │                                                       │   │
│  │  ── Iteration 1 ──────────────────────────────        │   │
│  │  14:28:00  started        Iteration 1                 │   │
│  │  14:28:45  running_test   → 2/5 PASS                  │   │
│  │  14:29:20  running_test   → 3/5 PASS (improved)       │   │
│  │  14:29:50  completed      Score: 0.60 → DISCARD       │   │
│  │                                                       │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─ Files Modified ─────────────────────────────────────┐    │
│  │  src/api/tasks.ts          +12 -3  (this iteration)  │    │
│  │  src/utils/pagination.ts   +25     (new file)        │    │
│  │  test/pagination.test.ts   +8  -2  (test fixes)      │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─ Score History ──────────────────────────────────────┐    │
│  │  Iter 1: 0.60 (DISCARD)                              │    │
│  │  Iter 2: 0.72 (KEEP) ← current best                  │    │
│  │  Iter 3: ... (running)                                │    │
│  │                                                       │    │
│  │  Score Chart:                                         │    │
│  │  1.0 ┤                                                │    │
│  │  0.8 ┤          ╭──                                   │    │
│  │  0.6 ┤    ╭─────╯                                     │    │
│  │  0.4 ┤────╯                                           │    │
│  │  0.0 ┼────┬────┬────                                  │    │
│  │       1    2    3                                      │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  [View Full Log] [View Proof] [View Spec Constraints]        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Data sources:**
```sql
-- Agent info
SELECT * FROM agent_nodes WHERE id = 'sprint-2:wp-03-exec';

-- Activity stream (live, polling)
SELECT timestamp, activity_type, detail, file_path
FROM agent_activity 
WHERE agent_node_id = 'sprint-2:wp-03-exec'
ORDER BY timestamp DESC;

-- Score history
SELECT iteration, best_score FROM work_packages 
WHERE id = 'wp-03' AND sprint_id = 'sprint-2';

-- Full log file
-- Read: .ratchet/sprints/sprint-2/agent-logs/wp-03-executor.md
```

---

### View 4: Backlog Board

Kanban-style backlog management. Drag-and-drop priority, inline editing.

```
┌──────────────────────────────────────────────────────────────┐
│  Backlog — Task Management API                               │
│  [+ Add Item]  [Filter: All ▼]  [Group: Priority ▼]         │
│                                                              │
│  ┌─ Must (8) ──────┬─ Should (10) ────┬─ Could (5) ────┐   │
│  │                 │                  │                 │   │
│  │ B-001 ✓        │ B-004 ✓         │ B-011           │   │
│  │ User auth      │ Search results  │ Dark mode       │   │
│  │ Sprint 1       │ Sprint 2        │                 │   │
│  │                 │                  │ B-013           │   │
│  │ B-002 ✓        │ B-006 ⟳         │ Export to CSV   │   │
│  │ CRUD API       │ Email notify    │                 │   │
│  │ Sprint 1       │ Sprint 2        │ B-015           │   │
│  │                 │                  │ API versioning  │   │
│  │ B-012 ★        │ B-014 ○         │                 │   │
│  │ Login CSS bug  │ API pagination  │                 │   │
│  │ type: bug      │ from: accept    │                 │   │
│  │                 │ role: developer │                 │   │
│  │ B-018 ⚠        │                  │                 │   │
│  │ Sort algorithm │ B-019 ○         │                 │   │
│  │ type: unresolvd│ Missing tests   │                 │   │
│  │ needs decision │ from: qa_review │                 │   │
│  │                 │                  │                 │   │
│  └─────────────────┴──────────────────┴─────────────────┘   │
│                                                              │
│  Legend: ✓ done │ ⟳ executing │ ○ new │ ★ bug │ ⚠ unresolvd │
│                                                              │
│  ── Item Detail (click to expand) ──────────────────────     │
│  B-018: Sort algorithm choice                                │
│  Type: unresolved │ Source: execution (Sprint 2, wp-03)      │
│  Description: "Agent couldn't decide: sort by due date       │
│  or by importance. Used due date as best-effort."            │
│  [Confirm Due Date] [Choose Importance] [Discuss]            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Data sources:**
```sql
-- All backlog items
SELECT * FROM backlog WHERE status != 'wont_do' ORDER BY priority, created_at;

-- With sprint info
SELECT b.*, s.name as sprint_name 
FROM backlog b LEFT JOIN sprints s ON b.planned_sprint = s.id;
```

**Interactions:**
- Drag items between priority columns
- Click item to expand detail
- Inline edit title, description, priority
- "Confirm" button for unresolved items → writes decision to DB
- "+ Add Item" → creates backlog entry
- Filter by: type, source, sprint, role

---

### View 5: Regression Dashboard

Global test health across all sprints.

```
┌──────────────────────────────────────────────────────────────┐
│  Regression Dashboard                                        │
│                                                              │
│  Overall: 15/22 scenarios tested │ All passing ✓             │
│  [████████████████████░░░░░░░░] 68%                          │
│                                                              │
│  ┌─ By Sprint ──────────────────────────────────────────┐    │
│  │                                                      │    │
│  │  Sprint 1: 8 scenarios registered                    │    │
│  │  S-01 ✓ User creates task              (end_user)    │    │
│  │  S-02 ✓ Task due notification          (end_user)    │    │
│  │  S-03 ✓ Delete task confirmed          (end_user)    │    │
│  │  S-04 ✓ JWT auth required              (security)    │    │
│  │  S-05 ✓ Rate limiting works            (security)    │    │
│  │  S-06 ✓ Invalid input rejected         (qa_tester)   │    │
│  │  S-07 ✓ Health check endpoint          (devops)      │    │
│  │  S-08 ✓ Graceful shutdown              (devops)      │    │
│  │                                                      │    │
│  │  Sprint 2: 7 scenarios registered                    │    │
│  │  S-09 ✓ Search returns results         (end_user)    │    │
│  │  S-10 ✓ Search pagination              (developer)   │    │
│  │  S-11 ✓ Email notification sent        (end_user)    │    │
│  │  S-12 ✓ Notification preferences       (end_user)    │    │
│  │  S-13 ✓ Search indexing performance    (devops)      │    │
│  │  S-14 ✓ Concurrent search requests     (qa_tester)   │    │
│  │  S-15 ✓ Search SQL injection blocked   (security)    │    │
│  │                                                      │    │
│  │  Not Yet Tested (pending sprints): 7 scenarios       │    │
│  │  S-16 ○ Export tasks to CSV            (end_user)    │    │
│  │  S-17 ○ Bulk operations                (developer)   │    │
│  │  ...                                                 │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─ Run History ────────────────────────────────────────┐    │
│  │  Apr 6 14:30  15/15 ✓  (after wp-02, Sprint 2)      │    │
│  │  Apr 6 14:00  15/15 ✓  (after wp-01, Sprint 2)      │    │
│  │  Apr 6 11:00  8/8  ✓  (Sprint 2 start baseline)     │    │
│  │  Apr 5 18:00  8/8  ✓  (Sprint 1 completion)         │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  [Run Regression Now]                                        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Data sources:**
```sql
SELECT rt.*, s.name as sprint_name
FROM regression_tests rt
LEFT JOIN sprints s ON rt.source_sprint = s.id
ORDER BY rt.scenario_id;
```

---

### View 6: Timeline

Chronological view of all project events. Useful for understanding what happened and when.

```
┌──────────────────────────────────────────────────────────────┐
│  Project Timeline                                            │
│  [Filter: All ▼] [Sprint: All ▼] [Agent: All ▼]             │
│                                                              │
│  Apr 6, 2026                                                 │
│  ─────────────────────────────────────────────               │
│                                                              │
│  14:32  Sprint 2 │ wp-03 │ verifier                          │
│         Score: 0.72 → DISCARD (no improvement)               │
│                                                              │
│  14:31  Sprint 2 │ wp-03 │ wp-executor                       │
│         Iteration 2 completed                                │
│         Files: src/api/tasks.ts, src/utils/pagination.ts     │
│                                                              │
│  14:30  Sprint 2 │ system                                    │
│         Regression: 15/15 pass ✓                             │
│                                                              │
│  14:29  Sprint 2 │ wp-02 │ verifier                          │
│         Score: 0.95 → KEEP ✓ (committed)                     │
│                                                              │
│  14:28  Sprint 2 │ wp-03 │ wp-executor                       │
│         Backlog item created: B-018 (unresolved)             │
│         "Sort algorithm needs user decision"                 │
│                                                              │
│  14:25  Sprint 2 │ wp-02 │ wp-executor                       │
│         Iteration 1 started                                  │
│                                                              │
│  ...                                                         │
│                                                              │
│  11:00  Sprint 2 │ system                                    │
│         Sprint 2 started. 4 WPs planned. 23 story points.   │
│                                                              │
│  Apr 5, 2026                                                 │
│  ─────────────────────────────────────────────               │
│                                                              │
│  18:00  Sprint 1 │ system                                    │
│         Sprint 1 completed. 5/5 WPs done. All tests pass.   │
│         Acceptance: PM verdict = ready for review            │
│                                                              │
│  ...                                                         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Data sources:**
```sql
SELECT a.timestamp, a.activity_type, a.detail, a.file_path,
       n.sprint_id, n.agent_name, n.agent_type
FROM agent_activity a
JOIN agent_nodes n ON a.agent_node_id = n.id
ORDER BY a.timestamp DESC;
```

---

## Data Layer

### Polling Strategy

```
Dashboard:     Poll every 5 seconds (lightweight queries)
Sprint DAG:    Poll every 2 seconds (when sprint executing)
Agent Detail:  Poll every 1 second (real-time feel)
Backlog:       Poll every 10 seconds (rarely changes during sprint)
Regression:    Poll on demand (manual refresh)
Timeline:      Poll every 3 seconds
```

### WebSocket (optional upgrade)

```
Python backend watches ratchet.db for changes (using SQLite triggers or polling).
Pushes events to frontend via WebSocket.

Events:
  agent_status_changed: { agent_id, old_status, new_status }
  wp_score_updated: { wp_id, score, decision: keep|discard }
  backlog_item_created: { item_id, type, title }
  sprint_step_completed: { sprint_id, step_name }
  regression_completed: { passed, failed, total }
```

### File Content Access

Some views need to display file content (proofs, agent logs, specs):

```
Backend endpoint: GET /files/{path}
  → Reads from .ratchet/{path}
  → Returns content with appropriate content-type
  → Markdown rendered to HTML for display

Examples:
  GET /files/sprints/sprint-2/proofs/wp-01.md
  GET /files/sprints/sprint-2/agent-logs/wp-03-executor.md
  GET /files/story/synthesis/initial.md
  GET /files/sprints/sprint-2/spec.yaml
```

---

## Implementation Phases

### Phase 1: Core Dashboard + Backlog

```
Priority: Highest — provides immediate value without DAG

Features:
  - Project dashboard (status, sprint list, basic stats)
  - Backlog board (CRUD, drag-and-drop priority)
  - Recent activity feed
  - Sprint progress bars
  
Data: Basic queries on project, sprints, backlog, work_packages tables
Tech: React + Tailwind + SQLite reader
```

### Phase 2: Sprint DAG Visualization

```
Priority: High — the signature feature

Features:
  - Interactive DAG rendering (dagre-d3 or similar)
  - Real-time status updates (node colors, progress)
  - Parallel group visualization
  - Click-to-drill-down navigation
  - Animated data flow edges
  
Data: agent_nodes + agent_edges tables
Tech: D3.js / dagre-d3 for graph layout
```

### Phase 3: Agent Detail + Drill-Down

```
Priority: High — essential for debugging and monitoring

Features:
  - Real-time activity stream
  - Score history chart
  - File diff viewer
  - Full work log viewer (Markdown rendered)
  - Link to proof documents
  
Data: agent_activity table + agent log .md files
Tech: Recharts for score chart, Markdown renderer
```

### Phase 4: Regression Dashboard

```
Priority: Medium — valuable for quality tracking

Features:
  - Scenario coverage map
  - Run history
  - Per-sprint breakdown
  - Manual run trigger
  
Data: regression_tests table
```

### Phase 5: Timeline

```
Priority: Medium — useful for retrospectives

Features:
  - Chronological event view
  - Filterable by sprint, agent, event type
  - Expandable event details
  
Data: agent_activity + audit_log tables
```

### Phase 6: Advanced Features

```
Priority: Lower — nice-to-have

Features:
  - Story artifacts viewer (perspectives, synthesis, journey)
  - Spec constraint explorer
  - Acceptance review comparison (expected vs actual per role)
  - Metrics trends across sprints
  - Project comparison (multiple projects)
  - Dark mode
```

---

## API Endpoints (for Studio Backend)

```
# === Project ===
GET  /api/project                     # Project info + stats
GET  /api/project/status              # Quick status check

# === Backlog ===
GET  /api/backlog                     # All items (with filters)
POST /api/backlog                     # Create item
PUT  /api/backlog/{id}                # Update item
GET  /api/backlog/stats               # Counts by status/priority/type

# === Sprints ===
GET  /api/sprints                     # All sprints
GET  /api/sprints/{id}                # Sprint detail
GET  /api/sprints/{id}/dag            # Agent DAG for sprint
GET  /api/sprints/{id}/work-packages  # WP list with status

# === Agents ===
GET  /api/agents?sprint={id}          # Agents for sprint
GET  /api/agents/{id}                 # Agent detail
GET  /api/agents/{id}/activity        # Activity stream (supports ?since=timestamp for polling)
GET  /api/agents/{id}/log             # Full work log (file content)

# === Regression ===
GET  /api/regression                  # Test list + results
GET  /api/regression/history          # Run history
POST /api/regression/run              # Trigger run

# === Events ===
GET  /api/events                      # Timeline (with filters)
GET  /api/events?since={timestamp}    # New events since (for polling)

# === Files ===
GET  /api/files/{path}                # Read any .ratchet/ file

# === WebSocket ===
WS   /ws/events                       # Real-time event stream
```

---

## Relationship to ratchet-cli

```
Ratchet Studio does NOT duplicate ratchet-cli logic.

Studio reads DB → visualizes.
Studio writes DB → only for backlog management (add, update priority).
All process management → ratchet-cli.
All agent execution → Claude Code.

Studio is a VIEWER + BACKLOG EDITOR, not an orchestrator.
```

---

## Packaging Options

### Option A: Local Web Server (recommended for v1)

```bash
# Start studio
$ ratchet studio
# → Starts FastAPI server on localhost:3000
# → Opens browser automatically
# → Reads .ratchet/ratchet.db from current directory
```

Bundled with ratchet-cli. No separate installation.

### Option B: Tauri Desktop App (future)

```
Cross-platform native app.
Embeds SQLite reader directly.
No server needed.
Better performance for real-time updates.
```

### Option C: VS Code Extension (future)

```
Webview panel inside VS Code.
Same codebase as web app.
Integrated with editor workflow.
```
