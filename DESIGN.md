# Ratchet — Design Document

## Vision

Ratchet is an intent-driven execution framework. You describe what you want, the system autonomously iterates until it produces the best possible result, and you review only what matters.

The name comes from the core mechanism: like a ratchet wrench, progress only moves forward. Every iteration either improves the result (commit/keep) or doesn't (reset/discard). Over time, quality ratchets up monotonically.

## Core Philosophy

> Human provides direction and taste.
> Agent does everything else.
> Agent creates conditions to do more.
> What truly cannot be automated, human reviews.
> Each review makes the next project more autonomous.

1. **Two touchpoints.** Human interacts at exactly two points: spec (provide direction) and review (evaluate results). Everything between runs autonomously.

2. **Thorough spec.** No time limit. Section-by-section confirmation. Includes delivery/UI direction. The more invested here, the less rework later.

3. **Maximum coverage.** Agent aggressively maximizes auto-verification by requesting tools, running multi-level tests (static → unit → integration), and never leaving basic functionality to human review.

4. **EVA (Environment-Verification Architecture).** An agent's autonomy is bounded by its verification capability. Validate all verification infrastructure before execution. Install tools, scaffold project, dry-run test pipeline. Catch problems when they're cheap to fix.

5. **Ratchet loop.** Budget-limited, git-backed. Every iteration: execute → verify → improved? keep : discard → repeat.

6. **Subagent architecture.** Specialized subagents for parallel execution — environment preparation, test generation, WP execution, verification, report writing.

7. **Direct feedback.** User reports issues in conversation OR via `/ratchet:review`. Both trigger the same feedback → constraint → iteration loop. No forced ceremony.

8. **Proof of work.** Reports include raw verification outputs — actual test results, ai_review justifications — not just pass/fail counts.

## Architecture Overview

```
User: "I want to build X"
  │
  ▼
┌─────────────────────────────────────────────────────┐
│ Spec (human + agent, ~5-30 min)                     │
│   Intent convergence (2-3 decisions)                │
│   Generate Intent Spec (constraints + delivery/UI)  │
│   Thorough section-by-section review                │
│   Status: draft → active                            │
└──────────────────────┬──────────────────────────────┘
                       │
          === Human walks away ===
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│ Preparation (autonomous, parallel subagents)        │
│   env-preparer: install tools, scaffold, validate   │
│   test-generator: create test suite from test_method│
│   Main agent: EVA pipeline validation               │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│ Plan (autonomous)                                   │
│   Decompose into work packages                     │
│   Reference pre-generated test suite               │
│   Status: agent_running                             │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│ Execute (autonomous, execute skill orchestrates)    │
│                                                     │
│   Per WP: wp-executor → verifier → ratchet decision│
│     improved? → git commit (keep)                  │
│     not improved? → git reset (discard)            │
│     repeat until pass or budget exhausted          │
│                                                     │
│   report-writer: iteration report with proof of work│
│   Status: → agent_complete                          │
└──────────────────────┬──────────────────────────────┘
                       │
          === Agent notifies human ===
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│ Review (human + agent)                              │
│   /ratchet:review or direct conversation            │
│   Feedback → constraint conversion → new round      │
│   Status: → done or → agent_running (new round)     │
└─────────────────────────────────────────────────────┘
```

## Key Concepts

### Intent Spec (spec.yaml)

Structured representation of human intent. Contains:

- **Invariants**: Hard constraints with multi-level test_method (static → unit → integration)
- **Quality Dimensions**: Measurable targets with rubrics and thresholds
- **Preferences**: Soft guidance
- **Delivery**: UI/UX direction (key screens, user journey, mood) or CLI direction
- **agent_guidance**: Natural language prompt for agent context and stuck-recovery

Each constraint has: track, verifier, test_method, tools_required (structured), ratchet_metric.

### Workspace Management

Each intent registered in `~/.config/ratchet/state.yaml` with:
- Unique ID, absolute workspace path (locked at creation)
- Lifecycle state, ticket metadata (priority, tags, brief, current_blocker)

All operations stay within workspace. Commands accept optional intent ID.

### Intent Lifecycle

```
draft → active → agent_running → agent_complete → human_review → done
                      ↑                │
                      └── ratchet ──────┘

any → paused │ paused → active │ any → archived
```

### Subagent Architecture

| Agent | Model | Purpose |
|-------|-------|---------|
| env-preparer | sonnet | Install tools, scaffold, validate environment |
| test-generator | sonnet | Generate test suite from test_method fields |
| wp-executor | sonnet | Execute single WP within workspace |
| verifier | sonnet | 3-level verification + ai_review, composite score |
| report-writer | haiku | Generate iteration reports from logs |

Orchestration: env-preparer + test-generator run in parallel. Independent WPs run in parallel via multiple wp-executor instances.

### Multi-Level Verification

```
Level 1 — Static: build, lint, type-check
Level 2 — Unit: isolated function tests
Level 3 — Integration: actually run the artifact and verify behavior
```

Level 3 catches encoding errors, broken buttons, navigation failures — issues unit tests miss. Agent discovers available verification capabilities and aggressively recommends tools to enable Level 3 (browser testing in headless mode, HTTP clients, etc.).

### Feedback Paths

**Direct conversation:** User says "the button is broken" → agent runs feedback conversion engine → converts to auto-verifiable constraint → updates spec → fixes immediately.

**Formal review:** `/ratchet:review` processes accumulated queue items across intents.

Both trigger the same loop. Basic functionality bugs are acknowledged as agent failures and get auto-verifiable constraints added.

## File Layout

### Plugin
```
ratchet/
├── .claude-plugin/plugin.json
├── commands/                     # User-facing only
│   ├── spec.md                   # Start new intent
│   ├── review.md                 # Review results
│   ├── status.md                 # Check progress
│   ├── pause.md                  # Pause execution
│   └── resume.md                 # Resume execution
├── skills/                       # Internal workflows
│   ├── getting-started/SKILL.md
│   ├── spec/SKILL.md             # Main orchestrator
│   ├── plan/SKILL.md
│   ├── verify/SKILL.md
│   ├── execute/SKILL.md           # Ratchet loop orchestration
│   ├── update/SKILL.md
│   ├── review/SKILL.md
│   ├── status/SKILL.md
│   ├── report/SKILL.md
│   ├── profile/SKILL.md
│   ├── metrics/SKILL.md
│   ├── pause/SKILL.md
│   └── resume/SKILL.md
├── agents/                       # Subagents
│   ├── env-preparer.md
│   ├── test-generator.md
│   ├── wp-executor.md
│   ├── verifier.md
│   └── report-writer.md
├── hooks/hooks.json
├── references/
│   ├── spec-schema.md
│   ├── inquiry-protocols.md
│   ├── verifier-guide.md
│   └── feedback-patterns.md
├── templates/spec-template.yaml
├── DESIGN.md
└── README.md
```

### User Config
```
~/.config/ratchet/
├── profile.yaml
├── state.yaml                    # Global intent registry
├── review_queue.yaml
└── global_metrics.yaml
```

### Per-Intent Workspace
```
<workspace>/.ratchet/
└── {intent-id}/                  # Each intent gets its own subdirectory
    ├── spec.yaml
    ├── plan.yaml
    ├── test-suite/
    │   ├── manifest.yaml
    │   ├── auto/                 # Executable test files
    │   ├── ai-review/            # Review prompts
    │   └── human/                # Checklists
    ├── pre-validation.log
    ├── review_log.yaml
    ├── metrics.yaml
    ├── suggested_constraints.yaml
    ├── reports/
    │   ├── wp-{id}.md            # Per-WP, generated after each WP
    │   └── iter-{NNN}.md         # Summary, generated after all WPs in a round
    └── artifacts/
```

Multiple intents can share the same workspace directory. Each intent's artifacts are isolated in its own subdirectory (e.g., `.ratchet/prism-enneagram/`, `.ratchet/prism-mbti/`).

## Commands

| Command | Purpose |
|---------|---------|
| `/ratchet:spec` | Start new intent — everything chains from here |
| `/ratchet:review` | Review results, give feedback |
| `/ratchet:status` | Progress dashboard with metrics |
| `/ratchet:pause` | Pause execution |
| `/ratchet:resume` | Resume execution |

Internal skills (plan, verify, report, metrics, update, profile) are invoked by the agent automatically — users don't need to call them.

## Design Decisions

### Why only two human touchpoints?
Every additional human checkpoint is a bottleneck. Spec and review are the only steps where human judgment is irreplaceable. Plan, execute, verify, report — agent can handle all of these. If the spec is thorough, execution rarely needs human intervention.

### Why thorough spec with no time limit?
Changes during spec cost ≈ 0 (editing YAML). Changes during execution cost ratchet iterations. Changes during review cost spec bumps + re-execution. Front-loading specification is always cheaper.

### Why delivery/UI direction in spec?
For products with user interfaces, the interaction model IS the product. A single-page swipe quiz and a multi-page form are two different products. Not aligning on this during spec guarantees rework.

### Why subagents?
Context isolation: each subagent gets a clean context focused on one task. Cost optimization: wp-executor and verifier on Sonnet (focused tasks), report-writer on Haiku (summarization). Parallelism: independent WPs run simultaneously.

### Why EVA (Environment-Verification Architecture)?
An agent's autonomy is bounded by its verification capability. If it can verify its own work, it can iterate without human help. Practically: discovering that the test runner isn't configured on iteration 3 wastes 2 iterations. Validating the pipeline before execution catches these issues when they're trivial to fix.

### Why maximum coverage over convenient human review?
Every constraint on human-track is a delay. Agent should exhaust all options (install tools, write integration tests, discover browser testing capabilities) before falling back to human review. Basic functionality bugs reaching human review is a system failure.

### Why direct feedback?
Requiring `/ratchet:review` for every piece of feedback adds ceremony without value. When the user is actively in conversation and sees an issue, they should just say it. The feedback conversion engine is the same either way.

## Future Directions

- Review UI: browser-based spec review for large specs (>20 constraints)
- Desktop app: Tauri-based UI for non-technical users
- Multi-agent teams: Claude Code Agent Teams for parallel WP execution
- Cross-project learning: global insights from accumulated review logs
