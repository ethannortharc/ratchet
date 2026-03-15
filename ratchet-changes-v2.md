# Ratchet Plugin — Change Specification v2

This document captures all design changes discussed since the initial v0.1.0 release. Hand this to Claude Code for review and implementation.

Read the existing DESIGN.md first for full context, then apply these changes.

---

## Overview of Changes

1. Spec flow redesigned to Hybrid three-step
2. Spec renamed to "Intent Spec" throughout
3. Each constraint gets detailed test_method and tools_required
4. Test suite generation inserted between spec and plan
5. Workspace management via global registry with absolute paths
6. Intent lifecycle state machine
7. Proof of Work in reports
8. Symphony-inspired architectural improvements

---

## Change 1: Hybrid Spec Flow

### Current behavior
`/ratchet:spec` generates a complete spec in one shot, user reviews in terminal.

### New behavior
Three steps within a single conversational flow (user does NOT leave Claude Code):

**Step 1 — Intent Convergence (2-3 questions max)**

Before generating anything, identify and ask ONLY the decisions that cascade into everything else. These are intent-level choices, NOT design choices.

Examples of intent-level (ask these):
- "Pure frontend static site or has backend?"
- "Chinese only or bilingual?"
- "MVP one test type or multi-test from start?"

Examples of design-level (do NOT ask, agent decides):
- "React or Vue?"
- "SQLite or PostgreSQL?"
- "Vitest or Jest?"

Implementation: In the spec skill, before generating the spec draft, analyze the user's intent description and identify 2-3 branching decisions where different answers would produce fundamentally different specs. Present these as quick choices. Previous answers may influence subsequent questions.

**Step 2 — Generate complete Intent Spec**

Based on intent convergence answers + industry knowledge + profile, generate the full spec. Include all three tiers (invariants, quality_dimensions, preferences) with detailed test_method and tools_required per constraint.

**Step 3 — Conversational review and micro-adjustments**

Present a readable summary (NOT raw YAML). User stays in the conversation and says things like "change X to Y" or "add Z" or "looks good". Agent modifies spec.yaml directly. No need for `/ratchet:update` at this stage — that command is for mid-execution updates only.

### Files to modify
- `skills/spec/SKILL.md` — rewrite workflow to implement three-step hybrid

---

## Change 2: Rename to "Intent Spec"

### What
Replace all references to "spec" (as a concept) with "Intent Spec" in user-facing text. The command stays `/ratchet:spec` (short is fine for commands), but descriptions and documentation should say "Intent Spec".

### Why
It's not a requirements document. It contains intent, constraints, quality standards, and verification methods — broader than "requirements" or "specification".

### Files to modify
- All SKILL.md files — update terminology in descriptions
- DESIGN.md — update terminology
- README.md — update terminology

---

## Change 3: Detailed test_method and tools_required per constraint

### Current schema
```yaml
invariants:
  - id: INV-01
    claim: "All tests pass"
    verifier: auto
    check: "go test ./..."
```

### New schema
```yaml
invariants:
  - id: INV-01
    claim: "All tests pass"
    track: agent
    verifier: auto
    check: "go test ./..."
    test_method: |
      Unit tests covering:
      - Happy path for each public function
      - Error cases for invalid inputs
      - Edge cases for boundary values
    tools_required:
      - id: go-test
        install: "built-in with Go"
        agent_can_install: false
    ratchet_metric: "passed_tests / total_tests"

quality_dimensions:
  - id: QD-01
    dimension: "Type description quality"
    track: agent
    verifier: ai_review
    test_method: |
      AI reviewer evaluates each type description for:
      - Accuracy of core motivation and fear
      - Presence of concrete behavioral examples (not vague)
      - Length between 200-500 characters
    tools_required: []  # Only needs LLM
    rubric: |
      5: Accurate, specific, resonant
      3: Basically accurate but vague
      1: Factual errors or no resonance
    threshold: 4
    ratchet_metric: "rubric_score"
```

### Key points
- `test_method` describes HOW to verify in enough detail for agent to generate actual test cases
- `tools_required` lists what's needed with install hints
- User sees a clean summary; agent sees the full detail
- This drives both test suite generation (Change 4) and environment negotiation

### Files to modify
- `references/spec-schema.md` — update schema
- `skills/spec/SKILL.md` — generate test_method for each constraint
- `templates/spec-template.yaml` — update template

---

## Change 4: Test Suite Generation between Spec and Plan

### Current flow
```
/ratchet:spec → /ratchet:plan → execute
```

### New flow
```
/ratchet:spec → (auto) generate test suite → /ratchet:plan → execute with ratchet
```

### How it works
After spec is confirmed, automatically generate concrete test cases from each constraint's `test_method`. Store in `.ratchet/test-suite/`:

```
.ratchet/test-suite/
├── INV-01.test.md    # or .py, .ts, .go depending on project type
├── INV-02.test.md
├── QD-01.review.md   # Review prompts for ai_review constraints
└── manifest.yaml     # Maps constraint IDs to test files
```

For `auto` verifiers: generate executable test files (unit tests, scripts).
For `ai_review` verifiers: generate structured review prompts with rubric.
For `human` verifiers: generate review checklists.

This happens automatically after spec confirmation — user doesn't need to invoke a separate command. The plan skill then references these test files when defining work package acceptance criteria.

### Why before plan
- Makes spec constraints concrete (you discover gaps when writing actual tests)
- Ratchet loop can use real tests from iteration 1
- Plan can reference specific test files in WP acceptance criteria

### Files to modify
- `skills/spec/SKILL.md` — add Step 5: auto-generate test suite after confirmation
- `skills/plan/SKILL.md` — reference test suite files in WP acceptance criteria
- `skills/verify/SKILL.md` — use test suite files for verification
- `references/spec-schema.md` — document test suite structure

---

## Change 5: Workspace Management

### Problem
Current design relies on current working directory to determine project context. Agent can `cd ..` and break isolation. Multiple intents have no clear boundary.

### Solution: Global Intent Registry with Absolute Paths

**~/.config/ratchet/state.yaml** becomes the central registry:

```yaml
intents:
  - id: prism                                    # Unique identifier
    name: "Prism — Online Personality Tests"
    workspace: /Users/coder/projects/prism       # Absolute path, locked at creation
    type: software
    status: active                               # See Change 6 for lifecycle
    spec_version: 1
    created: 2026-03-14T22:00:00
    last_activity: 2026-03-15T08:30:00

  - id: note-cli
    name: "Note CLI"
    workspace: /Users/coder/projects/note-cli
    type: software
    status: draft
    spec_version: 1
    created: 2026-03-15T10:00:00
    last_activity: 2026-03-15T10:00:00
```

**All Ratchet commands accept an optional intent ID:**
```
/ratchet:status              → show all intents
/ratchet:status prism        → show prism details
/ratchet:verify prism        → verify prism
/ratchet:review              → show review queue across all intents
```

**When intent ID is omitted, resolution order:**
1. If current directory is inside a registered workspace → use that intent
2. If multiple intents exist → ask user to choose
3. If no intents exist → suggest `/ratchet:spec`

**Spec creation registers the workspace:**
```
/ratchet:spec "online personality test website"

→ Intent ID? prism
→ Workspace location?
  [1] Current directory: /Users/coder/projects/prism
  [2] Create new: ~/projects/prism
  [3] Custom path
→ Registered. All operations for "prism" locked to this path.
```

**Agent execution includes workspace constraint:**
When executing work packages, the agent's context includes:
```
You are executing intent "prism", work package wp-03.
Workspace: /Users/coder/projects/prism
ALL file operations must stay within this directory.
Do not cd outside this directory.
```

### Files to modify
- `skills/getting-started/SKILL.md` — document workspace concept
- `skills/spec/SKILL.md` — add workspace registration on intent creation
- `skills/status/SKILL.md` — read from global state, support intent ID parameter
- `skills/verify/SKILL.md` — resolve workspace by intent ID
- `skills/review/SKILL.md` — show intent ID for each review item
- `skills/plan/SKILL.md` — include workspace path in each WP
- `skills/report/SKILL.md` — include workspace path in reports
- `skills/metrics/SKILL.md` — aggregate by intent ID
- `DESIGN.md` — document workspace management architecture

---

## Change 6: Intent Lifecycle State Machine

### States
```
draft → active → agent_running → agent_complete → human_review → done
                      ↑                │
                      └── ratchet ──────┘
                      
Additional transitions:
  any → paused (user pauses)
  paused → active (user resumes)
  any → archived (user archives)
```

### State definitions

| State | Meaning |
|-------|---------|
| `draft` | Spec exists but not yet confirmed |
| `active` | Spec confirmed, plan exists or being created |
| `agent_running` | Agent is executing work packages with ratchet loop |
| `agent_complete` | All agent-track constraints pass, human items queued |
| `human_review` | Waiting for human to process review queue |
| `done` | All constraints (agent + human) verified, project complete |
| `paused` | User paused execution |
| `archived` | User archived (hidden from active views) |

### State transitions triggered by
- `draft → active`: User confirms spec
- `active → agent_running`: Plan created, execution starts
- `agent_running → agent_complete`: All agent-track pass (or budget exhausted)
- `agent_complete → human_review`: Human items queued
- `human_review → agent_running`: Human feedback triggers spec update + new round
- `human_review → done`: All human reviews pass
- Any → `paused`: User runs `/ratchet:pause {intent-id}`
- `paused → active`: User runs `/ratchet:resume {intent-id}`

### Files to modify
- `skills/getting-started/SKILL.md` — document lifecycle
- `skills/status/SKILL.md` — display state with visual indicator
- `DESIGN.md` — add state machine diagram and transition rules
- `references/spec-schema.md` — document status field values

---

## Change 7: Proof of Work in Reports

### Current behavior
Reports are text summaries with tables.

### New behavior
Reports include concrete evidence — not just "4/6 passed" but the actual verification outputs.

**Iteration report additions:**
```markdown
## Proof of Work

### Auto Verifications
- INV-01 (builds): ✅ `npm run build` exit code 0
  ```
  Build output: 47 modules, 0 errors, 0 warnings
  Bundle size: 142KB gzipped
  ```
- INV-03 (scoring): ✅ 12/12 test cases passed
  ```
  Test output: PASS src/scoring.test.ts (0.8s)
    ✓ type 1 full score → primary type 1
    ✓ tie between type 2 and 3 → alphabetical tiebreak
    ...
  ```
- QD-01 (description quality): ai_review score 4.2/5
  ```
  Reviewer notes: Type 1 description is accurate and specific.
  Type 5 description could use more behavioral examples.
  ```

### Human Review Items (pending)
- QD-02 (visual design): screenshot at .ratchet/artifacts/screenshots/results-page.png
- INV-07 (usability): test instructions at .ratchet/artifacts/test-script.md
```

**Project report additions:**
- Optimization trajectory chart (ASCII or link to generated image)
- Complete diff summary (what changed from v1 to final)
- Total token consumption
- All spec versions with changelogs

### Files to modify
- `skills/report/SKILL.md` — add proof of work section to both report types
- `skills/verify/SKILL.md` — capture raw verification output for proof of work

---

## Change 8: Minor improvements inspired by Symphony

### 8a: WORKFLOW.md-style unified config

Consider merging spec.yaml's exploration_hints and agent behavior guidance into a single section that serves as the "agent prompt" for this intent. This keeps policy and constraints in one place.

```yaml
# In spec.yaml, add:
agent_guidance: |
  You are working on intent "prism".
  This is a static frontend website for personality tests.
  
  When stuck on scoring logic, refer to established enneagram research.
  When stuck on visual design, use the prism/light-refraction metaphor.
  Prioritize mobile experience over desktop.
  
  Do NOT:
  - Add a backend or database
  - Use external analytics
  - Require user registration
```

This replaces the separate `exploration_hints` list with a richer, more natural prompt.

### 8b: Intent as ticket

Each intent in state.yaml should have enough metadata to function as a lightweight ticket:

```yaml
intents:
  - id: prism
    name: "Prism — Online Personality Tests"
    workspace: /Users/coder/projects/prism
    type: software
    status: agent_running
    spec_version: 2
    created: 2026-03-14T22:00:00
    last_activity: 2026-03-15T08:30:00
    # Ticket-like fields:
    priority: normal           # low | normal | high | urgent
    tags: [frontend, chinese, mvp]
    brief: "Static site for personality tests, starting with Enneagram"
    current_blocker: null      # or "human review needed for QD-02"
```

This enables `/ratchet:status` to function as a simple project board without needing an external issue tracker.

### Files to modify
- `references/spec-schema.md` — add agent_guidance field, update state.yaml schema
- `skills/spec/SKILL.md` — generate agent_guidance section
- `skills/status/SKILL.md` — display ticket-like fields, show blockers
- `DESIGN.md` — document these additions

---

## Implementation Priority

Suggested order (each builds on the previous):

1. **Workspace management (Change 5)** — Foundation. Everything else depends on proper intent registration and workspace isolation.

2. **Intent lifecycle (Change 6)** — Needed for status display and execution flow.

3. **Hybrid spec flow (Change 1)** — The most user-facing improvement. Makes the first interaction much better.

4. **Rename to Intent Spec (Change 2)** — Simple find-and-replace, do alongside Change 1.

5. **Detailed test_method (Change 3)** — Enriches the spec content.

6. **Test suite generation (Change 4)** — Depends on Change 3.

7. **Proof of Work (Change 7)** — Enhances reports, depends on verify capturing raw outputs.

8. **Symphony-inspired improvements (Change 8)** — Polish and enrichment.

---

## Testing the Changes

After implementation, test with the existing Prism project:

1. Run `/ratchet:spec "online personality test website called Prism"` — verify hybrid three-step flow works
2. Check `~/.config/ratchet/state.yaml` — verify workspace registered with absolute path
3. Check `.ratchet/test-suite/` — verify test cases generated from spec
4. Run `/ratchet:plan` — verify plan references test suite files
5. Run `/ratchet:status` — verify lifecycle state displayed correctly
6. Run `/ratchet:status` from a DIFFERENT directory — verify it still works (workspace resolution by registry, not pwd)
7. Execute a work package — verify agent stays within workspace
8. Run `/ratchet:verify` — verify proof of work captured in report
9. Run `/ratchet:review` — verify items show intent ID and workspace

---

## Files Summary

### New files to create
- `~/.config/ratchet/state.yaml` — created on first intent registration (by spec skill)

### Files to modify
| File | Changes |
|------|---------|
| `DESIGN.md` | Workspace management, lifecycle states, Intent Spec terminology, proof of work, agent_guidance |
| `README.md` | Intent Spec terminology, updated flow description |
| `references/spec-schema.md` | test_method, tools_required, agent_guidance, state.yaml schema, test-suite structure |
| `skills/getting-started/SKILL.md` | Workspace concept, lifecycle states, updated terminology |
| `skills/spec/SKILL.md` | Hybrid three-step, workspace registration, test suite generation, agent_guidance |
| `skills/plan/SKILL.md` | Reference test suite, include workspace in WPs |
| `skills/verify/SKILL.md` | Capture raw output for proof of work, workspace-aware |
| `skills/review/SKILL.md` | Show intent ID per item, workspace-aware |
| `skills/status/SKILL.md` | Multi-intent dashboard, lifecycle display, ticket fields, workspace resolution |
| `skills/report/SKILL.md` | Proof of work sections |
| `skills/metrics/SKILL.md` | Aggregate by intent ID |
| `skills/update/SKILL.md` | Workspace-aware, intent ID parameter |
| `skills/profile/SKILL.md` | No changes needed |
| `templates/spec-template.yaml` | Add test_method, tools_required, agent_guidance |
