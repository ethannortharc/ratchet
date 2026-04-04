---
name: spec
description: "Convert confirmed story artifacts into machine-verifiable constraints, or generate spec standalone. When story exists, auto-extracts constraints from journey, scenarios, prototype, and decisions. Guides thorough section-by-section review, then auto-chains into environment preparation, test suite generation, pipeline validation, planning, and autonomous execution."
---

# Spec — Intent Formalization + Autonomous Execution Chain

## Overview

Spec is Phase 2. When story artifacts exist, it reads them and auto-extracts constraints. When invoked standalone (no story), it runs the full intent convergence flow.

```
With story:
  Read .ratchet/story/ → auto-extract constraints → quick confirmation → execute

Without story (standalone):
  Intent convergence → generate constraints → thorough review → execute
```

---

## Step 0: Detect Story Artifacts

Check for `.ratchet/story/` (flat project) or `.ratchet/phases/{phase}/story/` (multi-phase).

**If story exists** → Skip to Step 2 (auto-extraction mode). Story already handled intent convergence, domain research, and workspace registration.

**If no story** → Run full flow from Step 1.

---

## Step 1: Intent Convergence (standalone mode only)

Skip this step entirely if story artifacts exist.

### 1.1 Load Profile
Check `~/.config/ratchet/profile.yaml`. If not exists, ask 3 quick preference questions (intervention level, quality vs speed, risk tolerance) and create it.

### 1.2 Analyze Intent
From the user's description, identify:
- Project type: `software` | `creative_writing` | `research` | `design` | `general`
- Delivery format: `web_app` | `cli` | `tui` | `desktop_app` | `mobile_app` | `api` | `library` | `document` | `chatbot`
- 2-3 decisions that would fundamentally change the spec

### 1.3 Present Choices
Ask **only intent-level decisions** — things that fork the entire spec:

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

For domain-specific projects, research the domain BEFORE generating the spec:

1. Identify what domain knowledge is needed for accurate constraints
2. Spawn research subagent(s) to gather this knowledge
3. Use findings to inform constraint generation in Step 2

**Skip** if domain is generic or agent has sufficient knowledge.

---

## Step 2: Generate Intent Spec

### 2.0 Auto-Extract from Story (when story exists)

Read confirmed story artifacts and extract constraints:

```
From journey.md:
  Timing expectations ("< 2 seconds") → performance invariants
  UI elements mentioned → existence checks
  Interactions described → functional invariants
  Data flows → data integrity constraints

From scenarios.md:
  Normal scenarios → happy-path test cases
  Interruption scenarios → resilience invariants
  Boundary scenarios → edge-case test cases
  Out of scope → do NOT generate constraints for these

From prototype.html:
  Layout structure → visual consistency checks
  Element sizes/positions → UI verification criteria
  Navigation flow → interaction test cases

From decisions.md:
  User-confirmed decisions → hard constraints
  Agent-decided items → document in agent_guidance
  "human_must_decide" → must already be resolved (story phase handles this)

From mood.md:
  Style direction → quality dimensions for visual review
  Anti-patterns → negative constraints
```

Present extracted constraints to user:

```
Auto-extracted from story artifacts:

Invariants: [N] constraints
  INV-01: [from journey step 3: "progress preserved on browser close"]
  INV-02: [from scenario: "all answers = 3 → balanced result"]
  ...

Quality Dimensions: [N] dimensions
  QD-01: [from mood: visual consistency with prototype]
  ...

Anything to add, remove, or change?
```

This should be a quick confirmation — most alignment was done in story phase.

### 2.1 Environment Discovery
Actively probe the environment — don't just read project files:

1. **Detect project type** from project files (package.json, go.mod, Cargo.toml, pyproject.toml, etc.)
2. **Detect installed runtimes and tools** by running version/presence checks
3. **Reason about verification needs** from the project type
4. **Search for tools** that provide needed capabilities
5. **Detect environment constraints** — headless-only, CI environment, available resources

### 2.2 Environment Negotiation (Maximum Coverage)

**This step MUST present recommendations and WAIT for user confirmation before proceeding.**

Identify what verification capabilities would unlock auto-coverage:

```
Environment Negotiation

Current auto coverage: [N]% ([N]/[total] constraints auto-verifiable)

Recommended tools to increase coverage:

  1. [capability] → +[N]% coverage ([N] more constraints become auto)
     Install: [command]
     I can install this myself: [yes/no]

     Without it, these stay as HUMAN review:
       - [constraint]
       - [constraint]

After installing all: [N]% auto coverage (only [X] stays human)

Install recommended tools? [yes / pick specific ones / skip]
```

**Rules:**
- **MUST wait for user response** before continuing
- Show exactly which constraints move from human → agent track
- **Basic functionality MUST be auto-verifiable**

### 2.3 Generate Constraints
For every constraint:
- `check`, `test_method` (multi-level: static → unit → integration), `tools_required` (structured), `ratchet_metric`
- Assign track (agent preferred) and verifier (auto > ai_review > human)

### 2.4 Decision Classification

Classify every decision point in the spec:

```yaml
decisions:
  human_must_decide:
    - "[decisions requiring user judgment — should already be resolved from story]"

  agent_can_decide:
    - "[internal technical decisions — agent chooses freely, documents in proof]"

  unknown:
    - "[unclear items — if UX impact → escalate to human, if technical → decide and document]"
```

Rules:
- `human_must_decide`: Must be resolved before execution. If story phase didn't cover it, ask now.
- `agent_can_decide`: Agent chooses freely, documents choice in Proof of Completion.
- `unknown`: Attempt to resolve. UX impact → escalate. Technical → decide and document.

### 2.5 Generate Delivery Direction (conditional)
**For projects with user-facing interface**, generate `delivery` section with format, ui_direction, user_journey, mood, anti_patterns.

For CLI/TUI/API/library/document/chatbot: generate equivalent direction.
For non-UI projects: skip this section.

### 2.6 Generate Interface Mockup (conditional)

**For projects with user-facing interface**, generate a preview. If a story prototype exists, refine it into a more polished mockup:

| Format | Preview Method | Output |
|--------|---------------|--------|
| `web_app` / `desktop_app` / `mobile_app` | HTML mockup → open in browser | `.ratchet/{intent-id}/mockup.html` |
| `tui` | Render directly in terminal | Terminal output |
| `cli` | Show example commands + outputs | Terminal output |
| `api` | Generate OpenAPI spec → swagger-ui HTML | `.ratchet/{intent-id}/mockup-api.html` |
| `library` | Type definitions + function signatures + usage examples | Terminal output |

**Iterate until user approves.** Approved mockup becomes the visual reference for wp-executor.

**Skip** for non-UI projects.

### 2.7 Generate agent_guidance
Natural language prompt for agent context, constraints, and stuck-recovery. If a mockup was approved, reference it. If story decisions exist, reference them.

### 2.8 Configure Ratchet + Write spec.yaml

---

## Step 3: Thorough Review (HTML Review Page)

**No time limit.** This is the highest-ROI human investment.

**Always generate an HTML review page** — regardless of constraint count.

### Generate `.ratchet/{intent-id}/spec-review.html`

Generate a self-contained HTML page and open it:
```bash
open .ratchet/{intent-id}/spec-review.html
```

The HTML page includes:

**Section A: Project Overview + Delivery Direction**
- Project name, type, description
- Delivery format, user journey, key screens
- If story exists, link to story artifacts
- If a mockup was generated, embed or link to it

**Section B: Constraints (grouped, expandable)**
- Invariants with track, verifier, test_method
- Quality dimensions with rubric, threshold
- Preferences
- Each constraint shows its source (story artifact reference or standalone)
- Decision classification per constraint

**Section C: Coverage + Environment**
- Auto / ai_review / human coverage percentages
- Installed tools and capabilities
- Recommended tools (from Step 2.2 negotiation)

**Section D: Ratchet Configuration**
- Budget per WP, composite score weights
- Low-confidence assumptions flagged

**Section E: Interface Mockup Preview (if generated)**

**Interactive elements:**
- "Approve & Start" button → writes `.ratchet/{intent-id}/approved` marker file
- Per-section feedback text input
- Agent detects the marker and proceeds to Step 4

After opening:
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
3. Run test pipeline dry-run
4. If any infrastructure issues: fix them here
5. Write `.ratchet/{intent-id}/pre-validation.log`

If blockers require human action, pause and notify user.

### Step 6: Generate Plan

Main agent generates plan.yaml:
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

### Session Boundary

After spec confirmation (before execution), check if a new session is recommended:

- **Phase project**: Always suggest new session for execution
- **Long story discussion (>30 min)**: Suggest new session
- **Fresh session**: Proceed directly to execution

```
Spec is ready. All context saved to .ratchet/

[For phases]: Start a new Claude Code session for best execution quality.
[For fresh sessions]: Starting autonomous execution now.
```

---

## Spec Version Tracking

```yaml
changelog:
  - version: 1
    source: story_phase
    change: "Initial spec from confirmed story"
  - version: 2
    source: review_feedback
    change: "Added tiebreak display rule"
    story_updated: false
  - version: 3
    source: user_request
    change: "Added growth advice to results page"
    story_updated: true  # Story artifacts also changed
```

---

## Workspace Resolution

1. If intent ID provided → look up in state.yaml
2. If current directory inside registered workspace → use that intent
3. If creating new → register (Step 1.4)

---

## Rules

1. **Story first when available.** If story artifacts exist, auto-extract — don't re-ask questions.
2. **Intent convergence is fast.** 2-3 questions max, "what" not "how". (Standalone mode only.)
3. **Review is thorough.** No time limit. Grouped confirmation. Discuss as long as needed.
4. **Every constraint gets test_method + tools_required.** No exceptions.
5. **Delivery direction for UI projects.** Key screens, user journey, mood — not pixels.
6. **Maximum coverage.** Basic functionality MUST be auto-verifiable.
7. **EVA: validate pipeline before execution.** Catch infrastructure issues early.
8. **Auto-chain after approval.** Human says "approve" once, then walks away.
9. **Subagents for parallelism.** env-preparer + test-generator in parallel; independent WPs in parallel.
10. **Classify decisions.** Every decision is human_must_decide, agent_can_decide, or unknown.
11. **Track story source.** Each constraint notes which story artifact it was extracted from.
