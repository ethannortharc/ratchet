#!/usr/bin/env python3
"""Ratchet CLI — Deterministic process management for multi-agent collaboration.

This tool handles state, gates, coordination, and tracking.
Creative work is done by Claude Code agents.
This tool ensures consistency that LLMs cannot guarantee alone.

Usage: python tools/ratchet.py <command> [args]
"""

import sys
import os
import json
import uuid
import argparse
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

import db
import gates


def cmd_init(args):
    """Initialize a new Ratchet project."""
    workspace = os.getcwd()
    project_id = args.id or args.name.lower().replace(" ", "-")
    db_path = db.init_db(workspace)
    project = db.create_project(project_id, args.name, workspace, args.mode)

    # Create directory structure
    ratchet_dir = Path(workspace) / ".ratchet"
    (ratchet_dir / "story" / "perspectives").mkdir(parents=True, exist_ok=True)
    (ratchet_dir / "story" / "synthesis").mkdir(parents=True, exist_ok=True)
    (ratchet_dir / "sprints").mkdir(parents=True, exist_ok=True)
    (ratchet_dir / "regression").mkdir(parents=True, exist_ok=True)

    print(f"Initialized project '{args.name}' ({project_id})")
    print(f"  Workspace: {workspace}")
    print(f"  Mode: {args.mode}")
    print(f"  DB: {db_path}")


def cmd_status(args):
    """Show project status."""
    project = db.get_project()
    if not project:
        print("No project initialized. Run: python tools/ratchet.py init \"Project Name\"")
        return

    sprints = db.list_sprints(project["id"])
    stats = db.backlog_stats(project["id"])

    fmt = args.format if hasattr(args, "format") else "text"
    if fmt == "json":
        print(json.dumps({
            "project": project,
            "sprints": sprints,
            "backlog": stats,
        }, indent=2, default=str))
        return

    print(f"Project: {project['name']} ({project['id']})")
    print(f"Status: {project['status']} | Mode: {project['mode']}")
    print()

    # Backlog
    print(f"Backlog: {stats['total']} items")
    for p in ["must", "should", "could", "wont"]:
        count = stats["by_priority"].get(p, 0)
        if count:
            print(f"  {p}: {count}")
    print()

    # Sprints
    if sprints:
        for s in sprints:
            wps = db.list_wps(s["id"])
            done_wps = sum(1 for w in wps if w["status"] == "done")
            total_wps = len(wps)
            wp_info = f" ({done_wps}/{total_wps} WPs)" if wps else ""
            print(f"  {s['id']}: {s['name']} [{s['status']}]{wp_info}")

            if s["status"] == "executing":
                steps = db.list_steps(s["id"])
                for step in steps:
                    if step["status"] == "in_progress":
                        print(f"    Current step: {step['step_name']}")
                running_agents = db.list_agents(sprint_id=s["id"], status="running")
                for agent in running_agents:
                    activity = agent.get("current_activity", "")
                    print(f"    Active: {agent['agent_name']} — {activity}")

                lock = db.check_lock(s["id"])
                if lock and lock["status"] == "active":
                    print(f"    Lock: session {lock['session_id'][:8]}...")
    else:
        print("  No sprints yet.")


def cmd_backlog_add(args):
    """Add a backlog item."""
    project = db.get_project()
    if not project:
        print("ERROR: No project initialized.")
        return
    roles = args.roles.split(",") if hasattr(args, "roles") and args.roles else None
    item_id = db.add_backlog(
        project["id"], args.type, args.title,
        description=args.description,
        priority=args.priority,
        source=args.source or "user_report",
        source_sprint=getattr(args, "sprint", None),
        source_wp=getattr(args, "wp", None),
        source_roles=roles,
    )
    print(f"Created: {item_id} [{args.type}] [{args.priority}] {args.title}")


def cmd_backlog_list(args):
    """List backlog items."""
    project = db.get_project()
    if not project:
        print("ERROR: No project initialized.")
        return
    items = db.list_backlog(
        project["id"],
        status=getattr(args, "status", None),
        priority=getattr(args, "priority", None),
        item_type=getattr(args, "type", None),
    )
    if not items:
        print("Backlog is empty.")
        return
    for item in items:
        sprint = f" → {item['planned_sprint']}" if item.get("planned_sprint") else ""
        print(f"  {item['id']} [{item['type']}] [{item['priority']}] {item['status']}{sprint}")
        print(f"    {item['title']}")


def cmd_backlog_update(args):
    """Update a backlog item."""
    kwargs = {}
    if args.priority:
        kwargs["priority"] = args.priority
    if args.status:
        kwargs["status"] = args.status
    if args.decision:
        kwargs["decision"] = args.decision
    if hasattr(args, "sprint") and args.sprint:
        kwargs["planned_sprint"] = args.sprint
    db.update_backlog(args.id, **kwargs)
    print(f"Updated: {args.id}")


def cmd_backlog_stats(args):
    """Show backlog statistics."""
    project = db.get_project()
    if not project:
        print("ERROR: No project initialized.")
        return
    stats = db.backlog_stats(project["id"])
    print(json.dumps(stats, indent=2))


def cmd_sprint_create(args):
    """Create a new sprint."""
    project = db.get_project()
    if not project:
        print("ERROR: No project initialized.")
        return
    deps = args.depends_on.split(",") if hasattr(args, "depends_on") and args.depends_on else None
    sprint_id = db.create_sprint(
        project["id"], args.id, args.name,
        points=args.points or 0,
        sprint_type=args.type or "normal",
        depends_on=deps,
    )
    # Create sprint directory
    sprint_dir = Path(project["workspace"]) / ".ratchet" / "sprints" / sprint_id
    sprint_dir.mkdir(parents=True, exist_ok=True)
    (sprint_dir / "test-suite").mkdir(exist_ok=True)
    (sprint_dir / "scenario-tests").mkdir(exist_ok=True)
    (sprint_dir / "proofs").mkdir(exist_ok=True)
    (sprint_dir / "acceptance").mkdir(exist_ok=True)
    (sprint_dir / "agent-logs").mkdir(exist_ok=True)
    (sprint_dir / "reports").mkdir(exist_ok=True)
    print(f"Created sprint: {sprint_id} ({args.name})")


def cmd_sprint_list(args):
    """List all sprints."""
    sprints = db.list_sprints()
    if not sprints:
        print("No sprints.")
        return
    for s in sprints:
        print(f"  {s['id']}: {s['name']} [{s['status']}] {s['points'] or '?'}pts")


def cmd_sprint_status(args):
    """Show sprint detail."""
    sprint = db.get_sprint(args.id)
    if not sprint:
        print(f"Sprint {args.id} not found.")
        return
    print(f"Sprint: {sprint['id']} — {sprint['name']}")
    print(f"Status: {sprint['status']} | Points: {sprint['points']}")
    print()
    steps = db.list_steps(args.id)
    for step in steps:
        mark = {"done": "✓", "in_progress": "⟳", "failed": "✗", "pending": "○", "skipped": "—"}
        print(f"  {mark.get(step['status'], '?')} {step['step_name']}: {step['status']}")
    print()
    wps = db.list_wps(args.id)
    if wps:
        print("Work Packages:")
        for wp in wps:
            print(f"  {wp['id']}: {wp['name']} [{wp['status']}] iter={wp['iteration']} score={wp['best_score']}")


def cmd_sprint_lock(args):
    """Acquire sprint execution lock."""
    session_id = os.environ.get("CLAUDE_SESSION_ID", str(uuid.uuid4())[:8])
    ok = db.acquire_lock(args.id, session_id)
    if ok:
        print(f"Lock acquired for {args.id} (session: {session_id})")
    else:
        lock = db.check_lock(args.id)
        print(f"ERROR: Sprint {args.id} locked by session {lock['session_id']}")
        print(f"  Started: {lock['started_at']}")
        print(f"  Heartbeat: {lock['last_heartbeat']}")
        print(f"  Use: python tools/ratchet.py sprint force-unlock {args.id}")


def cmd_sprint_unlock(args):
    """Release sprint execution lock."""
    db.release_lock(args.id)
    print(f"Lock released for {args.id}")


def cmd_sprint_force_unlock(args):
    """Force unlock a crashed sprint."""
    db.force_unlock(args.id)
    print(f"Force unlocked {args.id}")


def cmd_sprint_heartbeat(args):
    """Update sprint heartbeat."""
    db.heartbeat(args.id)


def cmd_step_start(args):
    """Mark a sprint step as started."""
    db.start_step(args.sprint, args.step)
    print(f"Step started: {args.sprint}/{args.step}")


def cmd_step_complete(args):
    """Mark a sprint step as completed."""
    db.complete_step(args.sprint, args.step)
    print(f"Step completed: {args.sprint}/{args.step}")


def cmd_gate_check(args):
    """Run gate check for a sprint step."""
    project = db.get_project()
    if not project:
        print("ERROR: No project initialized.")
        sys.exit(1)
    sprint_dir = os.path.join(project["workspace"], ".ratchet", "sprints", args.sprint)
    result = gates.check_gate(sprint_dir, args.step)
    print(result.summary())
    # Store gate result in DB
    if result.passed:
        db.complete_step(args.sprint, args.step, gate_result=result.to_dict())
    else:
        db.fail_step(args.sprint, args.step, reason=json.dumps(result.to_dict()))
    sys.exit(0 if result.passed else 1)


def cmd_wp_start(args):
    """Mark a WP as started."""
    db.update_wp(args.sprint, args.wp, status="in_progress")
    print(f"WP started: {args.sprint}/{args.wp}")


def cmd_wp_update(args):
    """Update WP status/score."""
    kwargs = {}
    if args.status:
        kwargs["status"] = args.status
    if args.score is not None:
        kwargs["best_score"] = args.score
    if args.iteration is not None:
        kwargs["iteration"] = args.iteration
    if args.failure:
        kwargs["current_failure"] = args.failure
    db.update_wp(args.sprint, args.wp, **kwargs)
    print(f"WP updated: {args.sprint}/{args.wp}")


def cmd_wp_list(args):
    """List WPs for a sprint."""
    wps = db.list_wps(args.sprint)
    for wp in wps:
        print(f"  {wp['id']}: {wp['name']} [{wp['status']}] iter={wp['iteration']} score={wp['best_score']}")


def cmd_ratchet_decide(args):
    """Make ratchet keep/discard decision based on score comparison."""
    wps = db.list_wps(args.sprint)
    wp = next((w for w in wps if w["id"] == args.wp), None)
    if not wp:
        print(f"ERROR: WP {args.wp} not found in {args.sprint}")
        sys.exit(1)
    old_score = wp["best_score"] or 0.0
    new_score = args.score
    if new_score > old_score:
        db.update_wp(args.sprint, args.wp, best_score=new_score)
        print(f"KEEP (improved: {old_score:.2f} → {new_score:.2f})")
    else:
        print(f"DISCARD (no improvement: {old_score:.2f} >= {new_score:.2f})")
        sys.exit(1)  # Non-zero exit = discard


def cmd_agent_register(args):
    """Register an agent in the DAG."""
    agent_id = f"{args.sprint}:{args.name.lower().replace(' ', '-')}"
    db.register_agent(args.sprint, agent_id, args.type, args.name,
                      model=args.model or "sonnet", group_id=getattr(args, "group", None))
    print(f"Agent registered: {agent_id}")


def cmd_agent_update(args):
    """Update agent status/activity."""
    kwargs = {}
    if args.status:
        kwargs["status"] = args.status
    if args.activity:
        kwargs["current_activity"] = args.activity
    if args.progress:
        kwargs["progress"] = args.progress
    db.update_agent(args.id, **kwargs)


def cmd_agent_complete(args):
    """Mark agent as completed."""
    db.complete_agent(args.id, summary=getattr(args, "summary", None))
    print(f"Agent completed: {args.id}")


def cmd_agent_log(args):
    """Log agent activity."""
    db.log_activity(args.id, args.activity_type, detail=args.detail,
                    file_path=getattr(args, "file", None))


def cmd_agent_dag(args):
    """Show agent DAG for a sprint."""
    dag = db.get_dag(args.sprint)
    if not dag["nodes"]:
        print(f"No agents registered for {args.sprint}")
        return
    print(f"Agent DAG for {args.sprint}:")
    for node in dag["nodes"]:
        mark = {"done": "✓", "running": "⟳", "pending": "○", "failed": "✗"}.get(node["status"], "?")
        activity = f" — {node['current_activity']}" if node.get("current_activity") else ""
        print(f"  {mark} {node['agent_name']} ({node['model']}){activity}")
    if dag["edges"]:
        print("\nEdges:")
        for edge in dag["edges"]:
            print(f"  {edge['from_agent']} → {edge['to_agent']} ({edge['edge_type']})")


def cmd_agent_list(args):
    """List agents."""
    agents = db.list_agents(
        sprint_id=getattr(args, "sprint", None),
        status=getattr(args, "status", None),
    )
    for a in agents:
        activity = f" — {a['current_activity']}" if a.get("current_activity") else ""
        print(f"  {a['id']} [{a['status']}] {a['agent_name']}{activity}")


def cmd_events(args):
    """Show recent events."""
    events = db.get_events(
        sprint_id=getattr(args, "sprint", None),
        agent_id=getattr(args, "agent", None),
        limit=getattr(args, "limit", 20),
    )
    for e in events:
        ts = e.get("timestamp", "")[:19]
        if "activity_type" in e:
            detail = e.get("detail", "")[:80]
            print(f"  {ts}  {e['activity_type']}  {detail}")
        else:
            print(f"  {ts}  {e['entity_type']}:{e['entity_id']}  {e['action']}")


def cmd_regression_run(args):
    """Run regression tests (placeholder — actual test execution by agent)."""
    project = db.get_project()
    if not project:
        print("ERROR: No project initialized.")
        return
    tests = db.list_regression_tests(project["id"])
    if not tests:
        print("No regression tests registered yet.")
        return
    print(f"Regression suite: {len(tests)} tests")
    for t in tests:
        result = t.get("last_result", "untested")
        print(f"  {t['scenario_id']}: {t['description']} [{result}]")
    print("\nNote: Actual test execution should be triggered by the agent.")
    print("This command shows the current state of the regression suite.")


def cmd_regression_register(args):
    """Register scenario tests from a sprint into the global regression suite."""
    project = db.get_project()
    if not project:
        print("ERROR: No project initialized.")
        return
    sprint_dir = Path(project["workspace"]) / ".ratchet" / "sprints" / args.sprint / "scenario-tests"
    if not sprint_dir.exists():
        print(f"No scenario-tests directory for {args.sprint}")
        return
    count = 0
    for test_file in sorted(sprint_dir.glob("*.test.*")):
        scenario_id = test_file.stem.split(".")[0]  # S-01.test.ts → S-01
        db.register_regression_test(
            project["id"], scenario_id,
            description=f"From {args.sprint}",
            source_sprint=args.sprint,
            test_file=str(test_file),
        )
        count += 1
    print(f"Registered {count} scenario tests from {args.sprint}")


def cmd_regression_status(args):
    """Show regression test status."""
    project = db.get_project()
    if not project:
        print("ERROR: No project initialized.")
        return
    stats = db.regression_stats(project["id"])
    print(f"Regression: {stats['passing']}/{stats['total']} passing, "
          f"{stats['failing']} failing, {stats['untested']} untested")


def cmd_version(args):
    """Show version."""
    print("ratchet-cli 6.0.0")


def main():
    parser = argparse.ArgumentParser(prog="ratchet", description="Ratchet process management CLI")
    sub = parser.add_subparsers(dest="command")

    # init
    p = sub.add_parser("init", help="Initialize project")
    p.add_argument("name", help="Project name")
    p.add_argument("--id", help="Project ID (default: derived from name)")
    p.add_argument("--mode", default="greenfield", choices=["greenfield", "existing"])
    p.set_defaults(func=cmd_init)

    # status
    p = sub.add_parser("status", help="Project status")
    p.add_argument("--json", dest="format", action="store_const", const="json", default="text")
    p.set_defaults(func=cmd_status)

    # version
    p = sub.add_parser("version", help="Show version")
    p.set_defaults(func=cmd_version)

    # backlog
    backlog = sub.add_parser("backlog", help="Backlog management")
    backlog_sub = backlog.add_subparsers(dest="backlog_cmd")

    p = backlog_sub.add_parser("add")
    p.add_argument("title")
    p.add_argument("description", nargs="?")
    p.add_argument("--type", default="feature", choices=["feature", "bug", "improvement", "unresolved", "test_gap", "tech_debt"])
    p.add_argument("--priority", default="should", choices=["must", "should", "could", "wont"])
    p.add_argument("--source", default="user_report")
    p.add_argument("--sprint")
    p.add_argument("--wp")
    p.add_argument("--roles")
    p.set_defaults(func=cmd_backlog_add)

    p = backlog_sub.add_parser("list")
    p.add_argument("--status")
    p.add_argument("--priority")
    p.add_argument("--type")
    p.set_defaults(func=cmd_backlog_list)

    p = backlog_sub.add_parser("update")
    p.add_argument("id")
    p.add_argument("--priority", choices=["must", "should", "could", "wont"])
    p.add_argument("--status", choices=["new", "prioritized", "planned", "executing", "done", "wont_do", "blocked"])
    p.add_argument("--decision")
    p.add_argument("--sprint")
    p.set_defaults(func=cmd_backlog_update)

    p = backlog_sub.add_parser("stats")
    p.set_defaults(func=cmd_backlog_stats)

    # sprint
    sprint = sub.add_parser("sprint", help="Sprint management")
    sprint_sub = sprint.add_subparsers(dest="sprint_cmd")

    p = sprint_sub.add_parser("create")
    p.add_argument("id")
    p.add_argument("name")
    p.add_argument("--points", type=int)
    p.add_argument("--type", default="normal", choices=["normal", "hotfix"])
    p.add_argument("--depends-on")
    p.set_defaults(func=cmd_sprint_create)

    p = sprint_sub.add_parser("list")
    p.set_defaults(func=cmd_sprint_list)

    p = sprint_sub.add_parser("status")
    p.add_argument("id")
    p.set_defaults(func=cmd_sprint_status)

    p = sprint_sub.add_parser("lock")
    p.add_argument("id")
    p.set_defaults(func=cmd_sprint_lock)

    p = sprint_sub.add_parser("unlock")
    p.add_argument("id")
    p.set_defaults(func=cmd_sprint_unlock)

    p = sprint_sub.add_parser("force-unlock")
    p.add_argument("id")
    p.set_defaults(func=cmd_sprint_force_unlock)

    p = sprint_sub.add_parser("heartbeat")
    p.add_argument("id")
    p.set_defaults(func=cmd_sprint_heartbeat)

    # step
    step = sub.add_parser("step", help="Step lifecycle")
    step_sub = step.add_subparsers(dest="step_cmd")

    p = step_sub.add_parser("start")
    p.add_argument("sprint")
    p.add_argument("step")
    p.set_defaults(func=cmd_step_start)

    p = step_sub.add_parser("complete")
    p.add_argument("sprint")
    p.add_argument("step")
    p.set_defaults(func=cmd_step_complete)

    # gate
    gate = sub.add_parser("gate", help="Gate checks")
    gate_sub = gate.add_subparsers(dest="gate_cmd")

    p = gate_sub.add_parser("check")
    p.add_argument("sprint")
    p.add_argument("step")
    p.set_defaults(func=cmd_gate_check)

    # wp
    wp = sub.add_parser("wp", help="Work package management")
    wp_sub = wp.add_subparsers(dest="wp_cmd")

    p = wp_sub.add_parser("start")
    p.add_argument("sprint")
    p.add_argument("wp")
    p.set_defaults(func=cmd_wp_start)

    p = wp_sub.add_parser("update")
    p.add_argument("sprint")
    p.add_argument("wp")
    p.add_argument("--status")
    p.add_argument("--score", type=float)
    p.add_argument("--iteration", type=int)
    p.add_argument("--failure")
    p.set_defaults(func=cmd_wp_update)

    p = wp_sub.add_parser("list")
    p.add_argument("sprint")
    p.set_defaults(func=cmd_wp_list)

    # ratchet decide
    ratchet_cmd = sub.add_parser("ratchet", help="Ratchet decisions")
    ratchet_sub = ratchet_cmd.add_subparsers(dest="ratchet_cmd")

    p = ratchet_sub.add_parser("decide")
    p.add_argument("sprint")
    p.add_argument("wp")
    p.add_argument("--score", type=float, required=True)
    p.set_defaults(func=cmd_ratchet_decide)

    # agent
    agent = sub.add_parser("agent", help="Agent DAG management")
    agent_sub = agent.add_subparsers(dest="agent_cmd")

    p = agent_sub.add_parser("register")
    p.add_argument("sprint")
    p.add_argument("type")
    p.add_argument("name")
    p.add_argument("--model", default="sonnet")
    p.add_argument("--group")
    p.set_defaults(func=cmd_agent_register)

    p = agent_sub.add_parser("update")
    p.add_argument("id")
    p.add_argument("--status")
    p.add_argument("--activity")
    p.add_argument("--progress")
    p.set_defaults(func=cmd_agent_update)

    p = agent_sub.add_parser("complete")
    p.add_argument("id")
    p.add_argument("--summary")
    p.set_defaults(func=cmd_agent_complete)

    p = agent_sub.add_parser("log")
    p.add_argument("id")
    p.add_argument("activity_type")
    p.add_argument("detail", nargs="?")
    p.add_argument("--file")
    p.set_defaults(func=cmd_agent_log)

    p = agent_sub.add_parser("dag")
    p.add_argument("sprint")
    p.set_defaults(func=cmd_agent_dag)

    p = agent_sub.add_parser("list")
    p.add_argument("--sprint")
    p.add_argument("--status")
    p.set_defaults(func=cmd_agent_list)

    # events
    p = sub.add_parser("events", help="Event log")
    p.add_argument("--sprint")
    p.add_argument("--agent")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_events)

    # regression
    regression = sub.add_parser("regression", help="Regression testing")
    reg_sub = regression.add_subparsers(dest="reg_cmd")

    p = reg_sub.add_parser("run")
    p.set_defaults(func=cmd_regression_run)

    p = reg_sub.add_parser("register")
    p.add_argument("sprint")
    p.set_defaults(func=cmd_regression_register)

    p = reg_sub.add_parser("status")
    p.set_defaults(func=cmd_regression_status)

    # Parse and execute
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
