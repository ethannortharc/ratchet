---
name: spec
description: Transform intent into a structured, verifiable specification (spec.yaml) with dual-track constraints and ratchet configuration. Use whenever the user describes something they want to build, create, write, or accomplish. Generates complete specs with industry knowledge, auto-assigns verification tracks (agent/human) and verifier types (auto/ai_review/human) based on environment capabilities. Always use this before implementation for non-trivial tasks.
---

# Spec — Intent Formalization

## Workflow

### Step 1: Load Profile

Check `~/.config/ratchet/profile.yaml`. If exists, load preferences. If not, proceed with defaults and suggest `/ratchet:profile` afterward.

### Step 2: Analyze Intent

The user provides intent — one sentence to several paragraphs.

1. Identify project type: `software` | `creative_writing` | `research` | `design` | `general`
2. Generate a COMPLETE spec draft using: user's intent + industry knowledge (read `references/inquiry-protocols.md`) + profile preferences + reasonable assumptions
3. Assess confidence per constraint: ✅ high | ⚠️ medium (flag assumption) | ❓ low (must ask)

### Step 3: Environment Discovery

```bash
which go 2>/dev/null && go version
which node 2>/dev/null && node --version
which python3 2>/dev/null && python3 --version
which docker 2>/dev/null && docker --version
which git 2>/dev/null && git --version
which claude 2>/dev/null && claude --version
ls ~/.claude/plugins/ 2>/dev/null
```

### Step 4: Environment Negotiation (be aggressive)

Calculate what COULD be auto-verified with additional tools. Present:

```
Current auto-verification coverage: X%
With recommended tools: Y%

Strongly recommended:
  ⬜ [tool] — unlocks N auto-verifications
     Install: [one-line command]
     I can install this myself: [yes/no]
```

For tools you can install (npm/pip packages, plugins): offer to install immediately.

### Step 5: Assign Tracks and Verifiers

For EVERY constraint, assign:
- `track: agent` if verifiable by auto or ai_review
- `track: human` ONLY if genuinely subjective with no automated proxy
- Prefer: auto > ai_review > human

For each constraint, define `ratchet_metric` — a quantified progress indicator, not just pass/fail:
- Test pass rate: "passed_tests / total_tests"
- AI review: the rubric score itself (1-5)
- Coverage: "covered_items / total_items"

### Step 6: Configure Ratchet

Based on project type and verifier distribution:

```yaml
ratchet:
  enabled: true
  backend: git  # auto-detect: .git exists? git : filesystem
  default_budget: # software: 8-10, creative: 5, research: 5
  composite_score:
    method: weighted_average
    weights:
      auto_pass_rate: 0.5
      ai_review_avg: 0.3
```

### Step 7: Generate spec.yaml

Create `.ratchet/` directory if needed. Write spec.yaml per schema in `references/spec-schema.md`.

### Step 8: Present and Confirm

Show readable summary (NOT raw YAML):

```
📋 Spec for "[name]" (v1)

What I'll build:
  [2-3 sentences]

Key constraints: [N] total
  Agent track: [N] (auto: X, ai_review: Y) — runs without you
  Human track: [N] — you'll review when ready

Ratchet: [budget] iterations per work package

⚠️ I assumed:
  1. [assumption]

❓ I need your input on:
  1. [question — max 3]
```

### Step 9: Register Project

Update `~/.config/ratchet/state.yaml` with project entry.

### Step 10: Record Metrics

Append to `.ratchet/metrics.yaml`: timestamp, human_interactions, confidence_distribution, auto_coverage.

## Rules

1. **Max 3 questions.** If you're asking more, you're not using industry knowledge enough.
2. **Every constraint gets a track.** No constraint without `track: agent` or `track: human`.
3. **Every constraint gets a ratchet_metric.** Even if it's just pass/fail (0 or 1).
4. **Under 5 minutes** for the entire spec process.
5. **Exploration hints matter.** Add 2-3 hints about what to try if the agent gets stuck.
