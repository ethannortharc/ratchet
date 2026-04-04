# Ratchet

**An experiment in intent-driven autonomous execution for AI agents.**

Ratchet is a Claude Code plugin that explores a different way of working with AI agents: instead of supervising every step, you define your intent upfront, and the system tries to iterate autonomously — keeping improvements, discarding failures — until it converges on a good result.

The name comes from the core mechanism: like a ratchet wrench, progress only moves forward.

> **Status**: Experimental. Being tested on several real projects. Feedback and contributions welcome.

## Install

### Claude Code (via Plugin Marketplace)

Register the marketplace first:

```
/plugin marketplace add ethannortharc/marketplace
```

Then install the plugin:

```
/plugin install ratchet@ethannortharc-marketplace
```

### Gemini CLI

```
gemini extensions install https://github.com/ethannortharc/ratchet
```

Recommended: also install [Superpower](https://github.com/obra/superpowers) for enhanced TDD and code review within each ratchet iteration.

---

## Why This Exists

Today's AI coding agents are powerful but reactive. You prompt, they respond, you review, you prompt again. For a 4-hour project, you're engaged for most of those 4 hours.

Meanwhile, Karpathy's [autoresearch](https://github.com/karpathy/autoresearch) demonstrated something compelling: when an agent has a clear objective and a way to measure progress, it can run 100 experiments overnight while you sleep — each time keeping what works and discarding what doesn't.

But autoresearch works because ML has a single, precise metric (val_bpb). We wanted to explore: **can this pattern generalize to software projects, creative writing, research — tasks with multiple quality dimensions and subjective judgment?**

Ratchet is our attempt at that generalization.

## The Core Insights

Through real usage, we discovered two fundamental problems:

**1. Tests pass ≠ intent satisfied.** Code can be correct but not what the user wanted. The root cause: mixing understanding ("what are we building?") with verification ("how do we check it?") in one step.

**2. Single perspective = blind spots.** A feature looks completely different to an end-user, a developer, DevOps, security, and QA. When we build from one perspective, we ship gaps that no amount of testing catches — because the tests were written from the same narrow perspective.

Ratchet separates understanding from verification, and gathers multiple stakeholder perspectives before specification:

```
Perspectives → Understanding → Specification → Verification → Execution → Proof → Acceptance

Each step formalizes the previous:
  Stakeholder concerns → Human language → Machine language → Machine execution → Evidence → Perspective validation
```

The lifecycle is circular: perspectives start the process AND close it. After execution, role agents review the built output against their original requirements — catching intent gaps that survived formalization.

## Design Hypothesis: EVA

Through building Ratchet, we arrived at a design hypothesis we call **EVA (Environment-Verification Architecture)**:

> **An agent's autonomy is bounded by its verification capability.**

If an agent can verify its own work, it can iterate without human help. If it can't, it must stop and ask. But verification capability depends on specification quality, which depends on understanding alignment, which depends on comprehensive perspective gathering. This leads to the full principle:

**Perspectives-first, then understanding-first, then verification-first, then execution.**

Design principles we're testing:

**Multi-perspective alignment.** Before building anything, gather requirements from all relevant stakeholder roles — end-user, developer, DevOps, security, QA. A PM agent synthesizes these into a unified view. Conflicts are surfaced, not hidden.

**Verification-first specification.** Before building anything, define what "correct" means and confirm you can actually check it. TDD applied at the project level.

**Capability-based tool discovery.** Instead of hardcoding specific tools, the agent reasons about what verification capabilities it needs, discovers what's available, and adapts its approach.

**Dual-track verification.** Separate what machines can check (tests, lints, AI review) from what only humans can judge (taste, direction). Let the machine track run continuously; queue the human track for async review.

**Acceptance closes the loop.** After execution, re-spawn role agents to validate the built output against their original perspectives. Constraints are abstractions of intent — acceptance review catches what abstraction lost.

These are hypotheses, not proven principles. We're testing them through actual use.

## How It Works

### The Flow

```
You: /ratchet:story "Build a REST API for task management"

    [Phase 1: Story — Multi-Perspective Alignment]
    
    Role selection: End-user, Developer, DevOps, Security, QA
    (based on domain + project — you confirm or adjust)
    
    Parallel perspective agents (each inhabits a role):
      End-user: "I call the API, I get data, error messages are clear"
      Developer: "API is RESTful, well-documented, easy to extend"
      DevOps:    "Deployable, monitorable, graceful rollback"
      Security:  "JWT auth, rate limiting, input validation"
      QA:        "Deterministic tests, edge cases defined"
    
    PM synthesis: reconciles all perspectives, resolves conflicts
      "Developer wants API versioning, DevOps concerned about
       deploy complexity → PM: URL prefix /v1/, low overhead"
    
    You see ALL perspectives, review PM's resolutions
    Answer open questions, iterate until confirmed
    
    Manager sequences into specs/phases (for large projects)

    [Phase 2: Spec — Auto-extracted from PM synthesis]
    [Constraints tagged with source roles]
    [Environment negotiation — max auto-coverage]
    [HTML review page — confirm, approve]

You: "Looks good, go."

    === You walk away ===

    [Environment prepared, test suite generated]
    [Work packages executed with ratchet loop]
    [Proof of completion per WP]
    [Verification: build → unit → integration → AI review → QA review]

    [Acceptance Review — role agents review built output]
      End-user: "✓ flows work, △ error messages could be better"
      Developer: "✓ API is clean, ✗ pagination not implemented"
      PM summary: "Ready with caveats — 1 gap to address"

    === Agent notifies: "Ready for review" ===

You: /ratchet:review

    [See results with proof of work + acceptance review]
    [Coverage dashboard: /ratchet:coverage]
    [Feedback → converted to constraints → another round]

    === Done ===
```

### The Ratchet Loop

Borrowed directly from [autoresearch](https://github.com/karpathy/autoresearch):

```
Execute work package
    → Verify against agent-track constraints (short-circuit: build fail → immediate retry)
    → Composite score improved? → git commit (keep)
    → Score didn't improve? → git reset (discard)
    → Stuck detected? → Change strategy or escalate early
    → All constraints pass? → Run acceptance review → queue for human review
    → Budget remaining? → Try again with failure feedback
    → Budget exhausted? → Escalate to human
```

Each iteration is at least as good as the last. Progress is monotonic.

## What We Learned From Others

Ratchet doesn't exist in a vacuum. It draws heavily from several projects:

### From [autoresearch](https://github.com/karpathy/autoresearch) — The ratchet loop

Karpathy's project proved that modify → measure → keep/discard → repeat is a powerful pattern for autonomous improvement. We adopted this as our core execution mechanism.

### From [Superpower](https://github.com/obra/superpowers) — Skill-based plugin architecture

Jesse Vincent's Superpower plugin demonstrated that Claude Code plugins can encode entire development methodologies. We borrowed the skill architecture pattern. **Ratchet complements Superpower** — Superpower's TDD and code review skills enhance execution quality within each ratchet iteration.

### From [Symphony](https://github.com/openai/symphony) — Workspace isolation and proof of work

OpenAI's Symphony introduced isolated workspaces per task, lifecycle state machines, and requiring "proof of work" before considering a task complete.

### From [Kiro](https://kiro.dev/) — Spec-driven development

Amazon's Kiro demonstrated that starting from structured specifications produces more maintainable output. Our Intent Spec takes this further by adding verification methods and ratchet metrics to each constraint.

## Key Concepts

### Multi-Perspective Story Phase

Phase 1: gather requirements from all relevant stakeholder roles, synthesize into a unified view.

**Role agents** (parallel, on Sonnet) each produce requirements from their perspective:

| Role | What it contributes |
|------|-------------------|
| **End User** | Flows, usability, accessibility, perceived performance |
| **Developer** | API design, maintainability, extensibility, DX |
| **DevOps / SRE** | Deployment, monitoring, scaling, logging |
| **Security** | Auth, data protection, input validation, threat surface |
| **QA / Tester** | Testability, edge cases, scenario completeness |

**PM agent** (on Opus) reads all perspectives, resolves conflicts, and produces:
- Unified requirements table (prioritized, role-tagged)
- Conflict resolution log (who disagreed, how it was resolved)
- Comprehensive scenario table (with source-role column)
- Scope boundary (in-scope, out-of-scope, debated)

**Manager agent** (on Opus) sequences confirmed requirements into specs/phases for large projects.

Roles are domain-specific. Software development is the first supported domain (`references/role-registry.yaml`). Projects can add custom roles or exclude irrelevant ones.

### Intent Spec

The structured output of the spec phase. When story artifacts exist, constraints are auto-extracted from PM synthesis. Each constraint is tagged with which roles identified it:

```yaml
invariants:
  - id: INV-03
    claim: "Rate limiting on all production endpoints"
    source: "synthesis.md R-05, security perspective CONSTRAINT-1"
    source_roles: [security, devops]
    track: agent
    verifier: auto
    test_method: |
      Unit: rate limiter returns 429 after threshold
      Integration: concurrent requests → verify throttling
    tools_required:
      - id: [project-test-runner]
        install: "[install command]"
        agent_can_install: true
    ratchet_metric: "passed_tests / total_tests"
```

### Perspective Acceptance Review

After all work packages pass verification, role agents are re-spawned to review the **actual built output** against their **original perspective documents**. This catches intent gaps that survived the spec formalization:

```
Constraint check:  "API < 200ms" → PASS
Acceptance review: "Page makes 15 sequential calls = 3s total" → FLAGGED by End User
```

The PM produces an acceptance summary with a verdict: ready for human review, ready with caveats, or needs another iteration. Gaps can trigger new constraints and ratchet retries.

### Decision Classification

Every decision point is classified:

- **human_must_decide** — resolved in story/spec phase, never silently assumed
- **agent_can_decide** — agent chooses freely, documents choice in Proof of Completion
- **unknown** — if UX impact, escalate to human; if technical, decide and document

### Proof of Completion

Every completed WP produces a proof document:
- What was built, what decisions were made (and why)
- Role requirements addressed (which role's needs this WP satisfies)
- Scenario coverage table with actual results
- What was NOT covered — forces honesty about gaps
- How the user can manually verify

### Coverage Dashboard

Four-layer view available anytime via `/ratchet:coverage`:
- **Layer 1**: Which user journey steps are implemented?
- **Layer 1.5**: Which role perspectives are addressed?
- **Layer 2**: Which scenarios are tested?
- **Layer 3**: Code coverage, test results, review status

### Feedback Conversion

When you say "the search feels slow" during review, the system tries to convert that into an auto-verifiable constraint like `search_latency < 200ms`. Each review cycle shrinks the human track.

### Session Management

Files are the single source of truth. Sessions are disposable. Each phase starts a new session for best quality. The getting-started skill detects state on session start and resumes automatically.

## Architecture

```
~/.config/ratchet/                        Global: profile, intent registry, review queue
<project>/.ratchet/story/                 Story artifacts (Phase 1)
<project>/.ratchet/story/perspectives/    Per-role perspective documents
<project>/.ratchet/story/synthesis.md     PM synthesis output
<project>/.ratchet/{intent-id}/           Per-intent: spec, plan, tests, proofs, acceptance
<project>/.ratchet/phases/                Multi-phase projects (> 30 story points)
```

Ratchet uses Claude Code's subagent system for parallel execution:

| Agent | Model | Purpose |
|-------|-------|---------|
| perspective-{role} | Sonnet | Role-specific requirements gathering (parallel) |
| pm-synthesis | Opus | Synthesize perspectives, resolve conflicts |
| manager | Opus | Spec sequencing, phase planning |
| env-preparer | Sonnet | Install tools, scaffold, validate environment |
| test-generator | Sonnet | Generate test suite from spec constraints |
| wp-executor | Sonnet | Execute single work package |
| verifier | Sonnet | 3-level verification + AI review + QA perspective |
| report-writer | Haiku | Generate iteration reports |

### Claude Code Features Used

| Feature | How Ratchet Uses It |
|---------|-------------------|
| **Plugin system** (commands/, skills/) | All user-facing commands and internal workflows |
| **Subagent architecture** (Agent tool) | Role agents, wp-executor, verifier, env-preparer, test-generator, report-writer |
| **Model selection per subagent** | Perspective agents on Sonnet, PM/Manager on Opus, report-writer on Haiku |
| **Background agents** (run_in_background) | Perspective agents and independent WPs execute in parallel |
| **Skill system** | Internal workflow chaining (story → spec → execute → verify → acceptance) |

See [DESIGN.md](DESIGN.md) for the complete architecture, schemas, and design decisions.

## Usage

```bash
# Start a project — story first (recommended)
/ratchet:story "your intent description"
# → Role selection, parallel perspectives, PM synthesis
# → Iterate until "this is what I want"
# → Auto-transitions to spec

# Or go directly to spec for simple projects
/ratchet:spec "your intent description"

# Come back when notified
/ratchet:review
# → Review results with proof of work + acceptance review

# Check coverage anytime (includes perspective coverage)
/ratchet:coverage

# Check progress anytime
/ratchet:status
```

### Updating Existing Projects

Just describe the change in conversation:

```
"Fix the sharing link on the personality test"
"Add dark mode to the quiz results page"
```

The agent routes to the matching intent and cascades: story update → spec re-derive → test update → execute → verify → acceptance review.

### When to Use Ratchet

- **Single bug, obvious fix** → just fix it directly
- **Batch of related bugs** → one intent, one WP per bug
- **Systemic improvement** ("Lighthouse 60 → 90") → perfect for ratchet loop
- **New feature** → `/ratchet:story` for the full flow
- **Simple technical project** → `/ratchet:spec` directly (skip story)

## Limitations and Open Questions

- **Autonomy ratio varies widely by project type.** Software with good test coverage achieves high automation. Creative projects need more human judgment.
- **AI review as a verification tier has noise.** Using AI to judge AI works for structural checks but is unreliable for subjective quality.
- **Spec quality is everything.** Multi-perspective story phase helps, but the system is only as good as the perspectives gathered and the PM's synthesis quality.
- **Role agents add upfront cost.** 5 parallel perspective agents + PM synthesis takes time. The trade-off is catching blind spots early rather than discovering them in review.
- **Acceptance review is AI judging AI.** Role agents reviewing built output is better than no review, but not as reliable as human acceptance testing.
- **Session management is manual.** The agent suggests when to start a new session, but the user has to actually do it.
- **Only software development roles so far.** The role registry supports one domain. Multi-domain support (data science, design, research) is future work.

## Philosophy

Ratchet is built on a belief about human-AI collaboration that we're testing through practice:

**Humans provide direction and taste. Agents handle execution and verification. When agents can't verify something, they should try to create the conditions to verify it — not just ask for help.**

Human attention is the scarcest resource. It should be spent only where it uniquely matters: deciding what to build and judging whether the result matches your vision. Multi-perspective alignment ensures that "what to build" is informed by all stakeholders — not just the loudest voice in the room.

> *"You are programming the program.md Markdown files that provide context to the AI agents and set up your autonomous research org."*
> — Andrej Karpathy, autoresearch

Replace "program.md" with "story + perspectives + Intent Spec" and "ML experiments" with "any project." That's the idea we're exploring with Ratchet.

## License

MIT

## Acknowledgments

Ratchet's design is informed by ideas from:

- **[autoresearch](https://github.com/karpathy/autoresearch)** by Andrej Karpathy — the ratchet loop pattern
- **[Superpower](https://github.com/obra/superpowers)** by Jesse Vincent — skill-based plugin architecture for AI agents
- **[Symphony](https://github.com/openai/symphony)** by OpenAI — workspace isolation, lifecycle states, proof of work
- **[Kiro](https://kiro.dev/)** by Amazon — spec-driven development

We're standing on the shoulders of these projects. Ratchet is our attempt to synthesize their insights into a unified, cross-domain framework for autonomous agent execution.
