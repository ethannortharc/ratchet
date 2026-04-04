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

## The Core Insight

Through real usage, we discovered: **tests pass ≠ intent satisfied.** Code can be correct but not what the user wanted. The root cause: mixing understanding ("what are we building?") with verification ("how do we check it?") in one step.

Ratchet separates them:

```
Understanding (story) → Specification (spec) → Verification (test) → Execution (code) → Proof (evidence)

Each step formalizes the previous:
  Human intuition → Human language → Machine language → Machine execution → Human-readable evidence
```

## Design Hypothesis: EVA

Through building Ratchet, we arrived at a design hypothesis we call **EVA (Environment-Verification Architecture)**:

> **An agent's autonomy is bounded by its verification capability.**

If an agent can verify its own work, it can iterate without human help. If it can't, it must stop and ask. But verification capability depends on specification quality, which depends on understanding alignment. This leads to the full principle:

**Understanding-first, then verification-first, then execution.**

Three design principles we're testing:

**Verification-first specification.** Before building anything, define what "correct" means and confirm you can actually check it. TDD applied at the project level.

**Capability-based tool discovery.** Instead of hardcoding specific tools, the agent reasons about what verification capabilities it needs, discovers what's available, and adapts its approach.

**Dual-track verification.** Separate what machines can check (tests, lints, AI review) from what only humans can judge (taste, direction). Let the machine track run continuously; queue the human track for async review.

These are hypotheses, not proven principles. We're testing them through actual use.

## How It Works

### The Flow

```
You: /ratchet:story "Build an online personality test website"

    [Phase 1: Story — Human-Language Alignment]
    [Agent generates personas, user journey, scenario coverage]
    [You iterate on the prototype: "radar chart bigger, description on right"]
    [Complexity estimated, phases split if needed]
    [You confirm: "this is what I want"]

    [Phase 2: Spec — Auto-extracted from story]
    [Constraints derived from journey, scenarios, decisions]
    [Environment negotiation — what tools to install for max coverage]
    [HTML review page — confirm constraints, approve]

You: "Looks good, go."

    === You walk away ===

    [Environment prepared, capabilities discovered, test suite generated]
    [Work packages decomposed and executed with ratchet loop]
    [Proof of completion generated per WP]
    [Verification short-circuits: build fail → immediate retry]
    [Stuck detection: same error 3x → strategy change]

    === Agent notifies: "Ready for review" ===

You: /ratchet:review

    [See results with proof of work]
    [Check coverage: /ratchet:coverage]
    [Give feedback — gets converted to new constraints]
    [New iteration round if needed]

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
    → All constraints pass? → Queue for human review
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

### Story Phase

Phase 1: human-language alignment before specification. Produces five artifacts:

- **Personas** — behavioral patterns of target users, not demographics
- **User Journey** — narrative walkthrough of the complete experience
- **Scenario Coverage** — happy path + edge cases + explicit out-of-scope exclusions
- **Visual Mood + Prototype** — clickable HTML skeleton for direction confirmation
- **Decision Log** — every decision classified and tracked

The story phase also estimates project complexity with story points. Projects over 30 points are split into phases, each with its own spec and execution session.

### Intent Spec

The structured output of the spec phase. When story artifacts exist, constraints are auto-extracted from them. Each constraint has a verification method, required capabilities, and a ratchet metric:

```yaml
invariants:
  - id: INV-03
    claim: "Scoring logic produces correct personality type"
    source: "journey.md step 4, scenarios.md normal-01"
    track: agent
    verifier: auto
    test_method: |
      Unit: all 9 type scores, tie-breaking, boundary values
      Integration: complete quiz → verify correct type displayed
    tools_required:
      - id: [project-test-runner]
        install: "[install command]"
        agent_can_install: true
    ratchet_metric: "passed_tests / total_tests"
```

### Decision Classification

Every decision point is classified:

- **human_must_decide** — resolved in story/spec phase, never silently assumed
- **agent_can_decide** — agent chooses freely, documents choice in Proof of Completion
- **unknown** — if UX impact, escalate to human; if technical, decide and document

### Proof of Completion

Every completed WP produces a proof document:
- What was built, what decisions were made (and why)
- Scenario coverage table with actual results
- What was NOT covered — forces honesty about gaps
- How the user can manually verify

### Coverage Dashboard

Three-layer view available anytime via `/ratchet:coverage`:
- **Layer 1**: Which user journey steps are implemented?
- **Layer 2**: Which scenarios are tested?
- **Layer 3**: Code coverage, test results, review status

### Feedback Conversion

When you say "the search feels slow" during review, the system tries to convert that into an auto-verifiable constraint like `search_latency < 200ms`. Each review cycle shrinks the human track.

### Stuck Detection

- **Repeated failure** — same constraint fails 3+ times with same error → escalating hints
- **Score oscillation** — composite score plateaus → strategy change hint

### Session Management

Files are the single source of truth. Sessions are disposable. Each phase starts a new session for best quality. The getting-started skill detects state on session start and resumes automatically.

## Architecture

```
~/.config/ratchet/                  Global: profile, intent registry, review queue
<project>/.ratchet/story/           Story artifacts (Phase 1)
<project>/.ratchet/{intent-id}/     Per-intent: spec, plan, tests, proofs, reports
<project>/.ratchet/phases/          Multi-phase projects (> 30 story points)
```

Ratchet uses Claude Code's subagent system for parallel execution — environment preparation, test generation, work package execution, and verification each run as focused subagents.

### Claude Code Features Used

| Feature | How Ratchet Uses It |
|---------|-------------------|
| **Plugin system** (commands/, skills/) | All user-facing commands and internal workflows |
| **Subagent architecture** (Agent tool) | wp-executor, verifier, env-preparer, test-generator, report-writer |
| **Model selection per subagent** | Executor/verifier on Sonnet, report-writer on Haiku |
| **Background agents** (run_in_background) | Independent work packages execute in parallel |
| **Skill system** | Internal workflow chaining (story → spec → execute → verify) |

See [DESIGN.md](DESIGN.md) for the complete architecture, schemas, and design decisions.

## Usage

```bash
# Start a project — story first
/ratchet:story "your intent description"
# → Personas, journey, scenarios, prototype
# → Iterate until "this is what I want"
# → Auto-transitions to spec

# Or go directly to spec for simple projects
/ratchet:spec "your intent description"

# Come back when notified
/ratchet:review
# → Review results with proof of work

# Check coverage anytime
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

The agent routes to the matching intent and cascades: story update → spec re-derive → test update → execute → verify.

### When to Use Ratchet

- **Single bug, obvious fix** → just fix it directly
- **Batch of related bugs** → one intent, one WP per bug
- **Systemic improvement** ("Lighthouse 60 → 90") → perfect for ratchet loop
- **New feature** → `/ratchet:story` for the full flow
- **Simple technical project** → `/ratchet:spec` directly (skip story)

## Limitations and Open Questions

- **Autonomy ratio varies widely by project type.** Software with good test coverage achieves high automation. Creative projects need more human judgment.
- **AI review as a verification tier has noise.** Using AI to judge AI works for structural checks but is unreliable for subjective quality.
- **Spec quality is everything.** Story phase helps, but the system is only as good as the intent you put in.
- **Story phase adds upfront time.** The trade-off is less rework later, but we're still measuring the net effect.
- **Session management is manual.** The agent suggests when to start a new session, but the user has to actually do it.
- **Cross-project learning is theoretical.** Designed for it, not enough data to validate yet.

## Philosophy

Ratchet is built on a belief about human-AI collaboration that we're testing through practice:

**Humans provide direction and taste. Agents handle execution and verification. When agents can't verify something, they should try to create the conditions to verify it — not just ask for help.**

Human attention is the scarcest resource. It should be spent only where it uniquely matters: deciding what to build and judging whether the result matches your vision.

> *"You are programming the program.md Markdown files that provide context to the AI agents and set up your autonomous research org."*
> — Andrej Karpathy, autoresearch

Replace "program.md" with "story + Intent Spec" and "ML experiments" with "any project." That's the idea we're exploring with Ratchet.

## License

MIT

## Acknowledgments

Ratchet's design is informed by ideas from:

- **[autoresearch](https://github.com/karpathy/autoresearch)** by Andrej Karpathy — the ratchet loop pattern
- **[Superpower](https://github.com/obra/superpowers)** by Jesse Vincent — skill-based plugin architecture for AI agents
- **[Symphony](https://github.com/openai/symphony)** by OpenAI — workspace isolation, lifecycle states, proof of work
- **[Kiro](https://kiro.dev/)** by Amazon — spec-driven development

We're standing on the shoulders of these projects. Ratchet is our attempt to synthesize their insights into a unified, cross-domain framework for autonomous agent execution.
