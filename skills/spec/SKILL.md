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
  → Environment negotiation (WAIT for user confirmation on tools)
  → Constraints, delivery/UI direction, agent_guidance
  → Interface mockup (iterate until user approves)
Step 3: Thorough Review (HTML review page)
  → Browser-based review with all sections + mockup preview
  → No time limit, iterate until user clicks "Approve & Start"
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
- Delivery format: `web_app` | `cli` | `tui` | `desktop_app` | `mobile_app` | `api` | `library` | `document` | `chatbot`
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

**This step MUST present recommendations and WAIT for user confirmation before proceeding.**

Identify what "running the artifact" looks like for this project. Determine what verification capabilities would unlock auto-coverage, and present a clear before/after comparison:

```
🔧 Environment Negotiation

Current auto coverage: 65% (7/11 constraints auto-verifiable)

Recommended tools to increase coverage:

  1. [browser testing capability] → +25% coverage (3 more constraints become auto)
     Install: [install command]
     I can install this myself: ✅ yes
     Headless mode: supported

     Without it, these stay as HUMAN review:
       - Page loads correctly
       - Buttons functional
       - Navigation works

  2. [accessibility testing capability] → +5% coverage (1 more constraint)
     Install: [install command]
     I can install this myself: ✅ yes

After installing all: 95% auto coverage (only visual design stays human)

Install recommended tools? [yes / pick specific ones / skip]
```

**Rules:**
- **MUST wait for user response** before continuing to Step 2.3
- For `agent_can_install: true` tools, offer to install immediately upon user approval
- For `agent_can_install: false` tools, ask user to install and wait for confirmation
- Show exactly which constraints move from human → agent track with each tool
- **Basic functionality MUST be auto-verifiable.** If capabilities are missing, make this explicit
- Don't hardcode specific tool names — discover what's available or recommend based on the project ecosystem

### 2.3 Generate Constraints
For every constraint:
- `check`, `test_method` (multi-level: static → unit → integration), `tools_required` (structured), `ratchet_metric`
- Assign track (agent preferred) and verifier (auto > ai_review > human)

### 2.4 Generate Delivery Direction (conditional)
**For projects with user-facing interface**, generate `delivery` section:

```yaml
delivery:
  format: web_app  # web_app | cli | tui | desktop_app | mobile_app | api | library | document | chatbot
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

For CLI/TUI/API/library/document/chatbot: generate equivalent direction for that format.
For non-UI projects: skip this section.

### 2.5 Generate Interface Mockup (conditional)

**For projects with user-facing interface**, generate a preview so the user can see and negotiate the look before execution begins. Choose preview method based on `delivery.format`:

| Format | Preview Method | Output |
|--------|---------------|--------|
| `web_app` / `desktop_app` / `mobile_app` | HTML mockup → open in browser | `.ratchet/{intent-id}/mockup.html` |
| `tui` | Render directly in terminal with ANSI colors/box drawing | Terminal output |
| `cli` | Show example commands + outputs in terminal | Terminal output |
| `api` | Generate OpenAPI spec → swagger-ui HTML → open in browser | `.ratchet/{intent-id}/mockup-api.html` |
| `library` | Show type definitions + function signatures + usage examples | Terminal output |
| `document` | Show structure outline + sample content | Terminal output |
| `chatbot` | Show example conversation flows | Terminal output |

**For browser-based previews (HTML mockups):**
- Generate a self-contained HTML file with inline CSS showing key screens
- Include actual colors, typography, layout, spacing — not wireframes
- For mobile apps, use mobile viewport meta tag
- Open with `open .ratchet/{intent-id}/mockup.html`

**Iterate until user approves:**
1. Show the preview
2. User gives feedback ("too dark", "buttons too small", "want left sidebar not top nav")
3. Agent updates the mockup
4. Repeat until user says it looks right
5. Approved mockup becomes the visual reference for wp-executor

**Skip this step** for non-UI projects (pure libraries, data processing, etc.).

### 2.6 Generate agent_guidance
Natural language prompt for agent context, constraints, and stuck-recovery. If a mockup was approved, reference it as the visual spec for the executor.

### 2.7 Configure Ratchet + Write spec.yaml

---

## Step 3: Thorough Review (HTML Review Page)

**No time limit.** This is the highest-ROI human investment.

**Always generate an HTML review page** — regardless of constraint count. A browser-based review is always easier to navigate than terminal conversation.

### Generate `.ratchet/{intent-id}/spec-review.html`

Generate a self-contained HTML page and open it:
```bash
open .ratchet/{intent-id}/spec-review.html
```

The HTML page includes:

**Section A: Project Overview + Delivery Direction**
- Project name, type, description
- Delivery format, user journey, key screens
- If a mockup was generated (Step 2.5), embed or link to it

**Section B: Constraints (grouped, expandable)**
- Invariants with track, verifier, test_method
- Quality dimensions with rubric, threshold
- Preferences
- Each constraint shows its verification capability requirement

**Section C: Coverage + Environment**
- Auto / ai_review / human coverage percentages
- Installed tools and capabilities
- Recommended tools (from Step 2.2 negotiation)

**Section D: Ratchet Configuration**
- Budget per WP, composite score weights
- Low-confidence assumptions flagged

**Section E: Interface Mockup Preview (if generated)**
- Embedded preview or iframe for HTML mockups
- For terminal-based previews (TUI/CLI), show screenshots or description

**Interactive elements:**
- "Approve & Start" button → writes `.ratchet/{intent-id}/approved` marker file
- Per-section feedback text input
- Agent detects the marker and proceeds to Step 4

After opening the HTML page, tell the user:
```
Spec review page opened in browser. Review each section and either:
- Click "Approve & Start" to begin autonomous execution
- Or tell me what to change — I'll update the spec and regenerate the review page
```

### Process Feedback
- Incrementally patch spec — never regenerate from scratch
- Show what changed
- Regenerate the HTML review page with updates highlighted
- Wait for user to approve again

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
