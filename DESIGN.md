# Ratchet — Design Document

## Vision

Ratchet is an intent-driven execution framework. You describe what you want, the system autonomously iterates until it produces the best possible result, and you review only what matters.

The name comes from the core mechanism: like a ratchet wrench, progress only moves forward. Every iteration either improves the result (commit/keep) or doesn't (reset/discard). Over time, quality ratchets up monotonically.

## Core Philosophy

1. **Hybrid 3-step spec.** When a user describes intent: (1) converge on 2-3 high-level decisions, (2) generate a complete Intent Spec using industry knowledge + profile, (3) review section-by-section in conversation with incremental patching. Under 5 minutes total.

2. **Test suite first.** After Intent Spec confirmation, auto-generate concrete test files from each constraint's `test_method`. Tests exist before implementation starts, giving the ratchet loop real signals from iteration 1.

3. **Dual-track verification.** Agent-track constraints (auto + ai_review) run continuously without human involvement. Human-track constraints queue asynchronously — the user reviews when available, not when the system demands.

4. **Ratchet loop.** Every work package iterates: execute → verify → improved? keep : discard → repeat. Budget-limited, git-backed. Only escalate to human when budget is exhausted.

5. **Workspace isolation.** Each intent is registered with a unique ID and locked to an absolute workspace path. All operations stay within the workspace. The global registry enables multi-intent management from any directory.

6. **Proof of work.** Reports include raw verification outputs — actual test results, ai_review justifications, screenshots — not just pass/fail counts.

7. **Agent is proactive.** The system actively requests better tools/environment to increase automation coverage. It discovers new constraints during execution and proposes them for human approval.

8. **Intent Spec is a living document.** Versioned, updatable at any time. Human feedback gets converted into agent-verifiable constraints whenever possible. Over time, human-track shrinks, agent-track grows.

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
│   Step 4: Auto-generate test suite                  │
│   Register workspace in global intent registry      │
│   Output: spec.yaml v1 + .ratchet/test-suite/       │
│   State: draft → active                             │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│ Phase 2: Planning (sync, ~5 min)                    │
│   Decompose into work packages                     │
│   Reference pre-generated test suite files          │
│   wp-00: Environment prep (if needed)              │
│   wp-01+: Implementation work packages             │
│   Output: plan.yaml                                │
│   State: active                                     │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│ Phase 3: Autonomous Execution (async, hours)        │
│   State: agent_running                              │
│                                                     │
│   For each WP (parallel where possible):            │
│   ┌───────────────────────────────────────────┐     │
│   │ Execute → Verify agent-track constraints  │     │
│   │   ├─ improved? → git commit (keep)        │     │
│   │   └─ not improved? → git reset (discard)  │     │
│   │ Repeat until pass or budget exhausted     │     │
│   │ Capture raw output for proof of work      │     │
│   │                                           │     │
│   │ Agent-complete → queue human-track items  │     │
│   └───────────────────────────────────────────┘     │
│                                                     │
│   Cross-WP knowledge transfer                       │
│   Incremental delivery (done WPs available early)   │
│   Generate iteration reports with proof of work     │
│   State: → agent_complete                           │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│ Phase 4: Human Review (async, ~5-10 min)            │
│   State: human_review                               │
│   Review queue shows pending items across intents   │
│   Feedback → converted to agent constraints →       │
│   spec version increments → triggers new round      │
│   State: → agent_running (new round) or done        │
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
- `test_method`: detailed description of what to test — scenarios, edge cases, expected behaviors. Used to generate the test suite.
- `tools_required`: structured list with id, install hint, and agent_can_install flag
- `ratchet_metric`: Quantified progress indicator (not just pass/fail)

Intent Spec also includes:
- `agent_guidance`: natural language prompt giving the agent project context, constraints, and direction when stuck. Replaces the flat `exploration_hints` list.

Intent Spec is versioned. Every update increments version and logs the change reason.

### Hybrid 3-Step Spec Flow

1. **Intent convergence**: Ask 2-3 multiple-choice questions about high-level "what" decisions (architecture, scope, platform). NOT design decisions (frameworks, patterns).
2. **Generate Intent Spec**: Use decisions + industry knowledge + profile to produce complete spec.yaml with all constraints, test_methods, tools_required, and agent_guidance.
3. **Conversation review**: Present section-by-section summary. User provides natural language feedback. Incrementally patch — don't regenerate.

After approval, auto-generate the test suite (Step 4).

### Test Suite (.ratchet/test-suite/)

Generated automatically after Intent Spec confirmation:
- For `auto` verifiers: executable test files (unit tests, scripts) — runnable but failing (TDD red phase)
- For `ai_review` verifiers: structured review prompts with rubric
- For `human` verifiers: review checklists

Mapped by `manifest.yaml` which links constraint IDs to test files.

### Workspace Management

Each intent is registered in `~/.config/ratchet/state.yaml` with:
- Unique intent ID (kebab-case, auto-generated from name)
- Absolute workspace path (locked at creation)
- Lifecycle state
- Ticket-like metadata (priority, tags, brief, current_blocker)

All commands accept an optional intent ID. Resolution order when omitted:
1. Current directory is inside a registered workspace → use that intent
2. Multiple intents exist → ask user to choose
3. No intents exist → suggest `/ratchet:spec`

Agent execution includes workspace constraint: all file operations stay within the registered workspace.

### Intent Lifecycle

```
draft → active → agent_running → agent_complete → human_review → done
                      ↑                │
                      └── ratchet ──────┘

any → paused (user pauses)
paused → active (user resumes)
any → archived (user archives)
```

| State | Meaning |
|-------|---------|
| `draft` | Intent Spec exists but not yet confirmed |
| `active` | Intent Spec confirmed, plan exists or being created |
| `agent_running` | Agent is executing work packages with ratchet loop |
| `agent_complete` | All agent-track constraints pass, human items queued |
| `human_review` | Waiting for human to process review queue |
| `done` | All constraints (agent + human) verified, project complete |
| `paused` | User paused execution |
| `archived` | User archived (hidden from active views) |

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

### Proof of Work

Reports include raw verification outputs:
- Auto verifiers: actual test output, build logs, exit codes
- AI reviews: full reviewer response with score and justification
- Human items: artifact paths, checklists, screenshots

This makes reports trustworthy and auditable. Raw output is captured during verification and stored in `review_log.yaml`.

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
│   ├── update.md                  # /ratchet:update command entry
│   ├── pause.md                   # /ratchet:pause command entry
│   └── resume.md                  # /ratchet:resume command entry
├── skills/
│   ├── getting-started/SKILL.md   # Session bootstrap
│   ├── spec/SKILL.md              # Intent → Intent Spec + test suite (hybrid 3-step)
│   ├── plan/SKILL.md              # Intent Spec → work packages
│   ├── verify/SKILL.md            # Three-tier verification + ratchet loop
│   ├── update/SKILL.md            # Mid-project Intent Spec updates
│   ├── review/SKILL.md            # Human-track async review queue
│   ├── status/SKILL.md            # Multi-intent dashboard
│   ├── report/SKILL.md            # Iteration + project reports with proof of work
│   ├── profile/SKILL.md           # Personal preferences
│   ├── metrics/SKILL.md           # Interaction tracking
│   ├── pause/SKILL.md             # Pause intent execution
│   └── resume/SKILL.md            # Resume paused intent
├── hooks/
│   └── hooks.json                 # Lifecycle hooks (auto-loaded)
├── references/
│   ├── spec-schema.md             # Intent Spec format + state.yaml schema
│   ├── inquiry-protocols.md       # Domain knowledge
│   └── verifier-guide.md          # Verification implementation
├── templates/
│   └── spec-template.yaml
└── DESIGN.md                      # This file
```

### User Config (read-write, persists across intents)
```
~/.config/ratchet/
├── profile.yaml                   # Personal preferences
├── state.yaml                     # Global intent registry
├── review_queue.yaml              # Cross-intent human review queue
└── global_metrics.yaml            # Cross-intent trends
```

### Project State (read-write, per intent workspace)
```
<workspace>/.ratchet/
├── spec.yaml                      # Versioned Intent Spec
├── plan.yaml                      # Work packages + dependency graph
├── test-suite/                    # Auto-generated test files
│   ├── manifest.yaml              # Constraint → test file mapping
│   ├── INV-01.test.ts             # Auto verifier tests
│   ├── QD-01.review.md            # AI review prompts
│   └── QD-02.checklist.md         # Human review checklists
├── review_log.yaml                # All verification results + raw output
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

See `references/spec-schema.md` for the complete schema. Key additions from v0.3.0:

- `tools_required` is now structured objects (id, install, agent_can_install) not simple strings
- `agent_guidance` replaces `exploration_hints` as a natural language prompt
- `project.status` uses the full lifecycle state machine

## Global State Schema (state.yaml)

```yaml
intents:
  - id: string                    # Unique identifier (kebab-case)
    name: string                   # Human-readable name
    workspace: string              # Absolute path, locked at creation
    type: string                   # software | creative_writing | research | design | general
    status: string                 # Lifecycle state
    spec_version: int
    created: datetime
    last_activity: datetime
    priority: string               # low | normal | high | urgent
    tags: [string]
    brief: string                  # One-line summary
    current_blocker: string        # null, or what's blocking
```

## Commands

| Command | Purpose | Phase |
|---------|---------|-------|
| `/ratchet:spec` | Intent → Intent Spec + test suite (hybrid 3-step) | Init |
| `/ratchet:plan` | Intent Spec → work packages | Planning |
| `/ratchet:verify` | Run verification + ratchet loop | Execution |
| `/ratchet:review` | Process human-track review queue | Review |
| `/ratchet:status` | Multi-intent dashboard with lifecycle | Monitoring |
| `/ratchet:report` | Generate reports with proof of work | Reporting |
| `/ratchet:profile` | Manage personal preferences | Setup |
| `/ratchet:metrics` | Show interaction + automation stats | Analysis |
| `/ratchet:update` | Update Intent Spec mid-project | Iteration |
| `/ratchet:pause` | Pause intent execution | Control |
| `/ratchet:resume` | Resume paused intent | Control |

Most commands accept an optional intent ID as argument. When omitted, resolved by current directory → registry → ask.

Typical flow: `/ratchet:spec` → confirm → `/ratchet:plan` → agent runs autonomously → `/ratchet:review` when notified → `/ratchet:report` to see results.

## Design Decisions

### Why hybrid 3-step instead of single-pass spec generation?
Single-pass generates a full spec then asks "any questions?" — but fundamental direction choices get buried alongside implementation details. The hybrid flow settles high-level "what" decisions first (architecture, scope, platform), then generates the complete spec, then reviews section-by-section with incremental patching. Each step has a clear purpose and stays under 5 minutes total.

### Why test suite before implementation?
Without pre-existing tests, the ratchet loop's first iteration has no meaningful signal — the agent writes code and tests together, so the first "score" is always artificial. Generating tests first (from `test_method` fields) means every iteration has real pass/fail data. This is TDD at the framework level. Generating tests also surfaces ambiguities in the spec early.

### Why workspace isolation?
Without it, the agent can `cd ..` and break context. Multiple intents have no clear boundary. The workspace registry with absolute paths provides: isolation (agent stays in workspace), multi-intent support (commands work from any directory), and clear project boundaries.

### Why intent lifecycle state machine?
Simple status values (draft/active/completed) don't capture the execution flow. The full state machine (draft → active → agent_running → agent_complete → human_review → done) makes `/ratchet:status` meaningful and enables pause/resume functionality.

### Why proof of work in reports?
"4/6 passed" is not trustworthy. Showing actual test output, build logs, and ai_review justifications makes reports auditable. The user can see exactly what was verified and how, building confidence in the system.

### Why agent_guidance instead of exploration_hints?
A flat list of strings ("try X", "try Y") is too shallow. `agent_guidance` is a natural language prompt giving the agent rich context — what the project is, key constraints, what to try when stuck, and anti-patterns to avoid. More expressive and easier to write.

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
