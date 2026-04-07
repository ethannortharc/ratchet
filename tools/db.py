"""Ratchet DB — SQLite operations layer with WAL mode for concurrent access."""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

DB_NAME = "ratchet.db"
SCHEMA_FILE = Path(__file__).parent / "schema.sql"


def find_db_path(start_dir: str = None) -> Path:
    """Find .ratchet/ratchet.db by walking up from start_dir."""
    d = Path(start_dir or os.getcwd())
    while d != d.parent:
        db_path = d / ".ratchet" / DB_NAME
        if db_path.exists():
            return db_path
        d = d.parent
    return Path(os.getcwd()) / ".ratchet" / DB_NAME


def init_db(workspace: str) -> Path:
    """Initialize DB at <workspace>/.ratchet/ratchet.db."""
    ratchet_dir = Path(workspace) / ".ratchet"
    ratchet_dir.mkdir(parents=True, exist_ok=True)
    db_path = ratchet_dir / DB_NAME
    with get_conn(db_path) as conn:
        conn.executescript(SCHEMA_FILE.read_text())
    return db_path


@contextmanager
def get_conn(db_path: Path = None):
    """Get a connection with WAL mode and foreign keys enabled."""
    path = db_path or find_db_path()
    conn = sqlite3.connect(str(path), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# === Project ===

def create_project(project_id: str, name: str, workspace: str, mode: str = "greenfield") -> dict:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO project (id, name, workspace, mode) VALUES (?, ?, ?, ?)",
            (project_id, name, workspace, mode),
        )
        audit(conn, "project", project_id, "created", actor="user")
    return {"id": project_id, "name": name, "workspace": workspace, "mode": mode}


def get_project() -> dict:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM project LIMIT 1").fetchone()
        return dict(row) if row else None


def update_project_status(status: str):
    with get_conn() as conn:
        proj = conn.execute("SELECT id, status FROM project LIMIT 1").fetchone()
        if proj:
            conn.execute("UPDATE project SET status=?, updated_at=? WHERE id=?",
                         (status, now(), proj["id"]))
            audit(conn, "project", proj["id"], "status_changed", proj["status"], status)


# === Backlog ===

def add_backlog(project_id: str, item_type: str, title: str, description: str = None,
                priority: str = "should", source: str = None, source_sprint: str = None,
                source_wp: str = None, source_roles: list = None) -> str:
    item_id = _next_backlog_id(project_id)
    roles_json = json.dumps(source_roles) if source_roles else None
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO backlog (id, project_id, type, title, description, priority,
               source, source_sprint, source_wp, source_roles)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (item_id, project_id, item_type, title, description, priority,
             source, source_sprint, source_wp, roles_json),
        )
        audit(conn, "backlog", item_id, "created", actor="user")
    return item_id


def list_backlog(project_id: str = None, status: str = None, priority: str = None,
                 item_type: str = None) -> list:
    clauses, params = [], []
    if project_id:
        clauses.append("project_id = ?"); params.append(project_id)
    if status:
        clauses.append("status = ?"); params.append(status)
    if priority:
        clauses.append("priority = ?"); params.append(priority)
    if item_type:
        clauses.append("type = ?"); params.append(item_type)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    with get_conn() as conn:
        rows = conn.execute(f"SELECT * FROM backlog {where} ORDER BY priority, created_at", params).fetchall()
        return [dict(r) for r in rows]


def update_backlog(item_id: str, **kwargs):
    allowed = {"priority", "status", "decision", "planned_sprint", "description", "story_points"}
    updates = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not updates:
        return
    updates["updated_at"] = now()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    with get_conn() as conn:
        old = conn.execute("SELECT * FROM backlog WHERE id = ?", (item_id,)).fetchone()
        conn.execute(f"UPDATE backlog SET {set_clause} WHERE id = ?",
                     list(updates.values()) + [item_id])
        for k, v in updates.items():
            if k != "updated_at" and old and old[k] != v:
                audit(conn, "backlog", item_id, "updated", str(old[k]), str(v))


def backlog_stats(project_id: str) -> dict:
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM backlog WHERE project_id=?", (project_id,)).fetchone()[0]
        by_status = {r[0]: r[1] for r in conn.execute(
            "SELECT status, COUNT(*) FROM backlog WHERE project_id=? GROUP BY status", (project_id,)).fetchall()}
        by_priority = {r[0]: r[1] for r in conn.execute(
            "SELECT priority, COUNT(*) FROM backlog WHERE project_id=? GROUP BY priority", (project_id,)).fetchall()}
        by_type = {r[0]: r[1] for r in conn.execute(
            "SELECT type, COUNT(*) FROM backlog WHERE project_id=? GROUP BY type", (project_id,)).fetchall()}
    return {"total": total, "by_status": by_status, "by_priority": by_priority, "by_type": by_type}


def _next_backlog_id(project_id: str) -> str:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id FROM backlog WHERE project_id=? ORDER BY id DESC LIMIT 1", (project_id,)
        ).fetchone()
        if row:
            num = int(row["id"].split("-")[1]) + 1
        else:
            num = 1
        return f"B-{num:03d}"


# === Sprint ===

def create_sprint(project_id: str, sprint_id: str, name: str, points: int = 0,
                  sprint_type: str = "normal", depends_on: list = None) -> str:
    deps = json.dumps(depends_on) if depends_on else None
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO sprints (id, project_id, name, type, points, depends_on) VALUES (?, ?, ?, ?, ?, ?)",
            (sprint_id, project_id, name, sprint_type, points, deps),
        )
        # Create lifecycle steps
        steps = [
            ("spec", 1), ("preparation", 2), ("eva", 3), ("planning", 4),
            ("execution", 5), ("regression", 6), ("acceptance", 7), ("finalize", 8),
        ]
        for step_name, order in steps:
            conn.execute(
                "INSERT INTO sprint_steps (sprint_id, step_name, step_order) VALUES (?, ?, ?)",
                (sprint_id, step_name, order),
            )
        audit(conn, "sprint", sprint_id, "created", actor="system")
    return sprint_id


def get_sprint(sprint_id: str) -> dict:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM sprints WHERE id = ?", (sprint_id,)).fetchone()
        return dict(row) if row else None


def list_sprints(project_id: str = None) -> list:
    with get_conn() as conn:
        if project_id:
            rows = conn.execute("SELECT * FROM sprints WHERE project_id=? ORDER BY id", (project_id,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM sprints ORDER BY id").fetchall()
        return [dict(r) for r in rows]


def update_sprint(sprint_id: str, **kwargs):
    allowed = {"status", "started_at", "completed_at", "points", "name"}
    updates = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not updates:
        return
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    with get_conn() as conn:
        old = conn.execute("SELECT * FROM sprints WHERE id=?", (sprint_id,)).fetchone()
        conn.execute(f"UPDATE sprints SET {set_clause} WHERE id = ?",
                     list(updates.values()) + [sprint_id])
        if "status" in updates and old:
            audit(conn, "sprint", sprint_id, "status_changed", old["status"], updates["status"])


# === Sprint Steps ===

def start_step(sprint_id: str, step_name: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE sprint_steps SET status='in_progress', started_at=? WHERE sprint_id=? AND step_name=?",
            (now(), sprint_id, step_name),
        )
        audit(conn, "step", f"{sprint_id}:{step_name}", "status_changed", "pending", "in_progress")


def complete_step(sprint_id: str, step_name: str, gate_result: dict = None):
    gate_json = json.dumps(gate_result) if gate_result else None
    with get_conn() as conn:
        conn.execute(
            "UPDATE sprint_steps SET status='done', completed_at=?, gate_result=? WHERE sprint_id=? AND step_name=?",
            (now(), gate_json, sprint_id, step_name),
        )
        audit(conn, "step", f"{sprint_id}:{step_name}", "status_changed", "in_progress", "done")


def fail_step(sprint_id: str, step_name: str, reason: str = None):
    gate_json = json.dumps({"passed": False, "reason": reason}) if reason else None
    with get_conn() as conn:
        conn.execute(
            "UPDATE sprint_steps SET status='failed', completed_at=?, gate_result=? WHERE sprint_id=? AND step_name=?",
            (now(), gate_json, sprint_id, step_name),
        )
        audit(conn, "step", f"{sprint_id}:{step_name}", "status_changed", "in_progress", "failed")


def get_step(sprint_id: str, step_name: str) -> dict:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM sprint_steps WHERE sprint_id=? AND step_name=?",
            (sprint_id, step_name)
        ).fetchone()
        return dict(row) if row else None


def list_steps(sprint_id: str) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM sprint_steps WHERE sprint_id=? ORDER BY step_order",
            (sprint_id,)
        ).fetchall()
        return [dict(r) for r in rows]


# === Work Packages ===

def create_wp(sprint_id: str, wp_id: str, name: str, blocked_by: list = None, max_iter: int = 8):
    deps = json.dumps(blocked_by) if blocked_by else None
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO work_packages (id, sprint_id, name, blocked_by, max_iterations) VALUES (?, ?, ?, ?, ?)",
            (wp_id, sprint_id, name, deps, max_iter),
        )
        audit(conn, "wp", f"{sprint_id}:{wp_id}", "created", actor="system")


def update_wp(sprint_id: str, wp_id: str, **kwargs):
    allowed = {"status", "iteration", "best_score", "current_failure", "proof_path", "committed_at"}
    updates = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not updates:
        return
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    with get_conn() as conn:
        old = conn.execute("SELECT * FROM work_packages WHERE id=? AND sprint_id=?",
                           (wp_id, sprint_id)).fetchone()
        conn.execute(f"UPDATE work_packages SET {set_clause} WHERE id=? AND sprint_id=?",
                     list(updates.values()) + [wp_id, sprint_id])
        if "status" in updates and old:
            audit(conn, "wp", f"{sprint_id}:{wp_id}", "status_changed", old["status"], updates["status"])


def list_wps(sprint_id: str) -> list:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM work_packages WHERE sprint_id=? ORDER BY id",
                            (sprint_id,)).fetchall()
        return [dict(r) for r in rows]


# === Agent DAG ===

def register_agent(sprint_id: str, agent_id: str, agent_type: str, agent_name: str,
                   model: str = "sonnet", group_id: str = None) -> str:
    with get_conn() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO agent_nodes
               (id, sprint_id, agent_type, agent_name, model, group_id, status, started_at)
               VALUES (?, ?, ?, ?, ?, ?, 'running', ?)""",
            (agent_id, sprint_id, agent_type, agent_name, model, group_id, now()),
        )
        audit(conn, "agent", agent_id, "created", actor="system")
    return agent_id


def update_agent(agent_id: str, **kwargs):
    allowed = {"status", "current_activity", "progress", "result_summary",
               "output_files", "completed_at", "duration_ms"}
    updates = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not updates:
        return
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    with get_conn() as conn:
        conn.execute(f"UPDATE agent_nodes SET {set_clause} WHERE id = ?",
                     list(updates.values()) + [agent_id])


def complete_agent(agent_id: str, summary: str = None):
    with get_conn() as conn:
        node = conn.execute("SELECT started_at FROM agent_nodes WHERE id=?", (agent_id,)).fetchone()
        duration = None
        if node and node["started_at"]:
            start = datetime.fromisoformat(node["started_at"])
            duration = int((datetime.now() - start).total_seconds() * 1000)
        conn.execute(
            "UPDATE agent_nodes SET status='done', completed_at=?, duration_ms=?, result_summary=? WHERE id=?",
            (now(), duration, summary, agent_id),
        )
        audit(conn, "agent", agent_id, "status_changed", "running", "done")


def log_activity(agent_id: str, activity_type: str, detail: str = None,
                 file_path: str = None, tool_name: str = None, duration_ms: int = None):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO agent_activity (agent_node_id, activity_type, detail, file_path, tool_name, duration_ms)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (agent_id, activity_type, detail, file_path, tool_name, duration_ms),
        )


def add_edge(from_agent: str, to_agent: str, edge_type: str, data_flow: str = None):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO agent_edges (from_agent, to_agent, edge_type, data_flow) VALUES (?, ?, ?, ?)",
            (from_agent, to_agent, edge_type, data_flow),
        )


def get_dag(sprint_id: str) -> dict:
    with get_conn() as conn:
        nodes = [dict(r) for r in conn.execute(
            "SELECT * FROM agent_nodes WHERE sprint_id=?", (sprint_id,)).fetchall()]
        node_ids = [n["id"] for n in nodes]
        if node_ids:
            placeholders = ",".join("?" * len(node_ids))
            edges = [dict(r) for r in conn.execute(
                f"SELECT * FROM agent_edges WHERE from_agent IN ({placeholders})",
                node_ids).fetchall()]
        else:
            edges = []
    return {"nodes": nodes, "edges": edges}


def list_agents(sprint_id: str = None, status: str = None) -> list:
    clauses, params = [], []
    if sprint_id:
        clauses.append("sprint_id = ?"); params.append(sprint_id)
    if status:
        clauses.append("status = ?"); params.append(status)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(
            f"SELECT * FROM agent_nodes {where} ORDER BY started_at", params).fetchall()]


def get_agent_activity(agent_id: str, limit: int = 50) -> list:
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM agent_activity WHERE agent_node_id=? ORDER BY timestamp DESC LIMIT ?",
            (agent_id, limit)).fetchall()]


# === Verification ===

def log_verification(sprint_id: str, wp_id: str, constraint_id: str, level: str,
                     result: str, score: float = None, iteration: int = None,
                     raw_output: str = None, failure_reason: str = None):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO verification_log
               (sprint_id, wp_id, constraint_id, level, result, score, iteration, raw_output, failure_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (sprint_id, wp_id, constraint_id, level, result, score, iteration, raw_output, failure_reason),
        )


# === Regression ===

def register_regression_test(project_id: str, scenario_id: str, description: str,
                             source_sprint: str, source_role: str = None,
                             test_type: str = "scenario", test_file: str = None,
                             test_command: str = None):
    with get_conn() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO regression_tests
               (project_id, scenario_id, description, source_sprint, source_role,
                test_type, test_file, test_command)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (project_id, scenario_id, description, source_sprint, source_role,
             test_type, test_file, test_command),
        )


def update_regression_result(project_id: str, scenario_id: str, result: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE regression_tests SET last_result=?, last_run_at=? WHERE project_id=? AND scenario_id=?",
            (result, now(), project_id, scenario_id),
        )


def list_regression_tests(project_id: str) -> list:
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM regression_tests WHERE project_id=? ORDER BY scenario_id",
            (project_id,)).fetchall()]


def regression_stats(project_id: str) -> dict:
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM regression_tests WHERE project_id=?", (project_id,)).fetchone()[0]
        passing = conn.execute(
            "SELECT COUNT(*) FROM regression_tests WHERE project_id=? AND last_result='pass'",
            (project_id,)).fetchone()[0]
        failing = conn.execute(
            "SELECT COUNT(*) FROM regression_tests WHERE project_id=? AND last_result='fail'",
            (project_id,)).fetchone()[0]
    return {"total": total, "passing": passing, "failing": failing, "untested": total - passing - failing}


# === Sprint Locks ===

def acquire_lock(sprint_id: str, session_id: str) -> bool:
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT * FROM sprint_locks WHERE sprint_id=? AND status='active'", (sprint_id,)
        ).fetchone()
        if existing:
            return False
        conn.execute(
            "INSERT OR REPLACE INTO sprint_locks (sprint_id, session_id, status, started_at, last_heartbeat) VALUES (?, ?, 'active', ?, ?)",
            (sprint_id, session_id, now(), now()),
        )
    return True


def release_lock(sprint_id: str):
    with get_conn() as conn:
        conn.execute("UPDATE sprint_locks SET status='released' WHERE sprint_id=?", (sprint_id,))


def force_unlock(sprint_id: str):
    with get_conn() as conn:
        conn.execute("UPDATE sprint_locks SET status='crashed' WHERE sprint_id=?", (sprint_id,))
        audit(conn, "sprint", sprint_id, "force_unlocked", actor="user")


def heartbeat(sprint_id: str):
    with get_conn() as conn:
        conn.execute("UPDATE sprint_locks SET last_heartbeat=? WHERE sprint_id=? AND status='active'",
                     (now(), sprint_id))


def check_lock(sprint_id: str) -> dict:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM sprint_locks WHERE sprint_id=?", (sprint_id,)).fetchone()
        return dict(row) if row else None


# === Audit ===

def audit(conn, entity_type: str, entity_id: str, action: str,
          old_value: str = None, new_value: str = None, actor: str = "system"):
    conn.execute(
        "INSERT INTO audit_log (entity_type, entity_id, action, old_value, new_value, actor) VALUES (?, ?, ?, ?, ?, ?)",
        (entity_type, entity_id, action, old_value, new_value, actor),
    )


def get_events(sprint_id: str = None, agent_id: str = None, limit: int = 20) -> list:
    with get_conn() as conn:
        if agent_id:
            return [dict(r) for r in conn.execute(
                "SELECT * FROM agent_activity WHERE agent_node_id=? ORDER BY timestamp DESC LIMIT ?",
                (agent_id, limit)).fetchall()]
        elif sprint_id:
            return [dict(r) for r in conn.execute(
                """SELECT a.* FROM agent_activity a
                   JOIN agent_nodes n ON a.agent_node_id = n.id
                   WHERE n.sprint_id = ? ORDER BY a.timestamp DESC LIMIT ?""",
                (sprint_id, limit)).fetchall()]
        else:
            return [dict(r) for r in conn.execute(
                "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()]


# === Helpers ===

def now() -> str:
    return datetime.now().isoformat()
