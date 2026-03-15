---
name: spec
description: Transform intent into a structured, verifiable Intent Spec (spec.yaml) through a hybrid 3-step flow. Step 1 converges on high-level decisions, Step 2 generates the full Intent Spec, Step 3 reviews section-by-section in conversation. Use whenever the user describes something they want to build, create, write, or accomplish.
---

# Spec — Intent Formalization (Hybrid 3-Step)

## Overview

The spec flow has three distinct steps. The entire process should take under 5 minutes.

```
Step 1: Intent Convergence (~1 min)
  → 2-3 high-level "what" decisions via multiple choice
Step 2: Generate Intent Spec (~2 min)
  → Full spec.yaml using decisions + industry knowledge
Step 3: Conversation Review (~2 min)
  → Section-by-section summary, natural language feedback, incremental patch
```

---

## Step 1: Intent Convergence

The goal is to settle high-level decisions that fork the entire spec. Ask about **what**, not **how**.

### 1.1 Load Profile

Check `~/.config/ratchet/profile.yaml`. If exists, load preferences. If not, proceed with defaults and suggest `/ratchet:profile` afterward.

### 1.2 Analyze Intent

From the user's description, identify:
- Project type: `software` | `creative_writing` | `research` | `design` | `general`
- 2-3 decisions that would fundamentally change the spec

### 1.3 Present Choices

Ask **at most 3 questions**, using multiple choice when possible:

```
I'll generate an Intent Spec for this. A few decisions first:

1. Technical approach
   a) Pure frontend static site (simple, free hosting)
   b) Frontend + backend (data persistence, analytics)

2. Scope
   a) Start with one [thing], architecture supports expansion
   b) Build all three [things] from the start

3. Language
   a) Chinese only
   b) Chinese + English
```

**Rules for intent convergence:**
- Only ask about decisions that change the STRUCTURE of the spec (architecture, scope, language, platform)
- Do NOT ask about design decisions (colors, frameworks, patterns) — those go into the spec as agent-track constraints
- If the user's intent is clear enough, skip to Step 2 with zero questions
- Prefer multiple choice over open-ended
- One message, all questions at once (not one-at-a-time)

---

## Step 2: Generate Intent Spec

### 2.1 Environment Discovery

```bash
which go 2>/dev/null && go version
which node 2>/dev/null && node --version
which python3 2>/dev/null && python3 --version
which docker 2>/dev/null && docker --version
which git 2>/dev/null && git --version
```

### 2.2 Environment Negotiation (be aggressive)

Calculate what COULD be auto-verified with additional tools:

```
Current auto-verification coverage: X%
With recommended tools: Y%

Strongly recommended:
  ⬜ [tool] — unlocks N auto-verifications
     Install: [one-line command]
     I can install this myself: [yes/no]
```

### 2.3 Generate Constraints

Using the user's intent + Step 1 decisions + industry knowledge (read `references/inquiry-protocols.md`) + profile preferences:

1. Generate ALL constraints with confidence levels: ✅ high | ⚠️ medium | ❓ low
2. Assign track and verifier per constraint (prefer: auto > ai_review > human)
3. For each constraint, define:
   - `check`: the command or method to verify
   - `test_method`: detailed description of what tests should cover (scenarios, edge cases, expected behaviors). This is what the agent reads when generating the test suite.
   - `tools_required`: list of specific tools needed (e.g., `[vitest]`, `[pytest]`, `[golangci-lint]`)
   - `ratchet_metric`: quantified progress indicator

### 2.4 Configure Ratchet

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

### 2.5 Write spec.yaml

Create `.ratchet/` directory if needed. Write spec.yaml per schema in `references/spec-schema.md`.

---

## Step 3: Conversation Review

Present the Intent Spec section-by-section in conversation. Do NOT show raw YAML — show a readable summary.

### 3.1 Present Summary

```
📋 Intent Spec for "[name]" (v1)

What I'll build:
  [2-3 sentences]

🔒 Invariants (N) — all look right?
  INV-01  [claim]                    auto │ [tool]
  INV-02  [claim]                    auto │ [tool]
  ...

📊 Quality Dimensions (N) — thresholds OK?
  QD-01  [dimension]    ai_review    threshold: 4/5
  QD-02  [dimension]    human        threshold: 3/5
  ...

🎯 Verification Coverage
  auto: X% │ ai_review: Y% │ human: Z%

🔄 Ratchet: [budget] iterations per work package

⚠️ I assumed:
  1. [assumption with medium confidence]

Type feedback to adjust, or "approve" to continue to plan.
```

### 3.2 Process Feedback

When the user provides feedback:
- **Incrementally patch** the spec — do NOT regenerate from scratch
- Show what changed: "Updated INV-03 threshold from 80% to 90%"
- Re-present only the changed section
- Ask again: "Anything else, or approve?"

### 3.3 Finalize

On approval:
1. Ensure spec.yaml is written/updated
2. Register project in `~/.config/ratchet/state.yaml`
3. Record metrics in `.ratchet/metrics.yaml`
4. Suggest: "Ready for `/ratchet:plan` to decompose into work packages and generate test suite."

---

## Rules

1. **Max 3 questions in Step 1.** If you need more, you're not using industry knowledge enough.
2. **Questions are about "what", not "how".** Architecture, scope, platform — not design or implementation.
3. **Every constraint gets track + ratchet_metric + test_method.** No exceptions.
4. **Patch, don't regenerate.** In Step 3, apply feedback incrementally.
5. **Under 5 minutes** for the entire 3-step process.
6. **Exploration hints matter.** Add 2-3 hints about what to try if the agent gets stuck.
