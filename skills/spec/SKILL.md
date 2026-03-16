---
name: spec
description: Start a new intent. Guides the user through intent convergence, generates a complete Intent Spec with delivery/UI direction, enables thorough section-by-section review, then auto-chains into environment preparation, test suite generation, pipeline validation, planning, and autonomous execution. This is the ONLY command most users need to invoke — everything after confirmation runs autonomously.
---

# Spec — Intent Formalization + Autonomous Execution Chain

## Overview

```
Step 1: Intent Convergence
  → 2-3 high-level "what" decisions
  → Domain research (if domain-specific project)
Step 2: Generate Intent Spec
  → Full spec with delivery/UI direction, constraints, agent_guidance
Step 3: Thorough Review (as long as needed)
  → Grouped section-by-section confirmation, no time limit
Step 4-7: Autonomous (human walks away)
  → Test suite → EVA validation → Plan → Execute with ratchet
```

After Step 3, the human is done until results are ready for review.

---

## Step 1: Intent Convergence

### 1.1 Load Profile
Check `~/.config/ratchet/profile.yaml`. If not exists, ask 3 quick preference questions (intervention level, quality vs speed, risk tolerance) and create it.

### 1.2 Analyze Intent
From the user's description, identify:
- Project type: `software` | `creative_writing` | `research` | `design` | `general`
- Delivery format: `web_app` | `cli` | `desktop_app` | `document` | `api` | `library`
- 2-3 decisions that would fundamentally change the spec

### 1.3 Present Choices
Ask **only intent-level decisions** — things that fork the entire spec:

```
A few decisions before I generate the Intent Spec:

1. Technical approach
   a) Pure frontend static site (simple, free hosting)
   b) Frontend + backend (data persistence, analytics)

2. Scope
   a) Start with one test type, architecture supports expansion
   b) Multi-test from the start

3. Language
   a) Chinese only
   b) Chinese + English
```

**Rules:**
- Only "what" decisions, never "how" (agent decides frameworks, patterns, tools)
- If intent is clear enough, skip to Step 2 with zero questions
- Multiple choice preferred, one message with all questions

### 1.4 Register Workspace
```
Intent ID? [auto-generated from name, user can override]
Workspace? [current dir / create new / custom path]
```
Register in `~/.config/ratchet/state.yaml` with absolute path. Status: `draft`.

### 1.5 Domain Research (if needed)

For domain-specific projects (personality tests, financial tools, medical apps, educational platforms, etc.), research the domain BEFORE generating the spec:

1. Identify what domain knowledge is needed to write good constraints (e.g., "How do professional Enneagram tests work? What scoring methods exist? What makes a good personality test question?")
2. Spawn research subagent(s) to gather this knowledge — look for established methodologies, scoring algorithms, best practices, common pitfalls
3. Use findings to inform constraint generation in Step 2

**Skip this step** only if the domain is generic (e.g., CRUD app, landing page, CLI tool) or the agent already has sufficient domain knowledge to write accurate, specific constraints.

**Why this matters:** Domain errors in the spec cascade into wrong constraints, wrong tests, and wrong implementations. No amount of ratchet iterations can fix a spec that fundamentally misunderstands the domain. 5 minutes of research here saves hours of rework.

---

## Step 2: Generate Intent Spec

### 2.1 Environment Discovery
Actively probe the environment — don't just read project files:

1. **Detect project type** from project files (package.json, go.mod, Cargo.toml, pyproject.toml, Makefile, etc.)
2. **Detect installed runtimes and tools** by running version/presence checks
3. **Reason about verification needs** from the project type — what capabilities are needed to verify this project's constraints?
4. **Search for tools** that provide those capabilities — check what's already installed, what can be installed
5. **Detect environment constraints** — headless-only (no display), CI environment, available resources

This information feeds into constraint generation (what can be auto-verified) and env-preparer (what needs to be installed).

### 2.2 Environment Negotiation (Maximum Coverage)
Identify what "running the artifact" looks like for this project. Determine what verification capabilities would unlock auto-coverage, and recommend tools that provide them:
```
Current auto coverage: 65%
With [browser testing tool]: 90% (+25% — catches broken buttons, rendering errors, navigation)
  Install: [install command]
  I can install this: yes
  Headless mode: supported (no display needed)

Without it, these become HUMAN review items:
  - Page loads correctly
  - Buttons functional
  - Navigation works
```

**Basic functionality MUST be auto-verifiable.** If capabilities are missing, make this explicit and recommend tools that provide them. Don't hardcode specific tool names — discover what's available or recommend based on the project ecosystem.

### 2.3 Generate Constraints
For every constraint:
- `check`, `test_method` (multi-level: static → unit → integration), `tools_required` (structured), `ratchet_metric`
- Assign track (agent preferred) and verifier (auto > ai_review > human)

### 2.4 Generate Delivery Direction (conditional)
**For projects with user-facing interface**, generate `delivery` section:

```yaml
delivery:
  format: web_app
  ui_direction:
    style: "Minimal, calming, mobile-first"
    key_screens:
      - name: home
        purpose: "Welcome + start quiz"
        elements: [title, description, start_button]
      - name: quiz
        purpose: "Answer questions"
        elements: [question_text, options, progress_bar, back_button]
      - name: results
        purpose: "Show personality type"
        elements: [primary_type, description, all_types_ranking, retest_button, share_button]
    user_journey: "home → quiz (45 questions) → results"
    mood: "Professional but warm, light palette with accent colors per type"
    anti_patterns: ["No gamification", "No countdown timers", "No social pressure"]
```

For CLI: `cli_direction` with interaction style and output format.
For non-UI: skip this section.

### 2.5 Generate agent_guidance
Natural language prompt for agent context, constraints, and stuck-recovery.

### 2.6 Configure Ratchet + Write spec.yaml

---

## Step 3: Thorough Review

**No time limit.** This is the highest-ROI human investment. Some sections pass in seconds, others need detailed discussion. Both are fine.

### Grouped Confirmation

**For ≤20 constraints: conversational**

Present section-by-section, wait for confirmation on each:

**Group A: Overview + Delivery**
```
📋 Prism — Online Personality Tests (v1)
What: Static web app for Enneagram personality test, Chinese, 45 questions

🖥️ Delivery:
  web_app │ SPA │ mobile-first
  Journey: home → quiz (45q) → results
  Screens: home (3 elements), quiz (4 elements), results (5 elements)
  Mood: minimal, calming, professional

This interaction model right? Any screens missing?
```

**Group B: Core Functionality (N invariants)**
```
🔒 Core (auto-verified):                        # tools are illustrative — use discovered capabilities
  INV-01  Page loads without errors          unit + browser testing
  INV-02  All 45 questions display            unit tests
  INV-03  Scoring logic correct               unit tests (+ edge cases)
  INV-04  Results page renders all 9 types    unit + browser testing
  INV-05  Retest button works                 browser testing
  INV-06  Share button works                  browser testing
  INV-07  Responsive on mobile               browser testing (viewport)

All auto-verified with multi-level tests. Missing anything?
```

**Group C: Quality (N quality_dimensions)**
```
📊 Quality:
  QD-01  Type descriptions accurate    ai_review  4/5
  QD-02  Visual design matches mood    human      3/5
  QD-03  Accessibility basics          auto (accessibility testing)

Thresholds OK?
```

**Group D: Coverage + Guidance**
```
🎯 Coverage: auto 80% │ ai_review 10% │ human 10%
🔄 Ratchet: 8 iterations per WP
⚠️ Assumed: [low-confidence items]

Approve to start autonomous execution, or adjust anything.
```

**For >20 constraints: generate HTML review page**

Generate `.ratchet/{intent-id}/spec-review.html` and open in browser:
```bash
open .ratchet/{intent-id}/spec-review.html
```

The HTML page shows:
- Grouped constraints (expandable)
- Delivery/UI direction with any mockup references
- Modification text input per section
- "Approve & Start" button → writes `.ratchet/{intent-id}/approved` marker file
- Agent detects the marker and proceeds to Step 4

### Process Feedback
- Incrementally patch spec — never regenerate
- Show what changed
- Re-confirm only the changed section

### Finalize
On approval: update status to `active`, proceed to autonomous execution.

---

## Steps 4-7: Autonomous Execution Chain

**The human is done. Everything below runs without user intervention.**

### Step 4: Environment Preparation + Test Suite (parallel)

Spawn two subagents in parallel:
- **env-preparer** (sonnet): Install tools, scaffold project, validate build
- **test-generator** (sonnet): Generate test files from test_method fields

Wait for both to complete.

### Step 5: EVA — Pipeline Validation

Main agent validates the verification pipeline works end-to-end:
1. Read env-preparer results — any blockers?
2. Read test-generator manifest — all constraints covered?
3. Run test pipeline dry-run: `[test-runner] --passWithNoTests` or equivalent
4. If any infrastructure issues: fix them here, not during execution
5. Write `.ratchet/{intent-id}/pre-validation.log`

If blockers require human action (tool that can't be auto-installed), pause and notify user.

### Step 6: Generate Plan

Main agent generates plan.yaml (needs global view of spec + tests):
- Decompose into work packages by project type
- Reference test suite files in acceptance criteria
- Include workspace path in every WP
- Set dependency graph and parallel groups
- Update status to `agent_running`

### Step 7: Execute with Ratchet Loop

Invoke the **execute** skill, which orchestrates the full ratchet loop:
- Per-WP cycle: wp-executor → verifier → keep/discard decision
- Report generation after each WP
- Git management (single branch + tagged checkpoints)
- Status updates and human notification on completion

See `skills/execute/SKILL.md` for the complete orchestration logic.

---

## Workspace Resolution

1. If intent ID provided → look up in state.yaml
2. If current directory inside registered workspace → use that intent
3. If creating new → register (Step 1.4)

---

## Rules

1. **Intent convergence is fast.** 2-3 questions max, "what" not "how".
2. **Review is thorough.** No time limit. Grouped confirmation. Discuss as long as needed.
3. **Every constraint gets test_method + tools_required.** No exceptions.
4. **Delivery direction for UI projects.** Key screens, user journey, mood — not pixels.
5. **Maximum coverage.** Basic functionality MUST be auto-verifiable.
6. **EVA: validate pipeline before execution.** Catch infrastructure issues early.
7. **Auto-chain after approval.** Human says "approve" once, then walks away.
8. **Subagents for parallelism.** env-preparer + test-generator in parallel; independent WPs in parallel.
