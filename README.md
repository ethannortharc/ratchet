# Ratchet

Intent-driven execution with autonomous optimization. Describe what you want. The system iterates until it's right.

## How It Works

```
You: /ratchet:spec "Build a personality test website called Prism"

Ratchet: Asks 2-3 direction questions, generates full Intent Spec
         with UI direction, constraints, and verification plan.
         You review thoroughly — take 5 minutes or 30, no rush.

You: "Looks good, start."

=== You walk away ===

Ratchet: Installs tools, generates tests, validates pipeline,
         decomposes into work packages, executes with ratchet loop
         (try → verify → improved? keep : discard → repeat),
         captures proof of work, queues human review items.

=== Later ===

Ratchet: "Ready for review."

You: /ratchet:review
     "Search feels slow" → auto-converted to "search < 200ms" constraint
     → Another autonomous round → Done.

Total human time: ~45 min. Total agent time: hours.
```

## Commands

```
/ratchet:spec      Start new intent (main command — everything chains from here)
/ratchet:review    Review results, give feedback
/ratchet:status    Check progress anytime
/ratchet:pause     Pause execution
/ratchet:resume    Resume execution
```

Most workflows use only `spec` and `review`.

## Key Ideas

**Two human touchpoints.** Spec (provide direction + taste) and review (evaluate results). Everything between runs autonomously.

**Thorough spec, fast execution.** No time limit on spec review — invest here to avoid rework. Agent generates complete spec with delivery/UI direction, constraints, multi-level test methods.

**Maximum coverage.** Agent aggressively maximizes auto-verification. Basic functionality (pages load, buttons work, navigation works) is NEVER left to human review. Agent requests tools to enable this.

**EVA (Early Verification Architecture).** Before execution, validate that all tools are installed, tests can run, and build works. Catch infrastructure problems early.

**Ratchet loop.** Every iteration either improves (git commit) or doesn't (git reset). Progress only moves forward.

**Subagent architecture.** Parallel execution via specialized subagents — env-preparer, test-generator, wp-executor, verifier, report-writer.

**Direct feedback.** Say issues directly in conversation — no need for formal commands. "The results page is broken" triggers the same feedback→constraint→iteration loop.

## Architecture

```
~/.config/ratchet/              Global (profile, intent registry, review queue)
<workspace>/.ratchet/           Per-intent (spec, test suite, plan, logs, reports)
```

See [DESIGN.md](DESIGN.md) for full architecture.

## License

MIT
