# Ratchet Plugin — Change Specification v6

Read DESIGN.md, ratchet-changes-v4.md, and ratchet-changes-v5.md first.
This document covers the architectural transformation from "LLM manages process" to "code manages process, LLM does creative work." Based on real usage insight: **LLMs are probabilistic; process consistency requires deterministic code.**

---

## Summary

The core insight: **SKILL.md files are natural language instructions that LLMs follow probabilistically. The more complex the process, the more steps get skipped.** A 17-rule, 800-line SKILL.md cannot achieve strong consistency. Gates get forgotten, DB updates get missed, regression tests get skipped.

The solution: **split responsibilities.** Python code handles everything deterministic (state, gates, sequencing, DB, ratchet decisions). Claude Code agents handle everything creative (writing code, analyzing requirements, PM synthesis, code review). SKILL.md files become lightweight "recipes" that alternate between calling Python tools and spawning sub-agents.

This is also the transition from single-agent tool to **multi-agent collaboration platform**, with the agile model formalized: Story is a continuous process producing the product backlog, Specs are sprints consuming backlog items, and everything runs across multiple Claude Code sessions coordinated through SQLite.

Major changes:
1. Python orchestration tools (deterministic process management)
2. SQLite hybrid (files for content, DB for state/tracking/coordination)
3. Dual-track model (Story continuous ←→ Backlog ←→ Sprint autonomous)
4. Living Backlog (not one-time; all unresolved items flow back)
5. Multi-session support (locks, heartbeats, crash recovery)
6. Agent DAG model (observable pipeline with drill-down)
7. Scenario-based regression testing (global suite, only grows)
8. Strict gate checks (code-enforced, not LLM-judged)
9. Story decoupled from Sprint (can run independently, anytime)
10. Sprint always gets its own directory (even single-sprint projects)

---

## Change 31: Architecture Transformation — Code Manages Process

### Problem

Current architecture has the LLM responsible for both creative work AND process management:

```
Current (v5.1):
  SKILL.md (natural language) → LLM interprets → LLM manages state + does work
  
  LLM simultaneously responsible for:
    ✗ Creative work (writing code, analysis, synthesis)     — good at this
    ✗ Process management (state machine, gates, sequencing) — unreliable at this
    ✗ Record keeping (DB updates, logging, tracking)        — often forgets this
```

With 17 rules and 8-step flows, the LLM frequently:
- Skips state updates
- Forgets gate checks
- Runs steps out of order
- Misses regression test triggers
- Uses inconsistent status values ("done" vs "completed" vs "finished")

### Solution

Split into two layers:

```
v6 Architecture:
  Python tools (deterministic) + Claude Code agents (creative)
  
  Python tools handle:             Claude Code agents handle:
    ✓ State transitions              ✓ Writing code
    ✓ Gate checks                    ✓ Analyzing requirements
    ✓ DB operations (atomic)         ✓ PM synthesis
    ✓ Ratchet decisions              ✓ Code review
    ✓ Regression test triggers       ✓ Acceptance review
    ✓ Agent registration/tracking    ✓ Story discussion
    ✓ Lock management                ✓ All creative/analytical work
    ✓ Crash recovery                 
    ✓ Event logging                  
```

### Python tools live inside the Plugin

```
ratchet/                            # Claude Code Plugin
├── .claude-plugin/plugin.json
├── tools/                          # Python tools (distributed with plugin)
│   ├── ratchet.py                  # Main CLI entry point
│   ├── db.py                       # SQLite operations layer
│   ├── gates.py                    # Gate check logic
│   ├── models.py                   # Data models
│   ├── schema.sql                  # DB initialization schema
│   └── regression.py               # Regression test management
├── commands/                       # User-facing commands
├── skills/                         # Lightweight agent guides
├── agents/                         # Sub-agent prompt templates
└── references/
```

### SKILL.md pattern changes

Every step becomes: **Python call → Claude Code creative work → Python call**

```
Before (v5.1 — LLM manages everything):
  "After WP execution, run regression tests. If they fail, 
   discard the changes. Update the DB with the result."
  → LLM might forget any of these steps

After (v6 — code manages process):
  1. python tools/ratchet.py wp start sprint-1 wp-01
  2. [Claude Code: spawn wp-executor sub-agent]
  3. python tools/ratchet.py ratchet decide sprint-1 wp-01 --score=0.85
     → outputs KEEP or DISCARD (deterministic comparison)
  4. python tools/ratchet.py regression run sprint-1
     → outputs PASS or FAIL (deterministic test execution)
  → LLM just follows the recipe; code handles consistency
```

### Files to create
- `tools/ratchet.py` — Main CLI
- `tools/db.py` — SQLite layer
- `tools/gates.py` — Gate checks
- `tools/models.py` — Data models
- `tools/schema.sql` — DB schema
- `tools/regression.py` — Regression management

### Files to modify
- All `skills/*/SKILL.md` — Simplify to "recipe" pattern (Python call → agent work → Python call)
- `skills/getting-started/SKILL.md` — Session startup checks ratchet-cli, reads DB status
- `DESIGN.md` — Document new architecture

---

## Change 32: SQLite Hybrid — Files for Content, DB for State

### Problem

State is scattered across 10+ YAML files (state.yaml, execution-state.yaml, review_log.yaml, etc.). No atomic updates, no query capability, concurrent write risks, inconsistent state.

### Solution

SQLite database for all state/tracking. Files for all human-readable content.

```
Files (human + agent readable):        DB (process management):
  perspectives/*.md                      project status
  synthesis.md                           backlog items + status
  spec.yaml                              sprint lifecycle
  proofs/*.md                            step status + gates
  acceptance/*.md                        work package status
  agent-logs/*.md                        agent DAG + activity
  prototype.html                         verification results
  scenario tests                         regression results
                                         locks + heartbeats
                                         audit log
```

### Database schema

```sql
-- === Project ===
CREATE TABLE project (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    workspace TEXT NOT NULL,
    mode TEXT NOT NULL,                -- greenfield | existing
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- === Backlog ===
CREATE TABLE backlog (
    id TEXT PRIMARY KEY,
    project_id TEXT REFERENCES project(id),
    type TEXT NOT NULL,               -- feature | bug | improvement | unresolved | test_gap | tech_debt
    title TEXT NOT NULL,
    description TEXT,
    source TEXT,                      -- story_phase | user_report | execution | acceptance_review | qa_review
    source_sprint TEXT,
    source_wp TEXT,
    source_roles TEXT,                -- JSON array
    priority TEXT DEFAULT 'should',   -- must | should | could | wont
    status TEXT DEFAULT 'new',        -- new | prioritized | planned | executing | done | wont_do | blocked
    planned_sprint TEXT,
    story_points INTEGER,
    decision TEXT,                    -- Human decision content (for unresolved items)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- === Sprint ===
CREATE TABLE sprints (
    id TEXT PRIMARY KEY,
    project_id TEXT REFERENCES project(id),
    name TEXT,
    type TEXT DEFAULT 'normal',       -- normal | hotfix
    points INTEGER,
    status TEXT DEFAULT 'pending',    -- pending | executing | done | failed | paused
    depends_on TEXT,                  -- JSON array of sprint IDs
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- === Sprint Steps (lifecycle) ===
CREATE TABLE sprint_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sprint_id TEXT REFERENCES sprints(id),
    step_name TEXT NOT NULL,          -- spec | preparation | eva | planning | execution |
                                     -- regression | acceptance | finalize
    step_order INTEGER,
    status TEXT DEFAULT 'pending',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    gate_result TEXT                  -- JSON: gate check details
);

-- === Work Packages ===
CREATE TABLE work_packages (
    id TEXT,
    sprint_id TEXT REFERENCES sprints(id),
    name TEXT,
    status TEXT DEFAULT 'pending',    -- pending | in_progress | done | failed | blocked
    blocked_by TEXT,                  -- JSON array of WP IDs
    iteration INTEGER DEFAULT 0,
    max_iterations INTEGER DEFAULT 8,
    best_score REAL DEFAULT 0,
    current_failure TEXT,
    proof_path TEXT,
    committed_at TIMESTAMP,
    PRIMARY KEY (id, sprint_id)
);

-- === Agent DAG ===
CREATE TABLE agent_nodes (
    id TEXT PRIMARY KEY,
    sprint_id TEXT REFERENCES sprints(id),
    agent_type TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    model TEXT,
    group_id TEXT,                    -- Same group = parallel execution
    status TEXT DEFAULT 'pending',    -- pending | queued | running | done | failed | skipped
    current_activity TEXT,
    progress TEXT,
    input_files TEXT,                 -- JSON
    output_files TEXT,                -- JSON
    prompt_summary TEXT,
    result_summary TEXT,
    log_file TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms INTEGER
);

CREATE TABLE agent_edges (
    from_agent TEXT REFERENCES agent_nodes(id),
    to_agent TEXT REFERENCES agent_nodes(id),
    edge_type TEXT,                   -- depends_on | feeds_into | triggers
    data_flow TEXT,
    PRIMARY KEY (from_agent, to_agent)
);

-- === Agent Activity (fine-grained events) ===
CREATE TABLE agent_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_node_id TEXT REFERENCES agent_nodes(id),
    activity_type TEXT NOT NULL,      -- started | completed | failed | analyzing | deciding |
                                     -- reading_file | writing_file | running_command | running_test |
                                     -- test_passed | test_failed | score_updated | artifact_produced |
                                     -- backlog_created | decision_deferred | dependency_waiting
    detail TEXT,
    file_path TEXT,
    tool_name TEXT,
    duration_ms INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- === Verification Log ===
CREATE TABLE verification_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sprint_id TEXT,
    wp_id TEXT,
    constraint_id TEXT,
    level TEXT,                       -- static | unit | integration | ai_review | qa_review
    result TEXT,                      -- pass | fail | skipped
    score REAL,
    iteration INTEGER,
    raw_output TEXT,
    failure_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- === Regression Tests ===
CREATE TABLE regression_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT,
    scenario_id TEXT,
    source_sprint TEXT,
    test_type TEXT,                   -- scenario | integration | smoke
    test_file TEXT,
    test_command TEXT,
    last_result TEXT,                 -- pass | fail
    last_run_at TIMESTAMP,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- === Sprint Locks ===
CREATE TABLE sprint_locks (
    sprint_id TEXT PRIMARY KEY,
    session_id TEXT,
    status TEXT,                      -- active | released | crashed
    started_at TIMESTAMP,
    last_heartbeat TIMESTAMP
);

-- === Audit Log ===
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT,                 -- project | sprint | step | wp | backlog | agent | file
    entity_id TEXT,
    action TEXT,                      -- created | updated | status_changed | gate_passed | gate_failed
    old_value TEXT,
    new_value TEXT,
    actor TEXT,                       -- user | agent:{type} | system
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- === Indexes ===
CREATE INDEX idx_backlog_status ON backlog(status);
CREATE INDEX idx_backlog_priority ON backlog(priority);
CREATE INDEX idx_sprints_status ON sprints(status);
CREATE INDEX idx_agents_sprint ON agent_nodes(sprint_id);
CREATE INDEX idx_agents_status ON agent_nodes(status);
CREATE INDEX idx_activity_agent ON agent_activity(agent_node_id);
CREATE INDEX idx_activity_time ON agent_activity(timestamp);
CREATE INDEX idx_verification_sprint ON verification_log(sprint_id);
CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id);
```

### Files to create
- `tools/schema.sql` — Complete DB schema
- `tools/db.py` — SQLite operations layer with WAL mode

### Files to remove (replaced by DB)
- `~/.config/ratchet/state.yaml` → DB project + sprints tables
- `~/.config/ratchet/review_queue.yaml` → DB backlog table (type=unresolved)
- `.ratchet/execution-state.yaml` → DB sprint_steps + work_packages tables
- `.ratchet/{intent}/review_log.yaml` → DB verification_log table
- `.ratchet/{intent}/suggested_constraints.yaml` → DB backlog table
- `.ratchet/{intent}/metrics.yaml` → DB computed from audit_log + agent_activity

---

## Change 33: Dual-Track Model — Story Continuous, Sprint Autonomous

### Problem

Story is currently a one-time phase that must complete before sprints start. But:
- New requirements arrive during execution
- Bug reports come in anytime
- Acceptance review discovers gaps
- Execution finds unresolvable decisions

All of these need to feed back into the backlog, but the current flow has no mechanism for continuous backlog growth.

### Solution

Two independent tracks communicating through the Backlog:

```
HUMAN TRACK (Story — continuous):     AGENT TRACK (Sprint — autonomous):
  Create initial backlog                Sprint Planning (from backlog)
  Add new features anytime              Spec generation (auto)
  Report bugs                           Execution
  Review results                        Verification + regression
  Confirm decisions                     Acceptance Review
  Refine priorities                     Report → next Sprint
  
  ←── Unresolved items flow back
  ←── Acceptance gaps flow back
  ←── QA recommendations flow back
```

### Story is not a phase, it's a process

```
Forms of Story interaction:

  Full Story: Project startup / major new feature
    → Role derivation → Parallel perspectives → PM synthesis
    → Batch of new Backlog items
    
  Mini Story: Medium feature addition
    → Run relevant perspectives only → Quick synthesis
    → Few new Backlog items
    
  Direct Entry: Bug / small change
    → Directly create Backlog item, no perspectives needed
    
  Agent Feedback: Execution produces unresolved items
    → Auto-created Backlog items
    → User confirms decision → item re-prioritized
    
  Backlog Refinement: Ongoing maintenance
    → Adjust priorities, merge items, mark won't-do
```

### Nothing blocks Sprint execution

```
During Sprint execution, if agent encounters something it can't resolve:

  Before (v5.1 — blocking):
    Agent stops → asks user → waits → continues
    
  After (v6 — non-blocking):
    Agent uses best-effort → documents decision in proof
    → Creates Backlog item (type=unresolved)
    → Continues execution without stopping
    → User addresses it later (becomes next Sprint or refinement)
```

### Sprint auto-continuation

```
Sprint N completes:
  1. Register scenario tests to regression suite
  2. Check Backlog for must items:
     → Must items exist? → Auto-plan Sprint N+1
     → Only should/could? → Notify user, wait for decision
     → Empty? → Project idle
  3. Notify user of Sprint N results
```

### Human confirmation is ONE time

```
  Story phase: User confirms initial backlog     ← ONLY required human confirmation
  After that: All sprints auto-execute
  
  Spec is auto-generated from confirmed backlog items — no second confirmation.
  If agent is uncertain about a constraint → best-effort + backlog item.
```

### Files to modify
- `skills/story/SKILL.md` — Rewrite as continuous process, not phase
- `skills/getting-started/SKILL.md` — Routing includes backlog management
- `skills/execute/SKILL.md` — Non-blocking execution, unresolved → backlog
- `DESIGN.md` — Dual-track architecture

---

## Change 34: Unified Directory Structure

### Problem

Single-sprint and multi-sprint projects have different directory structures. Agent code needs branching logic. Sprint artifacts aren't cleanly isolated.

### Solution

All projects use the same structure. Even single-sprint projects use `sprints/sprint-1/`.

```
.ratchet/
│
├── ratchet.db                        # SQLite (state + tracking + coordination)
├── project.yaml                      # Project metadata (lightweight; core state in DB)
│
├── story/                            # Product Backlog artifacts (continuous, not one-time)
│   ├── codebase-analysis.md          # Latest codebase analysis
│   ├── domain-research.md            # Domain research (cumulative)
│   ├── roles.yaml                    # Current active role set (can update)
│   ├── perspectives/                 # Role perspective documents (can add new ones)
│   │   ├── end-user.md
│   │   ├── developer.md
│   │   └── ...
│   ├── synthesis/                    # PM synthesis docs (versioned, multiple)
│   │   ├── initial.md                # Initial synthesis
│   │   ├── v2-notifications.md       # Incremental synthesis for new feature
│   │   └── ...
│   ├── personas.md                   # Unified personas (updated as backlog grows)
│   ├── journey.md                    # Unified journey (updated)
│   ├── scenarios.md                  # Scenario table (grows over time)
│   ├── decisions.md                  # Decision log (grows)
│   ├── mood.md                       # Visual direction (can update)
│   ├── prototype.html                # Prototype (can update)
│   ├── complexity.yaml               # Latest estimation
│   └── sprint-plan.md                # Manager's sprint plan (updated each planning)
│
├── sprints/                          # ALL Sprints (always, even if only one)
│   ├── sprint-1/
│   │   ├── backlog-items.yaml        # Snapshot of backlog items for this sprint
│   │   ├── spec.yaml                 # Auto-generated constraints
│   │   ├── spec-review.html          # Spec review page (optional in v6)
│   │   ├── plan.yaml                 # WP decomposition
│   │   ├── pre-validation.log        # EVA validation log
│   │   ├── test-suite/               # Constraint tests
│   │   │   ├── manifest.yaml
│   │   │   ├── auto/
│   │   │   ├── ai-review/
│   │   │   └── human/
│   │   ├── scenario-tests/           # Scenario-based tests
│   │   │   ├── S-01.test.ts
│   │   │   └── S-02.test.ts
│   │   ├── execution-state.yaml      # Execution checkpoint (for crash recovery)
│   │   ├── proofs/                   # WP completion proofs
│   │   │   └── wp-{id}.md
│   │   ├── acceptance/               # Perspective acceptance reviews
│   │   │   ├── {role}.md
│   │   │   └── summary.md
│   │   ├── agent-logs/               # Per-agent detailed work logs
│   │   │   ├── perspective-enduser.md
│   │   │   ├── wp-01-executor.md
│   │   │   ├── wp-01-verifier.md
│   │   │   └── ...
│   │   ├── reports/                  # Iteration reports
│   │   │   └── iter-{N}.md
│   │   └── metrics.yaml              # Sprint metrics summary
│   │
│   ├── sprint-2/
│   │   ├── inputs.yaml               # Explicit: "Sprint 1 delivered X, Y, Z"
│   │   └── ...
│   └── ...
│
├── regression/                       # Global regression test suite (only grows)
│   ├── manifest.yaml                 # Scenario → test file mapping
│   ├── S-01.test.ts                  # Accumulated from all sprints
│   ├── S-02.test.ts
│   └── last-run.yaml                 # Latest regression run results
│
└── tools/                            # Python tools (from plugin, symlinked or copied)
    └── → {plugin-path}/tools/
```

---

## Change 35: Scenario-Based Regression Testing

### Problem

Testing only validates spec constraints. PM's scenarios (end-to-end user stories) are never directly tested. Sprint 2 can break Sprint 1's functionality without anyone noticing until human review.

### Solution

Three-layer test architecture with a persistent, growing global regression suite.

### Three layers

```
Layer 1: Constraint Tests (existing, per-sprint)
  Per-WP verification against spec.yaml invariants/quality dimensions.
  Lives in: sprints/sprint-N/test-suite/

Layer 2: Scenario Tests (NEW, per-sprint)
  End-to-end tests mapping directly to scenarios.md entries.
  Lives in: sprints/sprint-N/scenario-tests/
  
  Each scenario from scenarios.md gets a test:
    "User creates task → task appears in list" → S-01.test.ts
    "Task due date passes → notification sent" → S-02.test.ts
    "Concurrent update → conflict detected"    → S-05.test.ts

Layer 3: Regression Suite (NEW, project-level, only grows)
  Accumulated scenario tests from all completed sprints.
  Lives in: regression/
  
  After Sprint 1: regression/ has S-01, S-02, S-03
  After Sprint 2: regression/ has S-01, S-02, S-03, S-04, S-05, S-06, S-07
  Never shrinks. New sprints only add tests.
```

### Regression trigger points

```
Trigger 1: Sprint start
  → Run regression/ full suite → confirm baseline
  → If fails → block sprint start → fix first

Trigger 2: After each WP completion (in verify step)
  → Run constraint tests (existing) + regression/ full suite
  → If regression fails → this WP broke existing functionality → ratchet discard

Trigger 3: Sprint completion, before acceptance
  → Full regression run
  → Sprint's scenario tests registered to regression/

Trigger 4: Before merge to main
  → Final full regression → must all pass
```

### Python tool commands

```bash
python tools/ratchet.py regression run                    # Run full suite
python tools/ratchet.py regression register {sprint_id}   # Register sprint's tests
python tools/ratchet.py regression status                 # Show coverage
```

---

## Change 36: Multi-Session Support

### Problem

Long sprints exceed context window limits. Users need to interact while sprints execute. Sessions can crash mid-execution.

### Solution

Multiple Claude Code sessions coordinated through ratchet.db.

### Session types

```
Session A (Human Interactive):
  Story discussion, review, backlog management
  Can run concurrently with Sprint execution

Session B (Sprint Execution):
  Autonomous sprint execution
  One sprint per session
  Reads/writes DB for coordination

Both share:
  .ratchet/ratchet.db (SQLite WAL mode — concurrent reads, serialized writes)
  .ratchet/ file system
```

### Concurrency rules

```
✓ Allowed:
  Human session + Sprint execution session (different operations)
  Multiple human sessions (all read/write backlog, read sprint status)
  Status check from any session

✗ Not allowed:
  Two sessions executing same Sprint (enforced by DB lock)
  Two sessions writing code in same workspace simultaneously
```

### Sprint lock mechanism

```sql
CREATE TABLE sprint_locks (
    sprint_id TEXT PRIMARY KEY,
    session_id TEXT,
    status TEXT,              -- active | released | crashed
    started_at TIMESTAMP,
    last_heartbeat TIMESTAMP
);
```

```bash
# Acquiring lock
python tools/ratchet.py sprint lock {sprint_id}
# → Success: lock acquired
# → Failure: "Sprint locked by session X, started at Y"

# Releasing lock
python tools/ratchet.py sprint unlock {sprint_id}

# Force unlock (after crash)
python tools/ratchet.py sprint force-unlock {sprint_id}

# Heartbeat (called periodically during execution)
python tools/ratchet.py sprint heartbeat {sprint_id}
```

### Crash recovery

```
Session B crashes during Sprint 1, wp-03, iteration 4:

  DB state (persisted):
    sprint-1: status=executing
    wp-03: status=in_progress, iteration=4, best_score=0.72
    lock: session_id=B, last_heartbeat=2 hours ago
    
  Git state:
    Last KEEP commit: wp-03 iter 3, score 0.72
    Uncommitted changes: iter 4 (possibly incomplete)

New Session C starts:
  1. getting-started reads DB → detects stale lock
  2. Prompts user: "Sprint 1 execution appears crashed. Resume?"
  3. User confirms:
     python tools/ratchet.py sprint force-unlock sprint-1
     git reset --hard  # Back to last KEEP
     → Resume from wp-03, iteration 5
```

### Session startup protocol

```
Every new Claude Code session:
  1. Check ratchet-cli: python tools/ratchet.py --version
  2. Read project status: python tools/ratchet.py status
  
  Status output routes to:
    "No project" → suggest /ratchet:story or /ratchet:init
    "Sprint N executing (active in other session)" → monitoring mode
    "Sprint N executing (STALE)" → offer crash recovery
    "Sprint N done, Sprint N+1 pending" → offer review or next sprint
    "Backlog has N new items" → offer sprint planning
```

---

## Change 37: Agent DAG Model + Observability

### Problem

No visibility into which agents are running, what they're doing, or how they relate to each other.

### Solution

Every Sprint execution creates a DAG of agent nodes. Each agent logs fine-grained activity to DB. Agent work logs written as readable .md files for drill-down.

### DAG structure

```
Sprint DAG (example):

[Parallel: Perspectives]
  ├─ perspective-enduser ──┐
  ├─ perspective-developer ┤
  └─ perspective-qa ───────┼──→ [pm-synthesis] ──→ [spec-generation]
                           │
                     [Parallel: Preparation]
                     ├─ env-preparer ────┐
                     └─ test-generator ──┤
                                         │
                                   [eva-validation]
                                         │
                                    [planning]
                                         │
                     [Execution: WPs]
                     ├─ wp-01-exec → wp-01-verify ─┐
                     ├─ wp-02-exec → wp-02-verify ─┤──→ [regression]
                     └─ wp-03-exec → wp-03-verify ─┘       │
                                                     [Parallel: Acceptance]
                                                     ├─ accept-enduser ──┐
                                                     ├─ accept-developer ┤
                                                     └─ accept-qa ───────┤
                                                                         │
                                                                   [pm-acceptance]
                                                                         │
                                                                   [finalize]
```

### Agent observability protocol

Every agent must:
1. Register at start: `python tools/ratchet.py agent register {sprint_id} {type} {name}`
2. Log significant activities: `python tools/ratchet.py agent log {agent_id} {activity_type} "detail"`
3. Update on completion: `python tools/ratchet.py agent complete {agent_id}`
4. Write detailed work log: `sprints/{sprint}/agent-logs/{agent-name}.md`

### Work log format

```markdown
# Agent Log: WP-01 Executor (Sprint 1, Iteration 2)

## Task
Implement auth middleware per spec.yaml INV-01, INV-02

## Activity Log

### 14:30:05 — Reading test files
Read test-suite/auto/INV-01.test.ts → 5 test cases

### 14:30:12 — Planning implementation
Approach: express middleware with JWT verification

### 14:30:25 — Writing code
Created: src/middleware/auth.ts (45 lines)

### 14:30:45 — Running build
Command: tsc --noEmit → PASS

### 14:30:52 — Running tests
Result: 4/5 PASS, 1 FAIL (revoked token not handled)

### 14:31:10 — Fixing
Modified: src/middleware/auth.ts → added token blacklist

### 14:31:30 — Re-running tests
Result: 5/5 PASS ✓

## Output
Files: src/middleware/auth.ts
Tests: 5/5 passing
```

---

## Change 38: Strict Gate Checks

### Problem

Gate checks are natural language instructions ("check that spec.yaml exists before proceeding"). LLMs skip them or misjudge them.

### Solution

Gates are Python code. File existence, YAML validity, test pass/fail — all checked by deterministic code.

### Gate definitions

| Step | Gate Check (code-enforced) |
|------|---------------------------|
| spec | spec.yaml exists + valid YAML + all constraints have test_method + human decisions resolved |
| preparation | pre-validation.log exists + test-suite/manifest.yaml exists + all constraints covered |
| eva | pipeline dry-run passes |
| planning | plan.yaml exists + all WPs have acceptance criteria |
| execution | all WPs have proof document + all auto tests pass |
| regression | regression suite all pass |
| acceptance | acceptance/summary.md exists + PM verdict present |
| finalize | regression pass + merged to main |

### Python implementation

```bash
# Gate check is a single command
python tools/ratchet.py gate check {sprint_id} {step_name}

# Output (machine-readable):
# PASS: all 4 checks passed
# FAIL: 2/4 checks passed
#   ✗ spec.yaml: missing test_method for INV-03
#   ✗ decisions: 1 unresolved human_must_decide item
```

The SKILL.md simply says "run the gate check command and only proceed if it passes."

---

## Change 39: Python Tool CLI Interface

### Complete command reference

```bash
# === Project ===
python tools/ratchet.py init "Project Name"
python tools/ratchet.py status
python tools/ratchet.py status --json                     # Machine-readable

# === Backlog ===
python tools/ratchet.py backlog add --type=feature --priority=must "title" ["description"]
python tools/ratchet.py backlog list [--status=new] [--priority=must] [--type=bug]
python tools/ratchet.py backlog update {id} [--priority=X] [--status=X] [--decision="X"]
python tools/ratchet.py backlog stats                     # Summary counts

# === Sprint ===
python tools/ratchet.py sprint plan                       # Manager plans next sprint
python tools/ratchet.py sprint list
python tools/ratchet.py sprint status {sprint_id}
python tools/ratchet.py sprint lock {sprint_id}
python tools/ratchet.py sprint unlock {sprint_id}
python tools/ratchet.py sprint force-unlock {sprint_id}
python tools/ratchet.py sprint heartbeat {sprint_id}
python tools/ratchet.py sprint pause {sprint_id}
python tools/ratchet.py sprint resume {sprint_id}

# === Step Lifecycle ===
python tools/ratchet.py step start {sprint_id} {step_name}
python tools/ratchet.py step complete {sprint_id} {step_name}
python tools/ratchet.py gate check {sprint_id} {step_name}

# === Work Package ===
python tools/ratchet.py wp start {sprint_id} {wp_id}
python tools/ratchet.py wp update {sprint_id} {wp_id} [--score=X] [--status=X] [--failure="X"]
python tools/ratchet.py wp list {sprint_id}

# === Ratchet Decision ===
python tools/ratchet.py ratchet decide {sprint_id} {wp_id} --score={X}
# Output: KEEP (improved: 0.72 → 0.85) or DISCARD (no improvement: 0.85 >= 0.80)

# === Regression ===
python tools/ratchet.py regression run [--sprint={id}]
python tools/ratchet.py regression register {sprint_id}
python tools/ratchet.py regression status

# === Agent DAG ===
python tools/ratchet.py agent register {sprint_id} {type} {name} [--model=sonnet]
python tools/ratchet.py agent update {agent_id} [--status=X] [--activity="X"] [--progress="X"]
python tools/ratchet.py agent complete {agent_id} [--summary="X"]
python tools/ratchet.py agent log {agent_id} {activity_type} "detail" [--file=X]
python tools/ratchet.py agent dag {sprint_id}             # Output DAG structure
python tools/ratchet.py agent list [--sprint={id}] [--status=running]

# === Events ===
python tools/ratchet.py events [--sprint={id}] [--agent={id}] [--limit=20]
python tools/ratchet.py events --follow                   # Tail mode (for monitoring)
```

---

## Updated Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                     Ratchet v6                           │
│                                                          │
│  ┌──────────────────┐    ┌───────────┐    ┌───────────┐ │
│  │ Claude Code      │    │ Terminal  │    │ Ratchet   │ │
│  │ Plugin           │    │ CLI      │    │ Studio    │ │
│  │ (interactive)    │    │ (direct) │    │ (visual)  │ │
│  └────────┬─────────┘    └─────┬─────┘    └─────┬─────┘ │
│           │                    │                │       │
│           └────────────────────┼────────────────┘       │
│                                │                        │
│                    ┌───────────▼──────────┐              │
│                    │   Python tools/      │              │
│                    │   (deterministic)    │              │
│                    │   State, Gates, DB   │              │
│                    └───────────┬──────────┘              │
│                                │                        │
│                    ┌───────────▼──────────┐              │
│                    │    ratchet.db        │              │
│                    │    (SQLite WAL)      │              │
│                    └───────────┬──────────┘              │
│                                │                        │
│              ┌─────────────────┼─────────────────┐      │
│              │                 │                 │      │
│      ┌───────▼──────┐  ┌──────▼───────┐  ┌─────▼────┐ │
│      │ .ratchet/    │  │ .ratchet/    │  │regression│ │
│      │ story/       │  │ sprints/     │  │/         │ │
│      │ (content)    │  │ (per-sprint) │  │(tests)   │ │
│      └──────────────┘  └──────────────┘  └──────────┘ │
│                                                        │
└──────────────────────────────────────────────────────────┘
```

---

## Implementation Priority

1. **Change 31: Python tools** — Foundation. Must exist before anything else works.
2. **Change 32: SQLite schema** — Required by Python tools.
3. **Change 34: Directory structure** — Standardize before creating content.
4. **Change 38: Gate checks** — Core consistency mechanism.
5. **Change 33: Dual-track model** — Core workflow change.
6. **Change 39: CLI interface** — Complete tool interface.
7. **Change 35: Regression testing** — Quality assurance.
8. **Change 36: Multi-session** — Operational necessity.
9. **Change 37: Agent DAG** — Observability (needed for Studio).

---

## Interaction with v5 Changes

- **Role derivation (v5.1)**: Unchanged. Roles still derived from intent, not static list.
- **Perspectives + PM synthesis**: Unchanged in concept. Agents still spawned by Claude Code. But state tracking now through Python tools.
- **Manager sprint planning**: Unchanged. Manager always runs. But sprint creation/tracking through DB.
- **Acceptance Review**: Unchanged. But results tracked in DB, gaps auto-create Backlog items.
- **Spec auto-extraction**: Unchanged. But spec.yaml validity checked by code gate, not LLM judgment.
- **Story phase**: Transformed from one-time phase to continuous process.
- **Session management**: Transformed from manual suggestion to DB-coordinated multi-session.
