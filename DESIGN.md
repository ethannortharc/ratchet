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

1. **Understanding first, then verification first.** Align human understanding through narrative (story) before converting to machine-verifiable constraints (spec). Verification capability determines autonomy.

1.5. **Multi-perspective alignment.** Features serve multiple stakeholders. Story phase gathers perspectives from relevant roles (end-user, developer, DevOps, security, QA), synthesizes via PM agent, and confirms with the user — all perspectives visible. Right roles participate in right phases.

2. **Two touchpoints.** Human interacts at two points: story/spec (provide direction) and review (evaluate results). Everything between runs autonomously.

3. **Thorough alignment.** Story phase has no time limit — iterate on personas, journey, scenarios, and prototype until the user says "this is what I want." Spec review is equally thorough. The more invested here, the less rework later.

4. **Maximum coverage.** Agent aggressively maximizes auto-verification by requesting tools, running multi-level tests (static → unit → integration), and never leaving basic functionality to human review.

5. **EVA (Environment-Verification Architecture).** An agent's autonomy is bounded by its verification capability. Validate all verification infrastructure before execution.

6. **Ratchet loop.** Budget-limited, git-backed. Every iteration: execute → verify → improved? keep : discard → repeat.

7. **Subagent architecture.** Specialized subagents for parallel execution — environment preparation, test generation, WP execution, verification, report writing.

8. **Direct feedback.** User reports issues in conversation OR via `/ratchet:review`. Both trigger the same feedback → constraint → iteration loop. No forced ceremony.

9. **Proof of work.** Reports include raw verification outputs — actual test results, ai_review justifications — not just pass/fail counts. Every WP produces a proof of completion document.

10. **Sessions are disposable.** Files are the single source of truth. Any session can pick up from where any previous session left off. Each spec/phase starts a new session for best quality.

## Architecture Overview

```
User: "I want to build X"
  │
  ▼
┌─────────────────────────────────────────────────────┐
│ Story (human + agent, Phase 1)                      │
│   Role selection (domain-specific)                   │
│   Parallel perspective agents (sonnet)               │
│   PM synthesis (opus) — unified requirements         │
│   Multi-perspective user confirmation                │
│   Manager sequencing (opus) — spec/phase planning    │
│   Complexity estimation + phase splitting            │
│   Status: draft                                      │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│ Spec (mostly automatic when story exists, Phase 2)  │
│   Auto-extract constraints from story artifacts     │
│   Environment negotiation (WAIT for user on tools)  │
│   Decision classification                            │
│   Interface mockup (iterate until approved)          │
│   Thorough section-by-section review (HTML page)    │
│   Status: draft → active                             │
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
│   Proof of Completion per WP                        │
│   report-writer: iteration report with proof of work│
│   Status: → agent_complete                          │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│ Acceptance Review (once per spec/phase)             │
│   Re-spawn role agents against actual built output  │
│   PM acceptance summary + verdict                   │
│   Gaps → new constraints → ratchet retry if needed  │
└──────────────────────┬──────────────────────────────┘
                       │
          === Agent notifies human ===
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│ Review (human + agent)                              │
│   /ratchet:review or direct conversation            │
│   Feedback → constraint conversion → new round      │
│   Coverage dashboard available                       │
│   Status: → done or → agent_running (new round)     │
└─────────────────────────────────────────────────────┘
```

## Key Concepts

### Story Phase

Phase 1: multi-perspective alignment. Gathers stakeholder perspectives, synthesizes via PM, confirms with user.

**Role-Based Process:**
1. **Role Selection** — identify relevant stakeholder roles from domain registry (references/role-registry.yaml)
2. **Parallel Perspective Gathering** — spawn per-role subagents (Sonnet) that each produce requirements, concerns, scenarios
3. **PM Synthesis** — PM agent (Opus) reads all perspectives, resolves conflicts, produces unified requirements
4. **User Confirmation** — present synthesis with all perspectives visible; user makes final calls
5. **Manager Sequencing** — Manager agent (Opus) decomposes into specs/phases for multi-phase projects

**Artifacts produced:**
- **Perspectives** (`perspectives/*.md`) — per-role requirements, concerns, scenarios
- **PM Synthesis** (`synthesis.md`) — unified requirements with conflict resolutions and prioritized scope
- **Personas** (`personas.md`) — behavioral personas enhanced with role-tagged needs
- **User Journey** (`journey.md`) — narrative walkthrough with cross-cutting annotations from multiple roles
- **Scenario Coverage** (`scenarios.md`) — comprehensive table with source-role column
- **Visual Mood + Prototype** (`mood.md` + `prototype.html`) — style direction and clickable skeleton
- **Decision Log** (`decisions.md`) — every decision classified, with role attribution
- **Plan Overview** (`plan-overview.md`) — Manager's spec sequencing (multi-phase projects)
- **Active Roles** (`roles.yaml`) — which roles participated

**Role Distribution:**
| Phase | Active Roles | Purpose |
|-------|-------------|---------|
| Story | End-user, Developer, DevOps, Security, QA | Perspective gathering |
| Story Synthesis | PM | Conflict resolution, unified requirements |
| Planning | Manager | Spec sequencing, phase ordering |
| Verification | QA | Test quality review, scenario coverage |
| Review | PM | Structured review summary |

The story phase also estimates complexity with story points. Projects > 30 points are split into phases by the Manager agent, each with its own spec and execution session.

### Intent Spec (spec.yaml)

Structured representation of human intent, auto-derived from story artifacts when available. Contains:

- **Invariants**: Hard constraints with multi-level test_method (static → unit → integration)
- **Quality Dimensions**: Measurable targets with rubrics and thresholds
- **Preferences**: Soft guidance
- **Delivery**: UI/UX direction (key screens, user journey, mood) or CLI direction
- **Decisions**: Classified as human_must_decide, agent_can_decide, or unknown
- **agent_guidance**: Natural language prompt for agent context and stuck-recovery

Each constraint has: track, verifier, test_method, tools_required (structured), ratchet_metric, and source (which story artifact it was extracted from).

### Proof of Completion

Every WP completion produces a proof document at `.ratchet/proofs/wp-{id}.md`:

- **What was built** — files, functions, components
- **Design decisions made** (agent_can_decide) — with rationale
- **Decisions already confirmed** — references to story/spec confirmations
- **Scenario coverage table** — input → expected → actual → status
- **What was NOT covered** — forces agent to be honest about gaps
- **How to verify** — manual verification steps for the user

A WP is not "complete" without its proof document.

### Workspace Management

Each intent registered in `~/.config/ratchet/state.yaml` with:
- Unique ID, absolute workspace path (locked at creation)
- Lifecycle state, ticket metadata (priority, tags, brief, current_blocker)

All operations stay within workspace. Commands accept optional intent ID.

### Session Management

**Files are the single source of truth. Sessions are disposable.**

Everything that matters is persisted to `.ratchet/` files. Any session can pick up from where any previous session left off.

**Session transitions:**
- Phase complete → save all results → suggest new session for next phase
- Context getting full → save execution-state.yaml checkpoint → suggest new session
- Story discussion > 30 min → suggest fresh start (all artifacts saved)
- User explicitly asks → save checkpoint → user starts new session

**Execution checkpoint (.ratchet/execution-state.yaml):**
```yaml
intent: string
phase: string           # if multi-phase
checkpoint_at: datetime
work_packages:
  wp-01: done
  wp-02: running        # iteration N of budget
  wp-03: pending
current_wp:
  id: string
  iteration: int
  best_score: float
  last_failure: string
```

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
| perspective-{role} | sonnet | Role-specific requirements gathering (parallel) |
| pm-synthesis | opus | Synthesize perspectives, resolve conflicts |
| manager | opus | Spec sequencing, phase planning |
| env-preparer | sonnet | Install tools, scaffold, validate environment |
| test-generator | sonnet | Generate test suite from test_method fields |
| wp-executor | sonnet | Execute single WP within workspace |
| verifier | sonnet | 3-level verification + ai_review + QA perspective, composite score |
| report-writer | haiku | Generate iteration reports from logs |

Orchestration: env-preparer + test-generator run in parallel. Independent WPs run in parallel via multiple wp-executor instances.

### Multi-Level Verification

```
Level 1 — Static: build, lint, type-check
Level 2 — Unit: isolated function tests
Level 3 — Integration: actually run the artifact and verify behavior
```

Level 3 catches encoding errors, broken buttons, navigation failures — issues unit tests miss. Agent discovers available verification capabilities and aggressively recommends tools to enable Level 3.

### Feedback Paths

**Direct conversation:** User says "the button is broken" → agent runs feedback conversion engine → converts to auto-verifiable constraint → updates spec → fixes immediately.

**Formal review:** `/ratchet:review` processes accumulated queue items across intents.

Both trigger the same loop. Basic functionality bugs are acknowledged as agent failures and get auto-verifiable constraints added.

### Story Point Estimation + Phase Splitting

During story phase, agent estimates complexity:

```
1-5 points:    Trivial. Single WP, one session.
5-15 points:   Small. 2-4 WPs, one session.
15-30 points:  Medium. 5-10 WPs, one session.
30-60 points:  Large. Must split into multiple phases.
60+ points:    Very large. Must split. Each phase < 30 points.
```

Each phase gets its own story subset, spec, tests, and proofs. Phase 2's story can reference Phase 1's deliverables as inputs.

### EVA — Understanding-Verification Architecture

The complete EVA chain:

```
Perspectives → Understanding → Specification → Verification → Execution → Proof → Acceptance

Each step formalizes the previous:
  Stakeholder concerns → Human language → Machine language → Machine execution → Evidence → Perspective validation
```

The v5 addition: before understanding (story), we must first establish WHO needs to understand and WHAT each stakeholder cares about. Multi-perspective alignment ensures no blind spots reach the specification phase.

**Full principle: Perspectives-first, then understanding-first, then verification-first, then execution.**

## File Layout

### Plugin
```
ratchet/
├── .claude-plugin/plugin.json
├── commands/                     # User-facing
│   ├── story.md                  # Phase 1: human-language alignment
│   ├── spec.md                   # Phase 2: constraint generation
│   ├── review.md                 # Review results
│   ├── coverage.md               # Three-layer coverage dashboard
│   ├── status.md                 # Check progress
│   ├── profile.md                # Set preferences
│   ├── pause.md                  # Pause execution
│   └── resume.md                 # Resume execution
├── skills/                       # Internal workflows
│   ├── getting-started/SKILL.md
│   ├── story/SKILL.md            # Story phase orchestration
│   ├── spec/SKILL.md             # Spec generation + execution chain
│   ├── plan/SKILL.md
│   ├── verify/SKILL.md
│   ├── execute/SKILL.md          # Ratchet loop orchestration
│   ├── update/SKILL.md
│   ├── review/SKILL.md
│   ├── coverage/SKILL.md         # Three-layer coverage
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
├── state.yaml                    # Global intent registry (with phase tracking)
├── review_queue.yaml
└── global_metrics.yaml
```

### Per-Intent Workspace (simple project, < 30 points)
```
<workspace>/.ratchet/
├── story/                        # Story artifacts (Phase 1)
│   ├── perspectives/             # Per-role perspective documents
│   │   ├── end-user.md
│   │   ├── developer.md
│   │   ├── devops.md
│   │   ├── security.md
│   │   └── qa-tester.md
│   ├── synthesis.md              # PM synthesis output
│   ├── personas.md               # Unified personas (role-tagged)
│   ├── journey.md                # Unified journey (cross-cutting annotations)
│   ├── scenarios.md              # Comprehensive scenarios (source-role column)
│   ├── mood.md
│   ├── prototype.html
│   ├── decisions.md
│   ├── plan-overview.md          # Manager's spec sequencing
│   ├── roles.yaml                # Active roles for this project
│   └── complexity.yaml
└── {intent-id}/                  # Each intent gets its own subdirectory
    ├── spec.yaml
    ├── plan.yaml
    ├── test-suite/
    │   ├── manifest.yaml
    │   ├── auto/
    │   ├── ai-review/
    │   └── human/
    ├── proofs/                   # Proof of completion per WP
    │   └── wp-{id}.md
    ├── acceptance/               # Perspective acceptance reviews
    │   ├── end-user.md
    │   ├── developer.md
    │   ├── devops.md
    │   └── summary.md            # PM acceptance summary
    ├── pre-validation.log
    ├── review_log.yaml
    ├── metrics.yaml
    ├── suggested_constraints.yaml
    ├── reports/
    │   ├── wp-{id}.md
    │   └── iter-{NNN}.md
    ├── execution-state.yaml      # Execution checkpoint
    └── artifacts/
```

### Per-Intent Workspace (multi-phase project, > 30 points)
```
<workspace>/.ratchet/
├── story/                        # Top-level story (big picture)
│   ├── perspectives/             # Per-role perspective documents
│   │   ├── end-user.md
│   │   ├── developer.md
│   │   ├── devops.md
│   │   ├── security.md
│   │   └── qa-tester.md
│   ├── synthesis.md              # PM synthesis output
│   ├── personas.md               # Unified personas (role-tagged)
│   ├── journey.md                # Full journey across all phases (cross-cutting annotations)
│   ├── scenarios.md              # Comprehensive scenarios (source-role column)
│   ├── complexity.yaml           # Estimate + phase split
│   ├── decisions.md
│   ├── plan-overview.md          # Manager's spec sequencing
│   └── roles.yaml                # Active roles for this project
├── phases/
│   ├── phase-1/
│   │   ├── story/                # Phase 1 specific details
│   │   │   ├── journey.md
│   │   │   ├── scenarios.md
│   │   │   └── prototype.html
│   │   ├── spec.yaml
│   │   ├── plan.yaml
│   │   ├── test-suite/
│   │   ├── proofs/
│   │   ├── acceptance/               # Perspective acceptance reviews
│   │   │   ├── end-user.md
│   │   │   ├── developer.md
│   │   │   ├── devops.md
│   │   │   └── summary.md            # PM acceptance summary
│   │   └── reports/
│   ├── phase-2/
│   │   ├── story/
│   │   ├── spec.yaml
│   │   ├── inputs.yaml           # "Assumes Phase 1 delivered X"
│   │   └── ...
│   └── phase-3/
│       └── ...
├── execution-state.yaml          # Current execution checkpoint
├── review_log.yaml
└── coverage.yaml                 # Cross-phase coverage data
```

Multiple intents can share the same workspace directory. Each intent's artifacts are isolated in its own subdirectory.

## Commands

**User-facing (daily use):**

| Command | Purpose | When |
|---------|---------|------|
| `/ratchet:story` | Define what to build (personas, journey, scenarios, prototype) | Starting a new intent |
| `/ratchet:spec` | Convert story to verifiable constraints (usually auto-triggered) | After story, or standalone |
| `/ratchet:review` | Review results, give feedback | When agent notifies completion |
| `/ratchet:coverage` | View three-layer coverage dashboard | Anytime |
| `/ratchet:status` | View execution progress across intents | Anytime |
| `/ratchet:profile` | Set personal preferences | One-time setup |
| `/ratchet:pause` | Pause execution | When needed |
| `/ratchet:resume` | Resume execution | When ready |

**Internal (agent calls automatically):**

| Skill | Purpose | Triggered by |
|-------|---------|-------------|
| plan | Decompose spec into work packages | After spec confirmation |
| verify | Three-tier verification | After any code change |
| execute | Ratchet loop orchestration | After planning |
| report | Generate iteration reports with proof | After each WP/iteration |
| metrics | Track time, tokens, automation stats | Embedded in report/status |
| update | Process story/spec modifications | User says "change X" in conversation |

## Design Decisions

### Why story before spec?
Spec mixes "what are we building" with "how do we verify it's correct." The story phase separates these concerns. Story aligns human understanding through narrative and examples. Spec converts confirmed understanding into machine-verifiable constraints. This prevents the "tests pass but not what I wanted" problem.

### Why only two human touchpoints?
Every additional human checkpoint is a bottleneck. Story/spec and review are the only steps where human judgment is irreplaceable. Plan, execute, verify, report — agent can handle all of these.

### Why thorough spec with no time limit?
Changes during spec cost ~ 0 (editing YAML). Changes during execution cost ratchet iterations. Changes during review cost spec bumps + re-execution. Front-loading specification is always cheaper.

### Why delivery/UI direction in spec?
For products with user interfaces, the interaction model IS the product. Not aligning on this during spec guarantees rework.

### Why proof of completion?
Agent says "WP done, tests pass" but user has no way to judge WHAT was done, what decisions were made, what wasn't covered. Proof documents make implicit choices visible and force agent to be honest about gaps.

### Why decision classification?
Agent makes decisions silently during execution that the user should have confirmed, or asks about decisions it could have made itself. Classification prevents both failure modes.

### Why role-based perspectives?
A single agent generating story artifacts has blind spots — it's one mind trying to think of everything. Parallel perspective agents (end-user, developer, DevOps, security, QA) each focus on what they know, producing richer requirements than any single agent could. PM synthesis reconciles these into a unified view, making conflicts explicit rather than hidden.

### Why PM and Manager as separate agents?
PM and Manager serve distinct functions. PM synthesizes requirements (what to build), Manager sequences execution (in what order). Combining them would conflate prioritization with planning. PM runs during story synthesis; Manager runs after confirmation to decompose into specs/phases.

### Why Sonnet for perspectives, Opus for synthesis?
Individual perspective agents have focused, well-scoped tasks — Sonnet handles these efficiently. PM synthesis and Manager planning require deeper reasoning about trade-offs and conflicts — Opus produces better results for these complex reconciliation tasks.

### Why subagents?
Context isolation: each subagent gets a clean context focused on one task. Cost optimization: wp-executor and verifier on Sonnet, report-writer on Haiku. Parallelism: independent WPs run simultaneously.

### Why EVA?
An agent's autonomy is bounded by its verification capability. If it can verify its own work, it can iterate without human help. Validating the pipeline before execution catches infrastructure issues when they're trivial to fix.

### Why maximum coverage over convenient human review?
Every constraint on human-track is a delay. Agent should exhaust all options before falling back to human review. Basic functionality bugs reaching human review is a system failure.

### Why sessions are disposable?
Long sessions degrade AI quality. Context window fills up, responses slow down. Files are the single source of truth — any session can resume from any checkpoint.

### Why story point estimation?
Large intents are too big for a single spec → execution cycle. Each phase should be completable in one session with fresh context.

### Why direct feedback?
Requiring `/ratchet:review` for every piece of feedback adds ceremony without value. When the user sees an issue, they should just say it.

## Future Directions

- Review UI: browser-based spec review for large specs (>20 constraints)
- Desktop app: Tauri-based UI for non-technical users
- Multi-agent teams: Claude Code Agent Teams for parallel WP execution
- Cross-project learning: global insights from accumulated review logs
- Multi-domain role registries: data science, design, research domains with specialized roles
- Role memory: perspectives learn from past projects (e.g., "this team always neglects logging")
- Direct role interaction: users converse with individual role agents for deep-dive discussions
