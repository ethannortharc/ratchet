-- Ratchet v6 Database Schema
-- SQLite with WAL mode for concurrent access
-- Files store content (human-readable). DB stores state/tracking/coordination.

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- === Project ===
CREATE TABLE IF NOT EXISTS project (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    workspace TEXT NOT NULL,
    mode TEXT NOT NULL DEFAULT 'greenfield',  -- greenfield | existing
    status TEXT NOT NULL DEFAULT 'active',     -- active | paused | archived
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- === Backlog ===
CREATE TABLE IF NOT EXISTS backlog (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES project(id),
    type TEXT NOT NULL,                -- feature | bug | improvement | unresolved | test_gap | tech_debt
    title TEXT NOT NULL,
    description TEXT,
    source TEXT,                       -- story_phase | user_report | execution | acceptance_review | qa_review | agent_suggestion
    source_sprint TEXT,
    source_wp TEXT,
    source_roles TEXT,                 -- JSON array
    priority TEXT NOT NULL DEFAULT 'should',  -- must | should | could | wont
    status TEXT NOT NULL DEFAULT 'new',       -- new | prioritized | planned | executing | done | wont_do | blocked
    planned_sprint TEXT,
    story_points INTEGER,
    decision TEXT,                     -- Human decision content (for unresolved items)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- === Sprint ===
CREATE TABLE IF NOT EXISTS sprints (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES project(id),
    name TEXT,
    type TEXT NOT NULL DEFAULT 'normal',  -- normal | hotfix
    points INTEGER,
    status TEXT NOT NULL DEFAULT 'pending',  -- pending | executing | done | failed | paused
    depends_on TEXT,                   -- JSON array of sprint IDs
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- === Sprint Steps (lifecycle) ===
CREATE TABLE IF NOT EXISTS sprint_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sprint_id TEXT NOT NULL REFERENCES sprints(id),
    step_name TEXT NOT NULL,           -- spec | preparation | eva | planning | execution | regression | acceptance | finalize
    step_order INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',  -- pending | in_progress | done | failed | skipped
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    gate_result TEXT,                  -- JSON: gate check details
    UNIQUE(sprint_id, step_name)
);

-- === Work Packages ===
CREATE TABLE IF NOT EXISTS work_packages (
    id TEXT NOT NULL,
    sprint_id TEXT NOT NULL REFERENCES sprints(id),
    name TEXT,
    status TEXT NOT NULL DEFAULT 'pending',  -- pending | in_progress | done | failed | blocked
    blocked_by TEXT,                   -- JSON array of WP IDs
    iteration INTEGER DEFAULT 0,
    max_iterations INTEGER DEFAULT 8,
    best_score REAL DEFAULT 0.0,
    current_failure TEXT,
    proof_path TEXT,
    committed_at TIMESTAMP,
    PRIMARY KEY (id, sprint_id)
);

-- === Agent DAG Nodes ===
CREATE TABLE IF NOT EXISTS agent_nodes (
    id TEXT PRIMARY KEY,
    sprint_id TEXT REFERENCES sprints(id),
    agent_type TEXT NOT NULL,           -- perspective | pm_synthesis | manager | env_preparer | test_generator | wp_executor | verifier | acceptance | pm_acceptance | report_writer
    agent_name TEXT NOT NULL,
    model TEXT,                         -- sonnet | opus | haiku
    group_id TEXT,                      -- Same group = parallel execution
    status TEXT NOT NULL DEFAULT 'pending',  -- pending | queued | running | done | failed | skipped
    current_activity TEXT,
    progress TEXT,
    input_files TEXT,                   -- JSON array
    output_files TEXT,                  -- JSON array
    prompt_summary TEXT,
    result_summary TEXT,
    log_file TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms INTEGER
);

-- === Agent DAG Edges ===
CREATE TABLE IF NOT EXISTS agent_edges (
    from_agent TEXT NOT NULL REFERENCES agent_nodes(id),
    to_agent TEXT NOT NULL REFERENCES agent_nodes(id),
    edge_type TEXT NOT NULL,            -- depends_on | feeds_into | triggers
    data_flow TEXT,
    PRIMARY KEY (from_agent, to_agent)
);

-- === Agent Activity (fine-grained events) ===
CREATE TABLE IF NOT EXISTS agent_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_node_id TEXT REFERENCES agent_nodes(id),
    activity_type TEXT NOT NULL,
    detail TEXT,
    file_path TEXT,
    tool_name TEXT,
    duration_ms INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- === Verification Log ===
CREATE TABLE IF NOT EXISTS verification_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sprint_id TEXT NOT NULL,
    wp_id TEXT NOT NULL,
    constraint_id TEXT,
    level TEXT,                         -- static | unit | integration | ai_review | qa_review
    result TEXT NOT NULL,               -- pass | fail | skipped
    score REAL,
    iteration INTEGER,
    raw_output TEXT,
    failure_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- === Regression Tests ===
CREATE TABLE IF NOT EXISTS regression_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    scenario_id TEXT NOT NULL,
    description TEXT,
    source_sprint TEXT,
    source_role TEXT,
    test_type TEXT,                     -- scenario | integration | smoke
    test_file TEXT,
    test_command TEXT,
    last_result TEXT,                   -- pass | fail | null (never run)
    last_run_at TIMESTAMP,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, scenario_id)
);

-- === Sprint Locks (multi-session coordination) ===
CREATE TABLE IF NOT EXISTS sprint_locks (
    sprint_id TEXT PRIMARY KEY REFERENCES sprints(id),
    session_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',  -- active | released | crashed
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- === Audit Log ===
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,          -- project | sprint | step | wp | backlog | agent | file
    entity_id TEXT NOT NULL,
    action TEXT NOT NULL,               -- created | updated | status_changed | gate_passed | gate_failed
    old_value TEXT,
    new_value TEXT,
    actor TEXT,                         -- user | agent:{type} | system
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- === Indexes ===
CREATE INDEX IF NOT EXISTS idx_backlog_project ON backlog(project_id);
CREATE INDEX IF NOT EXISTS idx_backlog_status ON backlog(status);
CREATE INDEX IF NOT EXISTS idx_backlog_priority ON backlog(priority);
CREATE INDEX IF NOT EXISTS idx_backlog_type ON backlog(type);
CREATE INDEX IF NOT EXISTS idx_sprints_project ON sprints(project_id);
CREATE INDEX IF NOT EXISTS idx_sprints_status ON sprints(status);
CREATE INDEX IF NOT EXISTS idx_steps_sprint ON sprint_steps(sprint_id);
CREATE INDEX IF NOT EXISTS idx_wp_sprint ON work_packages(sprint_id);
CREATE INDEX IF NOT EXISTS idx_agents_sprint ON agent_nodes(sprint_id);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agent_nodes(status);
CREATE INDEX IF NOT EXISTS idx_activity_agent ON agent_activity(agent_node_id);
CREATE INDEX IF NOT EXISTS idx_activity_time ON agent_activity(timestamp);
CREATE INDEX IF NOT EXISTS idx_verification_sprint ON verification_log(sprint_id);
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_time ON audit_log(timestamp);
