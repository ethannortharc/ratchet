---
name: plan
description: Decompose spec into executable work packages using Python tools. Reads spec.yaml, creates WPs in DB, writes plan.yaml content file, and runs planning gate check.
---

# Plan — Work Package Decomposition

## Prerequisites

- `spec.yaml` must exist (from `/ratchet:spec`). If not, suggest running spec first.
- Story artifacts in `.ratchet/story/` should exist for full context.

## Workflow

### 1. Read Spec

Read `spec.yaml` to understand project type, constraints, and requirements.

### 2. Decompose into Work Packages

Decompose by project type:
- **Software**: by component/module, each producing a testable unit
- **Creative writing**: settings -> characters -> outline -> chapters -> consistency review -> editing
- **Research**: per-dimension data collection (parallel) -> synthesis -> conclusions

Include wp-00 (Environment Prep) if the spec identified tools to install or setup needed.

### 3. Register WPs in DB

For each work package:
```
python tools/ratchet.py wp create {sprint_id} {wp_id} "{name}"
```

### 4. Write plan.yaml

Write `plan.yaml` as a content file (not state — state lives in DB). Include:
- Work package list with descriptions, dependencies, parallel groups
- Execution strategy (parallel / sequential / sliding_window)
- Per-WP acceptance criteria referencing spec constraints

### 5. Gate Check

Run: `python tools/ratchet.py gate check {sprint_id} planning`

This verifies all planning prerequisites are met before execution can begin.

## Plan Schema (plan.yaml)

```yaml
plan:
  project: string
  sprint_id: string
  created: datetime
  strategy: parallel | sequential | sliding_window

work_packages:
  - id: string              # wp-00, wp-01, ...
    name: string
    description: string
    depends_on: [string]
    parallel_group: string
    inputs: [string]
    outputs: [string]
    acceptance:
      - id: string          # Maps to spec constraint
        track: agent | human
        verifier: auto | ai_review | human
        check: string
```

## Rules

1. Don't over-decompose. < 5 min for agent = too small, merge it.
2. Every acceptance criterion traces to a spec constraint.
3. Agent-track constraints stay on agent WPs. Human-track items get queued separately.
4. Present plan with visual summary showing phases, parallel groups, and critical path.
