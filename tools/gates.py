"""Ratchet Gates — Deterministic gate checks for sprint step transitions.

Each gate is a set of file/state checks that MUST pass before proceeding.
Gates are code, not LLM judgment. They cannot be skipped or overridden by agents.
"""

import os
import json
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


class GateResult:
    def __init__(self, step: str):
        self.step = step
        self.checks = []
        self.passed = True

    def check(self, name: str, condition: bool, detail: str = ""):
        self.checks.append({"name": name, "passed": condition, "detail": detail})
        if not condition:
            self.passed = False

    def to_dict(self) -> dict:
        return {
            "step": self.step,
            "passed": self.passed,
            "checks": self.checks,
            "passed_count": sum(1 for c in self.checks if c["passed"]),
            "total_count": len(self.checks),
        }

    def summary(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        lines = [f"{status}: {self.passed_count}/{self.total_count} checks passed"]
        for c in self.checks:
            mark = "✓" if c["passed"] else "✗"
            detail = f" — {c['detail']}" if c["detail"] and not c["passed"] else ""
            lines.append(f"  {mark} {c['name']}{detail}")
        return "\n".join(lines)

    @property
    def passed_count(self):
        return sum(1 for c in self.checks if c["passed"])

    @property
    def total_count(self):
        return len(self.checks)


def _load_yaml(path: str):
    """Load YAML file. Falls back to treating as plain text if PyYAML not installed."""
    if yaml:
        with open(path) as f:
            return yaml.safe_load(f)
    # Fallback: try json (some yaml is valid json)
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


def _yaml_valid(path: str) -> bool:
    try:
        result = _load_yaml(path)
        return result is not None
    except Exception:
        return False


def _file_exists(path: str) -> bool:
    return os.path.isfile(path)


def _dir_exists(path: str) -> bool:
    return os.path.isdir(path)


def check_gate(sprint_dir: str, step_name: str) -> GateResult:
    """Run gate check for a sprint step. Returns GateResult with pass/fail details."""
    checkers = {
        "spec": _gate_spec,
        "preparation": _gate_preparation,
        "eva": _gate_eva,
        "planning": _gate_planning,
        "execution": _gate_execution,
        "regression": _gate_regression,
        "acceptance": _gate_acceptance,
        "finalize": _gate_finalize,
    }
    checker = checkers.get(step_name)
    if not checker:
        result = GateResult(step_name)
        result.check("unknown_step", False, f"No gate defined for step '{step_name}'")
        return result
    return checker(sprint_dir)


def _gate_spec(sprint_dir: str) -> GateResult:
    g = GateResult("spec")
    spec_path = os.path.join(sprint_dir, "spec.yaml")
    g.check("spec.yaml exists", _file_exists(spec_path))
    if _file_exists(spec_path):
        g.check("spec.yaml valid YAML", _yaml_valid(spec_path))
        try:
            spec = _load_yaml(spec_path)
            invariants = spec.get("invariants", [])
            qds = spec.get("quality_dimensions", [])
            all_constraints = invariants + qds
            missing_tm = [c["id"] for c in all_constraints if not c.get("test_method")]
            g.check("all constraints have test_method",
                     len(missing_tm) == 0,
                     f"missing: {', '.join(missing_tm)}" if missing_tm else "")
            decisions = spec.get("decisions", {})
            unresolved = decisions.get("human_must_decide", [])
            g.check("human decisions resolved",
                     len(unresolved) == 0,
                     f"{len(unresolved)} unresolved" if unresolved else "")
        except Exception as e:
            g.check("spec.yaml parseable", False, str(e))
    g.check("backlog-items.yaml exists",
             _file_exists(os.path.join(sprint_dir, "backlog-items.yaml")))
    return g


def _gate_preparation(sprint_dir: str) -> GateResult:
    g = GateResult("preparation")
    g.check("pre-validation.log exists",
             _file_exists(os.path.join(sprint_dir, "pre-validation.log")))
    manifest_path = os.path.join(sprint_dir, "test-suite", "manifest.yaml")
    g.check("test-suite/manifest.yaml exists", _file_exists(manifest_path))
    if _file_exists(manifest_path):
        g.check("manifest valid YAML", _yaml_valid(manifest_path))
    g.check("test-suite directory has files",
             _dir_exists(os.path.join(sprint_dir, "test-suite")) and
             len(os.listdir(os.path.join(sprint_dir, "test-suite"))) > 1)
    return g


def _gate_eva(sprint_dir: str) -> GateResult:
    g = GateResult("eva")
    log_path = os.path.join(sprint_dir, "pre-validation.log")
    g.check("pre-validation.log exists", _file_exists(log_path))
    if _file_exists(log_path):
        content = open(log_path).read()
        g.check("no blockers in pre-validation",
                 "BLOCKER" not in content.upper(),
                 "pre-validation.log contains BLOCKER")
    return g


def _gate_planning(sprint_dir: str) -> GateResult:
    g = GateResult("planning")
    plan_path = os.path.join(sprint_dir, "plan.yaml")
    g.check("plan.yaml exists", _file_exists(plan_path))
    if _file_exists(plan_path):
        g.check("plan.yaml valid YAML", _yaml_valid(plan_path))
        try:
            plan = _load_yaml(plan_path)
            wps = plan.get("work_packages", [])
            g.check("at least one work package", len(wps) > 0)
            missing_ac = [wp["id"] for wp in wps if not wp.get("acceptance_criteria")]
            g.check("all WPs have acceptance_criteria",
                     len(missing_ac) == 0,
                     f"missing: {', '.join(missing_ac)}" if missing_ac else "")
        except Exception as e:
            g.check("plan.yaml parseable", False, str(e))
    return g


def _gate_execution(sprint_dir: str) -> GateResult:
    g = GateResult("execution")
    proofs_dir = os.path.join(sprint_dir, "proofs")
    g.check("proofs directory exists", _dir_exists(proofs_dir))
    if _dir_exists(proofs_dir):
        proofs = [f for f in os.listdir(proofs_dir) if f.endswith(".md")]
        g.check("at least one proof document", len(proofs) > 0,
                 f"found {len(proofs)} proofs")
    # Check plan to count expected WPs
    plan_path = os.path.join(sprint_dir, "plan.yaml")
    if _file_exists(plan_path):
        try:
            plan = _load_yaml(plan_path)
            expected_wps = len(plan.get("work_packages", []))
            actual_proofs = len(proofs) if _dir_exists(proofs_dir) else 0
            g.check("all WPs have proofs",
                     actual_proofs >= expected_wps,
                     f"{actual_proofs}/{expected_wps} proofs")
        except Exception:
            pass
    return g


def _gate_regression(sprint_dir: str) -> GateResult:
    g = GateResult("regression")
    # Check if regression directory exists at project level
    ratchet_dir = Path(sprint_dir).parent.parent  # sprints/sprint-N -> .ratchet
    regression_dir = ratchet_dir / "regression"
    if regression_dir.exists():
        last_run = regression_dir / "last-run.yaml"
        g.check("regression/last-run.yaml exists", last_run.exists())
        if last_run.exists():
            try:
                results = _load_yaml(str(last_run))
                failed = results.get("failed", 0) if results else 0
                g.check("all regression tests pass", failed == 0,
                         f"{failed} tests failed")
            except Exception:
                g.check("last-run.yaml parseable", False)
    else:
        # No regression suite yet (first sprint) — pass
        g.check("regression suite exists (or first sprint)", True, "first sprint, no regression yet")
    return g


def _gate_acceptance(sprint_dir: str) -> GateResult:
    g = GateResult("acceptance")
    acceptance_dir = os.path.join(sprint_dir, "acceptance")
    g.check("acceptance directory exists", _dir_exists(acceptance_dir))
    summary_path = os.path.join(acceptance_dir, "summary.md")
    g.check("acceptance/summary.md exists", _file_exists(summary_path))
    if _file_exists(summary_path):
        content = open(summary_path).read()
        g.check("PM verdict present",
                 "verdict" in content.lower() or "ready" in content.lower(),
                 "summary.md missing verdict section")
    return g


def _gate_finalize(sprint_dir: str) -> GateResult:
    g = GateResult("finalize")
    # Regression must be passing
    reg_result = _gate_regression(sprint_dir)
    g.check("regression passing", reg_result.passed)
    # Acceptance must be done
    acc_result = _gate_acceptance(sprint_dir)
    g.check("acceptance complete", acc_result.passed)
    return g
