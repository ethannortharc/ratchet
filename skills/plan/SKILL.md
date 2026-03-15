---
name: plan
description: Decompose spec.yaml into executable work packages with dependencies, parallel groups, ratchet config, and verification criteria. Use after /ratchet:spec, or when the user wants to break down a task. Creates plan.yaml with dependency graph and execution strategy.
---

# Plan — Work Package Decomposition

## Prerequisites
`.ratchet/spec.yaml` must exist. If not, suggest `/ratchet:spec`.

## Workflow

1. **Read spec** — understand project type, constraints, environment, quality dimensions
2. **Create wp-00 (environment prep)** if spec identified tools to install. Agent-executable tasks go in wp-00; things needing human action get flagged.
3. **Decompose by project type**:
   - Software: by component/module, each producing a testable unit
   - Creative writing: settings → characters → outline → chapters (sliding window parallel) → consistency review → editing
   - Research: per-dimension data collection (parallel) → synthesis → conclusions
4. **Assign per-WP ratchet config**: inherit defaults from spec, adjust by WP complexity
5. **Dependency analysis**: `depends_on`, `parallel_group`, `inputs`, `outputs`
6. **Execution strategy**: identify critical path, parallel opportunities, sliding windows

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
      - id: string          # Maps to spec constraint
        track: agent | human
        verifier: auto | ai_review | human
        check: string
        ratchet_metric: string
    status: pending | running | agent_complete | human_review | done | failed
```

## Rules
1. Don't over-decompose. < 5 min for agent = too small, merge it.
2. Every acceptance criterion traces to a spec constraint.
3. Include summary generation between sequential creative writing groups.
4. Agent-track constraints stay on agent WPs. Human-track items get queued separately.

## Present Plan
Show visual summary with phases, parallel groups, critical path, and estimated ratchet cycles.
