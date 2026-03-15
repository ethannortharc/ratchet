---
name: plan
description: Decompose Intent Spec into executable work packages with dependencies, parallel groups, ratchet config, and verification criteria. Generates test suite as the first work package so the ratchet loop has real signals from iteration 1. Use after /ratchet:spec, or when the user wants to break down a task.
---

# Plan — Work Package Decomposition

## Prerequisites
`.ratchet/spec.yaml` (Intent Spec) must exist. If not, suggest `/ratchet:spec`.

## Workflow

### 1. Read Intent Spec

Understand project type, constraints, environment, quality dimensions, and `test_method` fields.

### 2. Create wp-00: Environment Prep (if needed)

If the Intent Spec identified tools to install or environment setup needed:
- Agent-executable tasks go in wp-00
- Things needing human action get flagged

### 3. Create wp-01: Test Suite Generation

**This is the key change.** Before any implementation work, generate the test suite based on constraint `test_method` fields.

```yaml
- id: wp-01  # or wp-00 if no env prep needed
  name: "Generate test suite"
  description: |
    Generate tests for all auto-verifiable constraints using their test_method descriptions.
    Tests should be runnable but failing (TDD: red phase).
  depends_on: [wp-00]  # if env prep exists
  parallel_group: A
  inputs: [spec.yaml]
  outputs: [test files]
  executor: claude-code
  ratchet:
    budget: 3  # Test generation is straightforward
    composite_weights:
      test_validity: 1.0
  acceptance:
    - id: TEST-SUITE
      track: agent
      verifier: auto
      check: "[test runner] --dry-run"  # Tests exist and parse, but may fail
      ratchet_metric: "valid_tests / total_constraints"
```

**How to generate tests:**
1. For each constraint with `verifier: auto`, read its `test_method`
2. Generate test files using `tools_required` (e.g., vitest, pytest, go test)
3. Tests should cover all scenarios described in `test_method`
4. Tests will FAIL initially — that's correct (red phase of TDD)
5. Verify tests are syntactically valid and can be discovered by the test runner

### 4. Decompose Implementation Work Packages

After test suite, decompose by project type:
- **Software**: by component/module, each producing a testable unit
- **Creative writing**: settings → characters → outline → chapters (sliding window parallel) → consistency review → editing
- **Research**: per-dimension data collection (parallel) → synthesis → conclusions

### 5. Assign Per-WP Ratchet Config

Inherit defaults from Intent Spec, adjust by WP complexity.

### 6. Dependency Analysis

Define `depends_on`, `parallel_group`, `inputs`, `outputs` for each WP.

### 7. Execution Strategy

Identify critical path, parallel opportunities, sliding windows.

## Plan Schema

```yaml
plan:
  project: string
  created: datetime
  strategy: parallel | sequential | sliding_window

work_packages:
  - id: string              # wp-00, wp-01, ...
    name: string
    description: string
    depends_on: [string]
    parallel_group: string   # A, B, C-1, C-2, ...
    inputs: [string]
    outputs: [string]
    executor: claude-code | claude-api | codex
    ratchet:
      budget: int
      composite_weights: {metric: weight}
    acceptance:
      - id: string          # Maps to Intent Spec constraint
        track: agent | human
        verifier: auto | ai_review | human
        check: string
        ratchet_metric: string
    status: pending | running | agent_complete | human_review | done | failed
```

## Rules

1. **Test suite is always a work package.** Never skip it. The ratchet loop needs real signals from iteration 1.
2. Don't over-decompose. < 5 min for agent = too small, merge it.
3. Every acceptance criterion traces to an Intent Spec constraint.
4. Include summary generation between sequential creative writing groups.
5. Agent-track constraints stay on agent WPs. Human-track items get queued separately.

## Present Plan

Show visual summary with phases, parallel groups, critical path, and estimated ratchet cycles. Highlight that the test suite WP runs first.
