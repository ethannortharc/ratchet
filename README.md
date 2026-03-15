# Ratchet

Intent-driven execution with autonomous optimization. Describe what you want. The system iterates until it's right.

## How It Works

```
You: "Build a Go CLI tool for managing notes with tags and search"

Ratchet: generates complete spec, asks 2 questions, you confirm (3 min)

→ Agent works autonomously for hours
→ Ratchet loop: try → verify → improved? keep : discard → repeat
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
/ratchet:spec      Intent → structured spec with dual-track constraints
/ratchet:plan      Spec → work packages with dependencies
/ratchet:verify    Three-tier verification + ratchet optimization loop
/ratchet:review    Process human review queue (cross-project)
/ratchet:status    Multi-project dashboard
/ratchet:report    Iteration and project reports
/ratchet:update    Update spec mid-project (triggers new round)
/ratchet:profile   Personal preferences (one-time)
/ratchet:metrics   Interaction + automation statistics
```

## Key Ideas

**Dual-track verification.** Agent-track constraints (auto + ai_review) run continuously, 24/7. Human-track constraints queue asynchronously. Agent never blocks waiting for you.

**Ratchet loop.** Every work package iterates: execute → verify → improved? keep (git commit) : discard (git reset). Progress only moves forward, like a ratchet wrench.

**Feedback conversion.** When you review and say "search feels slow", the system converts that to "search < 200ms" — a constraint the agent can verify automatically. Over time, human-track shrinks, agent-track grows.

**Agent discovers constraints.** During execution, the agent may find issues not in the spec ("SQLite needs WAL mode for concurrency"). It proposes new constraints for your approval.

**Spec is alive.** Versioned, updatable anytime. Each update triggers a new optimization round from the best result so far.

## Architecture

```
~/.config/ratchet/              Global state (profile, review queue, project index)
<project>/.ratchet/             Project state (spec, plan, logs, reports, artifacts)
```

See [DESIGN.md](DESIGN.md) for full architecture, schemas, and design decisions.

## Comparison

|  | Superpower | Kiro | autoresearch | Ratchet |
|--|-----------|------|-------------|---------|
| Brainstorm | ✅ Socratic | ✅ Req-first | ❌ | ✅ Generate-first |
| Structured spec | ❌ Text plan | ⚠️ User stories | ⚠️ program.md | ✅ Dual-track + verifiers |
| Ratchet loop | ❌ | ❌ | ✅ | ✅ |
| Cross-session | ❌ | ✅ IDE | ✅ git branch | ✅ File-persisted |
| Cross-domain | ❌ Software | ❌ Software | ❌ ML only | ✅ Any task |
| Dual-track verify | ❌ | ❌ | ❌ | ✅ |
| Feedback→constraint | ❌ | ❌ | ❌ | ✅ |
| Agent discovers constraints | ❌ | ❌ | ❌ | ✅ |
| Multi-project | ❌ | ❌ | ❌ | ✅ |
| Reports | ❌ | ❌ | ✅ results.tsv | ✅ Rich reports |

Ratchet complements Superpower. Use both — Superpower's TDD and code review enhance execution quality within each ratchet iteration.

## License

MIT
