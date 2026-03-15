# Ratchet — Design Document

## Vision

Ratchet is an intent-driven execution framework. You describe what you want, the system autonomously iterates until it produces the best possible result, and you review only what matters.

The name comes from the core mechanism: like a ratchet wrench, progress only moves forward. Every iteration either improves the result (commit/keep) or doesn't (reset/discard). Over time, quality ratchets up monotonically.

## Core Philosophy

1. **Hybrid 3-step spec.** When a user describes intent: (1) converge on 2-3 high-level decisions, (2) generate a complete Intent Spec using industry knowledge + profile, (3) review section-by-section in conversation with incremental patching. Under 5 minutes total.

2. **Dual-track verification.** Agent-track constraints (auto + ai_review) run continuously without human involvement. Human-track constraints queue asynchronously — the user reviews when available, not when the system demands.

3. **Test suite first.** Before implementation, generate tests from each constraint's `test_method`. This gives the ratchet loop real pass/fail signals from iteration 1 (TDD at the framework level).

4. **Ratchet loop.** Every work package iterates: execute → verify → improved? keep : discard → repeat. Budget-limited, git-backed. Only escalate to human when budget is exhausted.

5. **Agent is proactive.** The system actively requests better tools/environment to increase automation coverage. It discovers new constraints during execution and proposes them for human approval.

6. **Intent Spec is a living document.** Versioned, updatable at any time. Human feedback gets converted into agent-verifiable constraints whenever possible. Over time, human-track shrinks, agent-track grows.

## Architecture Overview

```
User: "I want to build X"
  │
  ▼
┌─────────────────────────────────────────────────────┐
│ Phase 1: Intent Formalization (sync, ~5 min)        │
│   Step 1: Intent convergence (2-3 decisions)        │
│   Step 2: Generate Intent Spec (industry knowledge) │
│   Step 3: Conversation review + patch               │
│   Output: spec.yaml v1                              │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│ Phase 2: Planning + Test Suite (sync, ~5 min)       │
│   Decompose into work packages                     │
│   wp-00: Environment prep (if needed)              │
│   wp-01: Generate test suite from test_method      │
│   wp-02+: Implementation work packages             │
│   Output: plan.yaml + test files                   │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│ Phase 3: Autonomous Execution (async, hours)        │
│                                                     │
│   For each WP (parallel where possible):            │
│   ┌───────────────────────────────────────────┐     │
│   │ Execute → Verify agent-track constraints  │     │
│   │   ├─ improved? → git commit (keep)        │     │
│   │   └─ not improved? → git reset (discard)  │     │
│   │ Repeat until pass or budget exhausted     │     │
│   │                                           │     │
│   │ Agent-complete → queue human-track items  │     │
│   └───────────────────────────────────────────┘     │
│                                                     │
│   Cross-WP knowledge transfer                       │
│   Incremental delivery (done WPs available early)   │
│   Generate iteration reports                        │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│ Phase 4: Human Review (async, ~5-10 min)            │
│   Review queue shows pending items across projects  │
│   Feedback → converted to agent constraints →       │
│   spec version increments → triggers new round      │
└─────────────────────────────────────────────────────┘
```

## Key Concepts

### Intent Spec (spec.yaml)

The structured representation of human intent. Three tiers of constraints:

- **Invariants**: Hard constraints, must not be violated. "All tests pass", "First-person POV only"
- **Quality Dimensions**: Measurable quality targets with rubrics and thresholds. "Code readability ≥ 4/5"
- **Preferences**: Soft guidance, nice-to-have. "Prefer standard library"

Each constraint has:
- `track`: `agent` (auto-verified, drives ratchet) or `human` (queued for async review)
- `verifier`: `auto` (executable check) | `ai_review` (AI evaluates against rubric) | `human` (subjective judgment)
- `test_method`: detailed description of what to test — scenarios, edge cases, expected behaviors. Used by the agent to generate the test suite.
- `tools_required`: specific tools needed for verification (e.g., `[vitest]`, `[pytest]`)
- `ratchet_metric`: Quantified progress indicator (not just pass/fail)

Intent Spec is versioned. Every update increments version and logs the change reason.

### Hybrid 3-Step Spec Flow

1. **Intent convergence**: Ask 2-3 multiple-choice questions about high-level "what" decisions (architecture, scope, platform). NOT design decisions (frameworks, patterns).
2. **Generate Intent Spec**: Use decisions + industry knowledge + profile to produce complete spec.yaml with all constraints, test_methods, and tools_required.
3. **Conversation review**: Present section-by-section summary. User provides natural language feedback. Incrementally patch — don't regenerate.

### Test Suite First

After the Intent Spec is approved, `/ratchet:plan` generates tests as the first work package:
- Read each constraint's `test_method` field
- Generate test files using `tools_required`
- Tests are runnable but failing (TDD red phase)
- Implementation WPs then make tests pass (green phase)

This means the ratchet loop has real pass/fail signals from iteration 1, instead of the agent writing tests and implementation together (which makes the first score meaningless).

### Dual-Track Verification

**Agent track** runs 24/7:
- `auto` verifiers: executable commands (tests, lints, word counts)
- `ai_review` verifiers: AI evaluates against rubric
- Drives the ratchet loop — no human needed

**Human track** runs when human is available:
- Queued in `~/.config/ratchet/review_queue.yaml`
- Priority-sorted (blocking items first)
- Human feedback converted to agent constraints when possible

### Ratchet Loop

Inspired by Karpathy's autoresearch:
- Fixed iteration budget per work package
- Each iteration: modify → execute → measure
- Composite score improves → git commit (keep)
- Composite score doesn't improve → git reset (discard)
- All agent constraints pass → mark as agent_complete
- Budget exhausted without passing → escalate to human

Git backend for code projects, filesystem backend for non-code projects.

### Constraint Discovery

Constraints aren't only defined at init time:
- **Human discovers**: Reviews output, adds new constraint via `/ratchet:update`
- **Agent discovers**: Finds issues during execution, proposes via `suggested_constraints.yaml`
- Both flow through spec version update → trigger new iteration

### Cross-Domain Support

Same framework for software, creative writing, research, design:
- Industry knowledge built into spec generation (references/inquiry-protocols.md)
- Ratchet budget adapts by domain (software: high, creative: medium)
- Verifier distribution differs but format is universal

## File Layout

### Plugin Files (read-only, managed by Claude Code plugin system)
```
~/.claude/plugins/ratchet/
├── .claude-plugin/plugin.json     # Plugin manifest
├── commands/
│   ├── spec.md                    # /ratchet:spec command entry
│   ├── plan.md                    # /ratchet:plan command entry
│   ├── verify.md                  # /ratchet:verify command entry
│   ├── review.md                  # /ratchet:review command entry
│   ├── status.md                  # /ratchet:status command entry
│   ├── report.md                  # /ratchet:report command entry
│   ├── profile.md                 # /ratchet:profile command entry
│   ├── metrics.md                 # /ratchet:metrics command entry
│   └── update.md                  # /ratchet:update command entry
├── skills/
│   ├── getting-started/SKILL.md   # Session bootstrap
│   ├── spec/SKILL.md              # Intent → Intent Spec (hybrid 3-step)
│   ├── plan/SKILL.md              # Intent Spec → work packages + test suite
│   ├── verify/SKILL.md            # Three-tier verification + ratchet loop
│   ├── update/SKILL.md            # Mid-project Intent Spec updates
│   ├── review/SKILL.md            # Human-track async review queue
│   ├── status/SKILL.md            # Multi-project dashboard
│   ├── report/SKILL.md            # Iteration + project reports
│   ├── profile/SKILL.md           # Personal preferences
│   └── metrics/SKILL.md           # Interaction tracking
├── references/
│   ├── spec-schema.md             # Intent Spec format
│   ├── inquiry-protocols.md       # Domain knowledge
│   └── verifier-guide.md          # Verification implementation
├── templates/
│   └── spec-template.yaml
└── DESIGN.md                      # This file
```

### User Config (read-write, persists across projects)
```
~/.config/ratchet/
├── profile.yaml                   # Personal preferences
├── state.yaml                     # All projects index
├── review_queue.yaml              # Cross-project human review queue
└── global_metrics.yaml            # Cross-project trends
```

### Project State (read-write, per project)
```
<project-dir>/.ratchet/
├── spec.yaml                      # Versioned Intent Spec
├── plan.yaml                      # Work packages + dependency graph
├── review_log.yaml                # All verification results
├── metrics.yaml                   # Project-level metrics
├── suggested_constraints.yaml     # Agent-proposed constraints
├── iteration_history.yaml         # Per-round summaries
├── reports/                       # Generated reports
│   ├── iter-001.md
│   ├── iter-002.md
│   └── final.md
└── artifacts/                     # Execution outputs
    ├── current/                   # Current best version
    ├── staging/                   # Agent working copy
    └── history/                   # Previous versions
```

## Intent Spec Schema

```yaml
project:
  name: string
  type: software | creative_writing | research | design | general
  description: string
  created: datetime
  status: draft | active | completed | archived

spec_version: int
changelog:
  - version: int
    date: datetime
    source: human | agent_suggestion | review_feedback
    change: string
    added: [string]
    modified: [string]
    removed: [string]

environment:
  capabilities:
    - id: string
      type: runtime | tool | agent | service
      version: string
      detected: bool
      enables: [string]
  absent:
    - id: string
      impact: string
      install_hint: string
      agent_can_install: bool

invariants:
  - id: string            # INV-01
    claim: string
    track: agent | human
    confidence: high | medium | low
    verifier: auto | ai_review | human
    requires: [string]     # Capability IDs
    check: string          # Command or method to verify
    test_method: string    # Detailed test scenarios for agent
    tools_required: [string]  # Tools needed for verification
    ratchet_metric: string
    fallback_verifier: string
    fallback_check: string

quality_dimensions:
  - id: string            # QD-01
    dimension: string
    track: agent | human
    confidence: high | medium | low
    verifier: auto | ai_review | human
    rubric: string         # 5/3/1 scoring
    threshold: number
    test_method: string    # How to evaluate this dimension
    tools_required: [string]
    ratchet_metric: string

preferences:
  - string

exploration_hints:
  - string                 # Direction suggestions for agent when stuck

ratchet:
  enabled: bool
  default_budget: int      # Max iterations per WP
  strategy: keep_best | keep_last
  backend: git | filesystem  # Auto-detected
  composite_score:
    method: weighted_average | single_metric
    weights: {metric: weight}

profile_applied:
  - key: string
    value: string
    source: profile | project-override
```

## Commands

| Command | Purpose | Phase |
|---------|---------|-------|
| `/ratchet:spec` | Intent → Intent Spec (hybrid 3-step) | Init |
| `/ratchet:plan` | Intent Spec → work packages + test suite | Planning |
| `/ratchet:verify` | Run verification + ratchet loop | Execution |
| `/ratchet:review` | Process human-track review queue | Review |
| `/ratchet:status` | Multi-project dashboard | Monitoring |
| `/ratchet:report` | Generate iteration/project report | Reporting |
| `/ratchet:profile` | Manage personal preferences | Setup |
| `/ratchet:metrics` | Show interaction + automation stats | Analysis |
| `/ratchet:update` | Update Intent Spec mid-project | Iteration |

Typical flow: `/ratchet:spec` → confirm → `/ratchet:plan` (generates tests) → agent runs autonomously → `/ratchet:review` when notified → `/ratchet:report` to see results.

Advanced: individual commands for fine-grained control.

## Design Decisions

### Why hybrid 3-step instead of single-pass spec generation?
Single-pass generates a full spec then asks "any questions?" — but fundamental direction choices get buried alongside implementation details. The hybrid flow settles high-level "what" decisions first (architecture, scope, platform), then generates the complete spec, then reviews section-by-section with incremental patching. Each step has a clear purpose and stays under 5 minutes total.

### Why test suite before implementation?
Without pre-existing tests, the ratchet loop's first iteration has no meaningful signal — the agent writes code and tests together, so the first "score" is always artificial. Generating tests first (from `test_method` fields) means every iteration has real pass/fail data. This is TDD at the framework level.

### Why dual-track instead of unified verification?
Single-track means every human checkpoint blocks the agent. Dual-track lets agent optimize continuously while human reviews accumulate in a queue. This maximizes agent autonomy and respects human time.

### Why versioned specs?
Intent evolves. The user sees results and wants to add features, tighten quality, change direction. Versioned specs make this natural — each version triggers a new optimization round starting from the best result so far.

### Why git for ratchet state?
Git provides atomic commit/reset, branch isolation, diff visibility, and history for free. For non-code projects, the filesystem fallback (current/staging/history directories) provides equivalent functionality without requiring the user to understand git.

### Why composite score instead of individual pass/fail?
A work package might have 5 agent-track constraints. If 4/5 pass, that's better than 3/5 even though both "fail". The composite score lets the ratchet keep partial improvements, converging toward full pass over multiple iterations.

### Why agent-proposed constraints?
Specs are inherently incomplete — the user can't predict every edge case. When the agent discovers issues during execution (concurrency bugs, missing validation, inconsistent world-building), proposing them as new constraints captures knowledge that would otherwise be lost.

### Why not a web app?
Token costs fall on the user (they use their own API keys/subscriptions). No server to maintain. Integrates directly with Claude Code, Codex, and other local tools. Desktop tool later if needed.

## Future Directions

- **Review UI**: Local browser-based review page for Intent Spec review and intent convergence decisions
- **Desktop app**: Tauri-based UI over the same core, for non-technical users
- **Codex integration**: Use Codex as alternative execution backend
- **Multi-agent teams**: Claude Code Agent Teams for parallel WP execution
- **Plugin marketplace**: Publish to official Claude Code marketplace
- **Cross-project learning**: Global insights from accumulated review_logs
