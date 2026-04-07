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

1. **Code manages process, LLMs do creative work.** Python tools handle state, gates, sequencing, DB operations — all deterministic. Claude Code agents handle perspectives, synthesis, code writing, review — all creative. SKILL.md files are lightweight recipes that alternate between Python calls and agent spawns.

1.5. **Multi-perspective alignment.** Features serve multiple stakeholders. Story phase gathers perspectives from relevant roles (end-user, developer, DevOps, security, QA), synthesizes via PM agent, and confirms with the user — all perspectives visible. Right roles participate in right phases.

1.6. **Story is the backlog. Spec is a sprint.** Story phase produces the product backlog (all requirements, prioritized). The Manager agent always runs sprint planning — deciding how many sprints and what goes in each. Each spec executes one sprint. This maps directly to agile: backlog → sprint planning → sprint → review.

1.7. **Living Backlog.** The backlog is not a one-time artifact — it grows continuously. New requirements, bugs, unresolved decisions, acceptance gaps, and QA recommendations all flow into the backlog. Sprints consume from the backlog. Nothing blocks execution; unresolvable items become new backlog entries.

2. **Two touchpoints.** Human interacts at two points: story/spec (provide direction) and review (evaluate results). Everything between runs autonomously.

3. **Thorough alignment.** Story phase has no time limit — iterate on personas, journey, scenarios, and prototype until the user says "this is what I want." Spec review is equally thorough. The more invested here, the less rework later.

4. **Maximum coverage.** Agent aggressively maximizes auto-verification by requesting tools, running multi-level tests (static → unit → integration), and never leaving basic functionality to human review.

5. **EVA (Environment-Verification Architecture).** An agent's autonomy is bounded by its verification capability. Validate all verification infrastructure before execution.

6. **Ratchet loop.** Budget-limited, git-backed. Every iteration: execute → verify → improved? keep : discard → repeat.

7. **Subagent architecture.** Specialized subagents for parallel execution — environment preparation, test generation, WP execution, verification, report writing.

8. **Direct feedback.** User reports issues in conversation OR via `/ratchet:review`. Both trigger the same feedback → constraint → iteration loop. No forced ceremony.

9. **Proof of work.** Reports include raw verification outputs — actual test results, ai_review justifications — not just pass/fail counts. Every WP produces a proof of completion document.

10. **Sessions are disposable.** Files are the single source of truth. Any session can pick up from where any previous session left off. Each sprint starts a new session for best quality.

## Architecture Overview

```
User: "I want to build X"
  │
  ▼
┌─────────────────────────────────────────────────────┐
│ Story (continuous — can run anytime)                 │
│   Full Story / Mini Story / Direct Entry             │
│   Perspectives → PM Synthesis → Backlog items        │
│   python tools/ratchet.py backlog add ...            │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│ Backlog (living, in ratchet.db)                      │
│   Features, bugs, improvements, unresolved items     │
│   Continuously fed by both human and agent tracks    │
└──────────────────────┬──────────────────────────────┘
                       │
          Manager agent pulls must items
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│ Sprint (autonomous, one per session)                 │
│   python tools/ratchet.py manages all state          │
│                                                     │
│   Spec (auto) → Prep → EVA → Plan → Execute        │
│   Per WP: executor → verifier → ratchet decide      │
│   Regression after each WP                          │
│   Acceptance Review → gaps → backlog                │
│   Finalize → merge → notify human                   │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│ Review (human, non-blocking)                         │
│   Feedback → new backlog items                       │
│   Confirm unresolved decisions → re-prioritize       │
│   Must items remain? → next Sprint auto-starts       │
└─────────────────────────────────────────────────────┘
```

## Key Concepts

### Story Phase

Phase 1: multi-perspective alignment. Gathers stakeholder perspectives, synthesizes via PM, confirms with user.

**Role-Based Process:**
1. **Intent Analysis + Role Derivation** — analyze what the intent needs, detect greenfield vs. existing project, derive roles from expertise gaps (registry is a template library, not a checklist)
2. **Parallel Perspective Gathering** — spawn per-role subagents (Sonnet) that each produce requirements, concerns, scenarios
3. **PM Synthesis** — PM agent (Opus) reads all perspectives, resolves conflicts, produces unified requirements
4. **User Confirmation** — present synthesis with all perspectives visible; user makes final calls
5. **Manager Sprint Planning** — Manager agent (Opus) always runs sprint planning, decomposes into sprints

**Artifacts produced:**
- **Perspectives** (`perspectives/*.md`) — per-role requirements, concerns, scenarios
- **PM Synthesis** (`synthesis.md`) — unified requirements with conflict resolutions and prioritized scope
- **Personas** (`personas.md`) — behavioral personas enhanced with role-tagged needs
- **User Journey** (`journey.md`) — narrative walkthrough with cross-cutting annotations from multiple roles
- **Scenario Coverage** (`scenarios.md`) — comprehensive table with source-role column
- **Visual Mood + Prototype** (`mood.md` + `prototype.html`) — style direction and clickable skeleton
- **Decision Log** (`decisions.md`) — every decision classified, with role attribution
- **Sprint Plan** (`sprint-plan.md`) — Manager's sprint planning
- **Active Roles** (`roles.yaml`) — which roles participated

**Role Distribution:**
| Phase | Active Roles | Purpose |
|-------|-------------|---------|
| Story | End-user, Developer, DevOps, Security, QA | Perspective gathering |
| Story Synthesis | PM | Conflict resolution, unified requirements |
| Planning | Manager | Sprint planning, spec sequencing |
| Verification | QA | Test quality review, scenario coverage |
| Review | PM | Structured review summary |

The story phase also estimates complexity with story points. The Manager agent always runs sprint planning — deciding how many sprints are needed and which backlog items go into each. Each sprint becomes one Spec with its own execution session.

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

Each intent registered in `ratchet.db` with:
- Unique ID, absolute workspace path (locked at creation)
- Lifecycle state, ticket metadata (priority, tags, brief, current_blocker)

All operations stay within workspace. Commands accept optional intent ID.

### Session Management

**ratchet.db is the single source of truth. Sessions are disposable.**

Multiple Claude Code sessions coordinate through the DB:
- Human session (interactive) + Sprint session (autonomous) can run concurrently
- Sprint execution acquires a DB lock — one sprint per session
- Crash recovery via stale lock detection and force-unlock
- Any session reads DB to know current state and resume

**Session transitions:**
- Sprint complete → check backlog for must items → auto-start next sprint or notify human
- Context filling up → DB has checkpoints → suggest new session
- Session crash → DB lock goes stale → next session detects and offers recovery

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
| manager | opus | Sprint planning |
| env-preparer | sonnet | Install tools, scaffold, validate environment |
| test-generator | sonnet | Constraint tests + scenario tests from test_method |
| wp-executor | sonnet | Execute single WP within workspace |
| verifier | sonnet | 3-level verification + AI review + QA perspective |
| acceptance-{role} | sonnet | Post-sprint perspective validation |
| pm-acceptance | opus | Acceptance summary + verdict |
| report-writer | haiku | Generate iteration reports from DB + files |

Process management (state, gates, ratchet decisions, regression triggers, agent tracking) is handled by Python tools (`tools/ratchet.py`), not by agents.

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

### Story Point Estimation + Sprint Planning

During story phase, agent estimates complexity:

```
1-5 points:    Trivial. Single WP, one session.
5-15 points:   Small. 2-4 WPs, one session.
15-30 points:  Medium. 5-10 WPs, one session.
30-60 points:  Large. Manager splits into multiple sprints.
60+ points:    Very large. Manager splits. Each sprint < 30 points.
```

The Manager always runs sprint planning. Each sprint gets its own story subset, spec, tests, and proofs. Sprint 2's story can reference Sprint 1's deliverables as inputs.

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
└── global_metrics.yaml
```

### Project Workspace
```
<workspace>/.ratchet/
├── ratchet.db                        # SQLite (state, tracking, coordination)
├── project.yaml                      # Project metadata (lightweight)
├── story/                            # Product backlog artifacts (continuous)
│   ├── codebase-analysis.md
│   ├── domain-research.md
│   ├── roles.yaml
│   ├── perspectives/
│   ├── synthesis/
│   ├── personas.md
│   ├── journey.md
│   ├── scenarios.md
│   ├── decisions.md
│   ├── mood.md
│   ├── prototype.html
│   ├── complexity.yaml
│   └── sprint-plan.md
├── sprints/                          # ALL sprints (always, even single)
│   └── sprint-N/
│       ├── backlog-items.yaml
│       ├── spec.yaml
│       ├── plan.yaml
│       ├── pre-validation.log
│       ├── test-suite/
│       ├── scenario-tests/
│       ├── proofs/
│       ├── acceptance/
│       ├── agent-logs/
│       ├── reports/
│       └── metrics.yaml
├── regression/                       # Global regression suite (only grows)
│   ├── manifest.yaml
│   └── S-{id}.test.*
└── tools/ → {plugin}/tools/          # Python tools (symlinked from plugin)
```

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
PM and Manager serve distinct functions. PM synthesizes requirements (what to build — the product backlog), Manager runs sprint planning (how many sprints, what goes in each). Combining them would conflate prioritization with planning. PM runs during story synthesis; Manager always runs after confirmation to plan sprints.

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

### Why story points and sprint planning?
Story point estimation helps the Manager agent make informed sprint planning decisions. The Manager always runs — even for small projects — because sprint planning is a structural step, not a threshold-triggered optimization. A 15-point project might still benefit from being split into two focused sprints rather than one sprawling one.

### Why direct feedback?
Requiring `/ratchet:review` for every piece of feedback adds ceremony without value. When the user sees an issue, they should just say it.

### Why Python tools for process management?
LLMs are probabilistic — they skip steps, forget state updates, and misjudge gates. Process consistency requires deterministic code. Python tools handle everything that must be 100% reliable (state, gates, ratchet decisions, regression triggers). LLMs handle everything that benefits from intelligence (writing code, analyzing requirements, reviewing quality). This separation means SKILL.md files become simple recipes rather than complex process manuals.

### Why SQLite?
Atomic transactions for state consistency. Queryable for status dashboards. WAL mode for concurrent read/write across sessions. Single file for portability. Zero configuration. The DB is the coordination mechanism between sessions and the data source for Ratchet Studio.

### Why living backlog?
In real agile, the backlog grows continuously — new requirements, bugs, acceptance gaps, technical debt. The old model (one-time Story → fixed Spec) doesn't support this. The living backlog means any source (user, agent, review, acceptance) can add items, and sprints continuously consume them.

## Future Directions

- **Ratchet Studio**: Visual DAG, backlog board, agent drill-down, real-time monitoring
- Multi-domain role registries: data science, design, research
- Role memory: perspectives learn from past projects
- Direct role interaction: users converse with individual role agents
- Cross-project learning: global insights from accumulated review logs
- Ratchet as a service: remote execution with webhook notifications
