---
name: spec
description: Transform intent into a structured, verifiable Intent Spec (spec.yaml) through a hybrid 3-step flow, then auto-generate the test suite. Use whenever the user describes something they want to build, create, write, or accomplish. Supports workspace registration and intent ID for multi-project management.
---

# Spec — Intent Formalization (Hybrid 3-Step) + Test Suite

## Overview

The spec flow has three steps plus automatic test suite generation. The entire process should take under 5 minutes.

```
Step 1: Intent Convergence (~1 min)
  → 2-3 high-level "what" decisions via multiple choice
Step 2: Generate Intent Spec (~2 min)
  → Full spec.yaml using decisions + industry knowledge
Step 3: Conversation Review (~2 min)
  → Section-by-section summary, natural language feedback, incremental patch
Step 4: Auto-generate Test Suite (automatic)
  → Concrete test files from each constraint's test_method
```

---

## Step 1: Intent Convergence

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
- Do NOT ask about design decisions (colors, frameworks, patterns) — those go into agent_guidance
- If the user's intent is clear enough, skip to Step 2 with zero questions
- Prefer multiple choice over open-ended
- One message, all questions at once (not one-at-a-time)

### 1.4 Register Workspace

After intent convergence (or immediately if no questions needed):

```
Intent ID? [auto-generated from project name, user can override]
Workspace location?
  [1] Current directory: /Users/coder/projects/prism
  [2] Create new: ~/projects/[intent-id]
  [3] Custom path
```

Register in `~/.config/ratchet/state.yaml` with absolute path. All subsequent operations for this intent are locked to this workspace.

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

### 2.2 Environment Negotiation (Maximum Coverage Principle)

The agent's goal is to **maximize automated verification coverage** — leave as little as possible to human review. This applies to ALL project types.

**Step A: Identify what "running the artifact" looks like for this project:**

| Project produces | How to verify it actually works | Tool needed |
|-----------------|-------------------------------|-------------|
| Web app/site | Start dev server + browser tests | Playwright |
| CLI tool | Run with test inputs, check output | shell (built-in) |
| API service | Start server + call endpoints | curl (built-in) |
| Library/package | Run example code, import tests | project runtime |
| Document/report | Validate structure, format, length | shell + LLM |
| Creative writing | Check consistency, format, word count | LLM |

**Step B: Calculate coverage with and without additional tools:**

```
Current auto-verification coverage: X%
With recommended tools: Y%

Strongly recommended:
  ⬜ [tool] — unlocks N auto-verifications
     What it enables: [e.g. "end-to-end browser tests — catches rendering errors, broken buttons, navigation issues"]
     Install: [one-line command]
     I can install this myself: [yes/no]

Without these tools, the following constraints will require HUMAN verification
instead of automated testing:
  - [constraint that could be auto but lacks tooling]
```

**Step C: Be aggressive.** If a tool can be installed by the agent, offer to install it immediately. The goal is to push `human` track items toward `auto` track wherever possible. Every constraint left on human track is a potential delay.

**Key rule: "Basic functionality" must ALWAYS be auto-verifiable.** For any project that produces a runnable artifact, the spec MUST include invariants that verify the artifact actually runs and basic interactions work. These are NOT optional — they are industry-standard baseline tests that catch encoding errors, broken buttons, navigation failures, etc.

### 2.3 Generate Constraints

Using the user's intent + Step 1 decisions + industry knowledge (read `references/inquiry-protocols.md`) + profile preferences:

1. Generate ALL constraints with confidence levels: ✅ high | ⚠️ medium | ❓ low
2. Assign track and verifier per constraint (prefer: auto > ai_review > human)
3. For each constraint, define:
   - `check`: the command or method to verify
   - `test_method`: detailed description of what tests should cover (scenarios, edge cases, expected behaviors). This is what the agent reads when generating the test suite.
   - `tools_required`: structured list with id, install hint, and agent_can_install flag
   - `ratchet_metric`: quantified progress indicator

**Multi-level test_method (mandatory for software projects, encouraged for all):**

Every constraint's `test_method` should include the highest verification level achievable:

```
Level 1 — Static: build, lint, type-check (catches syntax/type errors)
Level 2 — Unit: isolated function tests (catches logic errors)
Level 3 — Integration: actually run the artifact and verify behavior (catches rendering, interaction, wiring errors)
```

Example for a web project constraint "results page displays correctly":
```yaml
test_method: |
  Level 1: TypeScript compiles without errors
  Level 2: Unit test — scoring function returns correct type for known inputs
  Level 3: Integration — start dev server, navigate to results page after completing quiz,
           verify: page renders without errors, all 9 type descriptions visible,
           primary type highlighted, retest button clickable, share button functional
```

**The agent MUST auto-generate Level 3 tests when the environment supports it.** Basic functionality issues (broken buttons, encoding errors, pages not rendering) should NEVER reach human review — they are auto-verifiable with the right tools.

### 2.4 Generate agent_guidance

Create the `agent_guidance` section — a natural language prompt giving the agent project context, key constraints, and direction when stuck:

```yaml
agent_guidance: |
  You are working on intent "[name]".
  [What the project is in 1-2 sentences]

  [Key constraints and direction]

  When stuck on [X], try [Y].

  Do NOT:
  - [Anti-patterns specific to this project]
```

### 2.5 Configure Ratchet

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

### 2.6 Write spec.yaml

Create `.ratchet/` directory in the registered workspace if needed. Write spec.yaml per schema in `references/spec-schema.md`.

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

Type feedback to adjust, or "approve" to continue.
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
2. Update intent status to `active` in `~/.config/ratchet/state.yaml`
3. Record metrics in `.ratchet/metrics.yaml`
4. Proceed to Step 4 (test suite generation)

---

## Step 4: Auto-generate Test Suite

After spec confirmation, automatically generate concrete test files from each constraint's `test_method`. This happens without user intervention.

### 4.1 Create test-suite directory

```bash
mkdir -p .ratchet/test-suite
```

### 4.2 Generate test files

For each constraint:

**`verifier: auto`** → Generate executable test file:
- Read `test_method` for scenarios and edge cases
- Use `tools_required` to determine test framework (vitest, pytest, go test, etc.)
- Generate runnable but FAILING tests (TDD red phase)
- File: `.ratchet/test-suite/INV-01.test.{ts,py,go,...}`

**`verifier: ai_review`** → Generate structured review prompt:
- Include rubric, threshold, what to evaluate
- File: `.ratchet/test-suite/QD-01.review.md`

**`verifier: human`** → Generate review checklist:
- Clear criteria, where to find artifacts, pass/fail guidance
- File: `.ratchet/test-suite/QD-02.checklist.md`

### 4.3 Write manifest

Create `.ratchet/test-suite/manifest.yaml`:
```yaml
generated: [datetime]
spec_version: 1
project_type: [type]
test_runner: [vitest | pytest | go test | ...]
entries:
  - constraint_id: INV-01
    type: auto
    file: INV-01.test.ts
    status: generated
  - constraint_id: QD-01
    type: ai_review
    file: QD-01.review.md
    status: generated
```

### 4.4 Report and continue

```
✅ Test suite generated: [N] test files
   auto: [N] executable tests
   ai_review: [N] review prompts
   human: [N] checklists

Ready for /ratchet:plan to decompose into work packages.
```

---

## Workspace Resolution

When this skill is invoked:
1. If intent ID provided as argument → look up workspace in state.yaml
2. If current directory is inside a registered workspace → use that intent
3. If creating new → register workspace (Step 1.4)

**Agent execution constraint:** All file operations must stay within the registered workspace directory.

---

## Rules

1. **Max 3 questions in Step 1.** If you need more, you're not using industry knowledge enough.
2. **Questions are about "what", not "how".** Architecture, scope, platform — not design or implementation.
3. **Every constraint gets track + ratchet_metric + test_method + tools_required.** No exceptions.
4. **Patch, don't regenerate.** In Step 3, apply feedback incrementally.
5. **Under 5 minutes** for the entire process (Steps 1-3). Step 4 runs automatically.
6. **agent_guidance replaces exploration_hints.** Write a natural language prompt, not a flat list.
7. **Register workspace.** Every intent gets a locked absolute path.
8. **Maximum coverage.** Aggressively request tools to maximize auto-verification. Basic functionality (runs, renders, navigates, buttons work) MUST be auto-verifiable. If a tool is missing, tell the user what it unlocks and offer to install it.
9. **Multi-level test_method.** For every constraint, push to the highest verification level the environment supports (static → unit → integration).
