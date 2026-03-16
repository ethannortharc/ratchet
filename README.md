# Ratchet

**An experiment in intent-driven autonomous execution for AI agents.**

Ratchet is a Claude Code plugin that explores a different way of working with AI agents: instead of supervising every step, you define your intent upfront, and the system tries to iterate autonomously — keeping improvements, discarding failures — until it converges on a good result.

The name comes from the core mechanism: like a ratchet wrench, progress only moves forward.

> **Status**: Experimental. Being tested on several real projects. Feedback and contributions welcome.

---

## Why This Exists

Today's AI coding agents are powerful but reactive. You prompt, they respond, you review, you prompt again. For a 4-hour project, you're engaged for most of those 4 hours.

Meanwhile, Karpathy's [autoresearch](https://github.com/karpathy/autoresearch) demonstrated something compelling: when an agent has a clear objective and a way to measure progress, it can run 100 experiments overnight while you sleep — each time keeping what works and discarding what doesn't.

But autoresearch works because ML has a single, precise metric (val_bpb). We wanted to explore: **can this pattern generalize to software projects, creative writing, research — tasks with multiple quality dimensions and subjective judgment?**

Ratchet is our attempt at that generalization.

## Design Hypothesis: EVA

Through building Ratchet, we arrived at a design hypothesis we call **EVA (Environment-Verification Architecture)**:

> **An agent's autonomy is bounded by its verification capability.**

If an agent can verify its own work, it can iterate without human help. If it can't, it must stop and ask. This leads to three design principles we're testing:

**Verification-first specification.** Before building anything, define what "correct" means and confirm you can actually check it. This is TDD applied at the project level, not just the code level.

**Capability-based tool discovery.** Instead of hardcoding specific tools, the agent reasons about what verification capabilities it needs, discovers what's available in the environment, and adapts its approach. "I need browser testing capability" rather than "I need Playwright."

**Dual-track verification.** Separate what machines can check (tests, lints, AI review against rubrics) from what only humans can judge (taste, direction, "does this feel right"). Let the machine track run continuously; queue the human track for async review. This way agent work is never blocked waiting for a human who's asleep or busy.

These are hypotheses, not proven principles. We're testing them through actual use.

## How It Works

### The Ratchet Loop

Borrowed directly from [autoresearch](https://github.com/karpathy/autoresearch)'s core pattern:

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

### The Complete Flow

```
You: /ratchet:spec "Build an online personality test website"

    [Agent researches the domain — scoring methods, question design, best practices]
    [Asks a few foundational "what" questions — never "how"]
    [Generates complete Intent Spec with constraints and verification plan]
    [You confirm and adjust — 5 to 30 minutes depending on complexity]

You: "Looks good, go."

    === You walk away ===

    [Environment prepared, capabilities discovered, test suite generated]
    [Work packages decomposed and executed with ratchet loop]
    [TDD inner loop: executor builds incrementally, testing after each function]
    [Verification short-circuits: build fail → immediate retry, no wasted tokens]
    [Stuck detection: same error 3x → strategy change, score plateau → new approach]
    [Per-WP reports generated as each completes]

    === Agent notifies: "Ready for review" ===

You: /ratchet:review

    [See results with proof of work: test outputs, scores, resource usage]
    [Give feedback — gets converted to new constraints when possible]
    [New iteration round if needed]

    === Done ===
```

In practice, human time is mostly in the spec phase (where it has the highest ROI) and the review phase. The goal is to minimize everything in between, though we're still learning what the realistic autonomy ratio is for different project types.

## What We Learned From Others

Ratchet doesn't exist in a vacuum. It draws heavily from several projects, each of which contributed a key insight:

### From [autoresearch](https://github.com/karpathy/autoresearch) — The ratchet loop

Karpathy's project proved that modify → measure → keep/discard → repeat is a powerful pattern for autonomous improvement. We adopted this as our core execution mechanism. The difference is that autoresearch optimizes a single metric on a single file; we're attempting to apply the same pattern to multi-dimensional projects with multiple work packages.

### From [Superpower](https://github.com/obra/superpowers) — Skill-based plugin architecture

Jesse Vincent's Superpower plugin demonstrated that Claude Code plugins can encode entire development methodologies, not just shortcuts. We borrowed the skill architecture pattern and the idea that disciplined processes (TDD, structured planning) should be encoded as mandatory workflows, not optional suggestions. **Ratchet complements Superpower** — Superpower's TDD and code review skills enhance execution quality within each ratchet iteration.

### From [Symphony](https://github.com/openai/symphony) — Workspace isolation and proof of work

OpenAI's Symphony introduced the idea of isolated workspaces per task, lifecycle state machines, and requiring "proof of work" (passing tests, CI green) before considering a task complete. We adopted workspace isolation for multi-intent support and the proof-of-work concept for our iteration reports.

### From [Kiro](https://kiro.dev/) — Spec-driven development

Amazon's Kiro demonstrated that starting from structured specifications (rather than freeform prompts) produces more maintainable output. Our Intent Spec concept takes this further by adding verification methods and ratchet metrics to each constraint, making specs not just documentation but executable verification plans.

## Key Concepts

### Intent Spec

The structured output of the spec phase. Not a requirements document — it captures intent, constraints, quality standards, and verification methods:

- **Invariants** — hard constraints that must not be violated
- **Quality dimensions** — measurable targets with rubrics and thresholds
- **Preferences** — soft guidance
- **Delivery direction** — UI/UX mood, interaction patterns, visual references
- **Verification plan** — every constraint has a test method, required capabilities, and a ratchet metric

Each constraint is assigned a **track** (agent or human) and a **verifier** (auto, ai_review, or human). Here's what a constraint looks like:

```yaml
invariants:
  - id: INV-03
    claim: "Scoring logic produces correct personality type"
    track: agent
    verifier: auto
    test_method: |
      Unit: all 9 type scores, tie-breaking, boundary values
      Integration: complete quiz → verify correct type displayed
    tools_required:                        # use the project's actual test runner
      - id: [project-test-runner]
        install: "[install command]"
        agent_can_install: true
    ratchet_metric: "passed_tests / total_tests"
```

The `test_method` drives automatic test generation. The `tools_required` drives environment preparation. The `ratchet_metric` drives the keep/discard decision.

### Domain Research

For domain-specific projects (personality tests, financial tools, medical apps), the agent researches the domain before generating the spec — scoring methodologies, question design best practices, common pitfalls. Domain errors in the spec cascade into everything downstream; 5 minutes of research saves hours of rework.

### Feedback Conversion

When you say "the search feels slow" during review, the system tries to convert that into an auto-verifiable constraint like `search_latency < 200ms`. Conversion patterns are organized by domain (software, creative writing, research, design) in a structured reference file. The idea is that each review cycle shrinks the human track by converting subjective observations into objective checks. This works well for some types of feedback and not at all for others — "the story is boring" doesn't have a good automated proxy.

### Constraint Discovery

During execution, the agent may discover issues not covered by the spec ("SQLite needs WAL mode for concurrent access"). Rather than silently fixing these, it proposes them as new constraints for human approval, capturing knowledge that would otherwise be lost.

### Stuck Detection

The ratchet loop includes two stuck detectors that fire before budget exhaustion:

- **Repeated failure** — same constraint fails 3+ times with same error pattern → escalating hints (try different approach → suggest re-decomposition → early human escalation)
- **Score oscillation** — composite score plateaus across 3 iterations → strategy change hint

This prevents wasting budget on dead-end strategies.

### Multi-Intent Workspaces

Multiple intents can share the same project directory. Each intent gets its own isolated subdirectory:

```
<project>/.ratchet/
├── prism-enneagram/     # First intent
│   ├── spec.yaml
│   ├── test-suite/
│   └── reports/
└── prism-mbti/          # Second intent, same codebase
    ├── spec.yaml
    ├── test-suite/
    └── reports/
```

Existing intents can be reactivated for updates — the agent routes to the right intent based on what you describe, no need to remember intent IDs.

## Architecture

```
~/.config/ratchet/                  Global: profile, intent registry, review queue
<project>/.ratchet/{intent-id}/     Per-intent: spec, plan, tests, logs, reports
```

Ratchet uses Claude Code's subagent system for parallel execution — environment preparation, test generation, work package execution, and verification each run as focused subagents, while the main agent orchestrates.

### Claude Code Features Used

Ratchet relies on several Claude Code capabilities:

| Feature | How Ratchet Uses It |
|---------|-------------------|
| **Plugin system** (commands/, skills/) | All user-facing commands and internal workflows |
| **Subagent architecture** (Agent tool) | wp-executor, verifier, env-preparer, test-generator, report-writer — each as isolated subagents with dedicated context |
| **Model selection per subagent** | Executor/verifier on Sonnet (focused tasks), report-writer on Haiku (summarization) |
| **Background agents** (run_in_background) | Independent work packages execute in parallel |
| **Skill system** | Internal workflow chaining (spec → execute → verify) |

See [DESIGN.md](DESIGN.md) for the complete architecture, schemas, and design decisions.

## Install

```bash
# Quick test
claude --plugin-dir /path/to/ratchet

# Via marketplace
/plugin marketplace add your-org/marketplace
/plugin install ratchet@your-marketplace
```

Recommended: also install [Superpower](https://github.com/obra/superpowers) for enhanced TDD and code review within each ratchet iteration.

## Usage

```bash
# Start a project
/ratchet:spec "your intent description"
# → Discuss, confirm, agent takes over

# Come back when notified
/ratchet:review
# → Review results, give feedback, or approve

# Optional: check progress anytime
/ratchet:status
```

Two commands for the normal flow. Everything else is automated.

### Updating Existing Projects

You don't need a special command. Just describe the change in conversation:

```
"Fix the sharing link on the personality test"
"Add dark mode to the quiz results page"
```

The agent checks the intent registry, finds the matching intent, and routes to it — updating the spec, regenerating tests, and running a new iteration. If the intent is already marked as done, it gets reactivated.

### When to Use Ratchet

Not everything needs the full pipeline:

- **Single bug, obvious fix** → just fix it directly, no Ratchet needed
- **Batch of related bugs** → one intent, one WP per bug — Ratchet verifies all are fixed
- **Systemic improvement** ("Lighthouse 60 → 90") → perfect for ratchet loop, measurable progress
- **New feature** → `/ratchet:spec` for the full flow

## Limitations and Open Questions

We want to be upfront about what we don't know yet:

- **Autonomy ratio varies widely by project type.** Software projects with good test coverage achieve high automation. Creative projects still need frequent human judgment. We don't have enough data to quote reliable numbers.
- **AI review as a verification tier has noise.** Using one AI to judge another AI's output works for structural checks (consistency, format) but is unreliable for subjective quality.
- **Spec quality is everything.** A vague spec produces vague results no matter how many ratchet iterations you run. Domain research helps, but the system is only as good as the intent you put in.
- **Cross-project learning is theoretical.** We designed for it (review logs with reason classification, pattern detection), but don't have enough accumulated data to validate that it works in practice.
- **Capability discovery is heuristic.** The agent probes the environment for verification capabilities, but it may miss tools it doesn't know about or misjudge headless compatibility. We're iterating on making this more robust.

## Philosophy

Ratchet is built on a belief about human-AI collaboration that we're testing through practice:

**Humans provide direction and taste. Agents handle execution and verification. When agents can't verify something, they should try to create the conditions to verify it — not just ask for help.**

Human attention is the scarcest resource. It should be spent only where it uniquely matters: deciding what to build and judging whether the result matches your vision.

> *"You are programming the program.md Markdown files that provide context to the AI agents and set up your autonomous research org."*
> — Andrej Karpathy, autoresearch

Replace "program.md" with "Intent Spec" and "ML experiments" with "any project." That's the idea we're exploring with Ratchet.

## License

MIT

## Acknowledgments

Ratchet's design is informed by ideas from:

- **[autoresearch](https://github.com/karpathy/autoresearch)** by Andrej Karpathy — the ratchet loop pattern
- **[Superpower](https://github.com/obra/superpowers)** by Jesse Vincent — skill-based plugin architecture for AI agents
- **[Symphony](https://github.com/openai/symphony)** by OpenAI — workspace isolation, lifecycle states, proof of work
- **[Kiro](https://kiro.dev/)** by Amazon — spec-driven development

We're standing on the shoulders of these projects. Ratchet is our attempt to synthesize their insights into a unified, cross-domain framework for autonomous agent execution.
