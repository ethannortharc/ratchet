# Ratchet — Design Document

## Vision

Ratchet is an intent-driven execution framework. You describe what you want, the system autonomously iterates until it produces the best possible result, and you review only what matters.

The name comes from the core mechanism: like a ratchet wrench, progress only moves forward. Every iteration either improves the result (commit/keep) or doesn't (reset/discard). Over time, quality ratchets up monotonically.

## Core Philosophy

1. **Generate first, ask later.** When a user describes intent, generate a complete spec draft using industry knowledge + personal profile. Ask only about 2-3 low-confidence areas. Never interrogate with 15 questions.

2. **Dual-track verification.** Agent-track constraints (auto + ai_review) run continuously without human involvement. Human-track constraints queue asynchronously — the user reviews when available, not when the system demands.

3. **Ratchet loop.** Every work package iterates: execute → verify → improved? keep : discard → repeat. Budget-limited, git-backed. Only escalate to human when budget is exhausted.

4. **Agent is proactive.** The system actively requests better tools/environment to increase automation coverage. It discovers new constraints during execution and proposes them for human approval.

5. **Spec is a living document.** Versioned, updatable at any time. Human feedback gets converted into agent-verifiable constraints whenever possible. Over time, human-track shrinks, agent-track grows.

## Architecture Overview

```
User: "I want to build X"
  │
  ▼
┌─────────────────────────────────────────────────────┐
│ Phase 1: Intent Formalization (sync, ~3 min)        │
│   Load profile → Generate spec draft → Confirm      │
│   Detect environment → Negotiate capabilities       │
│   Output: spec.yaml v1                              │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│ Phase 2: Autonomous Execution (async, hours)        │
│                                                     │
│   plan.yaml ← decompose spec into work packages    │
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
│ Phase 3: Human Review (async, ~5-10 min)            │
│   Review queue shows pending items across projects  │
│   Feedback → converted to agent constraints → spec  │
│   version increments → triggers new iteration round │
└─────────────────────────────────────────────────────┘
```

## Key Concepts

### Spec (spec.yaml)

The structured representation of human intent. Three tiers of constraints:

- **Invariants**: Hard constraints, must not be violated. "All tests pass", "First-person POV only"
- **Quality Dimensions**: Measurable quality targets with rubrics and thresholds. "Code readability ≥ 4/5"
- **Preferences**: Soft guidance, nice-to-have. "Prefer standard library"

Each constraint has:
- `track`: `agent` (auto-verified, drives ratchet) or `human` (queued for async review)
- `verifier`: `auto` (executable check) | `ai_review` (AI evaluates against rubric) | `human` (subjective judgment)
- `ratchet_metric`: Quantified progress indicator (not just pass/fail)

Spec is versioned. Every update increments version and logs the change reason.

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
├── skills/
│   ├── getting-started/SKILL.md   # Session bootstrap
│   ├── spec/SKILL.md              # Intent → structured spec
│   ├── plan/SKILL.md              # Spec → work packages
│   ├── verify/SKILL.md            # Three-tier verification + ratchet loop
│   ├── review/SKILL.md            # Human-track async review queue
│   ├── status/SKILL.md            # Multi-project dashboard
│   ├── report/SKILL.md            # Iteration + project reports
│   ├── profile/SKILL.md           # Personal preferences
│   └── metrics/SKILL.md           # Interaction tracking
├── references/
│   ├── spec-schema.md             # spec.yaml format
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
├── spec.yaml                      # Versioned intent specification
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

## Spec Schema

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
    check: string          # How to verify
    ratchet_metric: string # Quantified progress (optional)
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
| `/ratchet:spec` | Intent → structured spec | Init |
| `/ratchet:plan` | Spec → work packages | Planning |
| `/ratchet:verify` | Run verification + ratchet loop | Execution |
| `/ratchet:review` | Process human-track review queue | Review |
| `/ratchet:status` | Multi-project dashboard | Monitoring |
| `/ratchet:report` | Generate iteration/project report | Reporting |
| `/ratchet:profile` | Manage personal preferences | Setup |
| `/ratchet:metrics` | Show interaction + automation stats | Analysis |
| `/ratchet:update` | Update spec mid-project | Iteration |

Typical flow: `/ratchet:spec` → confirm → agent runs autonomously → `/ratchet:review` when notified → `/ratchet:report` to see results.

Advanced: individual commands for fine-grained control.

## Design Decisions

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

- **Desktop app**: Tauri-based UI over the same core, for non-technical users
- **Codex integration**: Use Codex as alternative execution backend
- **Multi-agent teams**: Claude Code Agent Teams for parallel WP execution
- **Plugin marketplace**: Publish to official Claude Code marketplace
- **Cross-project learning**: Global insights from accumulated review_logs
