# Ratchet

Intent-driven execution with autonomous optimization. Describe what you want. The system iterates until it's right.

## How It Works

```
You: "Build a Go CLI tool for managing notes with tags and search"

Ratchet: hybrid 3-step Intent Spec (2 quick decisions, generates spec, you review ~5 min)

→ Test suite auto-generated from spec constraints
→ Workspace registered, agent works autonomously for hours
→ Ratchet loop: try → verify → improved? keep : discard → repeat
→ Proof of work: reports include raw test outputs, not just pass/fail
→ You review async when convenient
→ Your feedback becomes new constraints → next iteration round
→ Done.
```

Like Karpathy's [autoresearch](https://github.com/karpathy/autoresearch), but for any project — software, writing, research — not just ML experiments.

## Install

### Quick test (no setup)
```bash
claude --plugin-dir /path/to/ratchet
```

### Permanent install
```bash
# Add marketplace (replace with your Gitea/GitHub URL)
/plugin marketplace add your-org/marketplace

# Install
/plugin install ratchet@your-marketplace
```

## Commands

```
/ratchet:spec      Intent → Intent Spec + test suite (hybrid 3-step)
/ratchet:plan      Intent Spec → work packages with dependencies
/ratchet:verify    Three-tier verification + ratchet optimization loop
/ratchet:review    Process human review queue (cross-intent)
/ratchet:status    Multi-intent dashboard with lifecycle states
/ratchet:report    Iteration and project reports with proof of work
/ratchet:update    Update Intent Spec mid-project (triggers new round)
/ratchet:profile   Personal preferences (one-time)
/ratchet:metrics   Interaction + automation statistics
/ratchet:pause     Pause an intent's execution
/ratchet:resume    Resume a paused intent
```

Most commands accept an optional intent ID (e.g., `/ratchet:status prism`).

## Key Ideas

**Hybrid 3-step spec.** Intent convergence (2-3 "what" decisions) → generate complete Intent Spec → conversation review with incremental patching. Under 5 minutes.

**Test suite first.** After spec approval, auto-generate test files from each constraint's `test_method`. Tests exist before implementation, so the ratchet loop has real signals from iteration 1.

**Workspace isolation.** Each intent registered with absolute path. Agent stays within workspace. Multi-intent management from any directory via `/ratchet:status`.

**Dual-track verification.** Agent-track constraints (auto + ai_review) run continuously, 24/7. Human-track constraints queue asynchronously. Agent never blocks waiting for you.

**Ratchet loop.** Every work package iterates: execute → verify → improved? keep (git commit) : discard (git reset). Progress only moves forward, like a ratchet wrench.

**Proof of work.** Reports include raw verification outputs — actual test results, ai_review justifications — not just "4/6 passed."

**Feedback conversion.** When you review and say "search feels slow", the system converts that to "search < 200ms" — a constraint the agent can verify automatically. Over time, human-track shrinks, agent-track grows.

**Intent lifecycle.** Full state machine: draft → active → agent_running → agent_complete → human_review → done. Plus pause/resume.

## Architecture

```
~/.config/ratchet/              Global state (profile, intent registry, review queue)
<workspace>/.ratchet/           Project state (Intent Spec, test suite, plan, logs, artifacts)
```

See [DESIGN.md](DESIGN.md) for full architecture, schemas, and design decisions.

## Comparison

|  | Superpower | Kiro | autoresearch | Ratchet |
|--|-----------|------|-------------|---------|
| Brainstorm | ✅ Socratic | ✅ Req-first | ❌ | ✅ Generate-first |
| Structured spec | ❌ Text plan | ⚠️ User stories | ⚠️ program.md | ✅ Dual-track + verifiers |
| Test suite first | ❌ | ❌ | ❌ | ✅ Auto-generated |
| Ratchet loop | ❌ | ❌ | ✅ | ✅ |
| Workspace isolation | ❌ | ✅ IDE | ✅ git branch | ✅ Registry-based |
| Cross-domain | ❌ Software | ❌ Software | ❌ ML only | ✅ Any task |
| Dual-track verify | ❌ | ❌ | ❌ | ✅ |
| Proof of work | ❌ | ❌ | ✅ results.tsv | ✅ Rich reports |
| Feedback→constraint | ❌ | ❌ | ❌ | ✅ |
| Multi-intent | ❌ | ❌ | ❌ | ✅ |

Ratchet complements Superpower. Use both — Superpower's TDD and code review enhance execution quality within each ratchet iteration.

## License

MIT
