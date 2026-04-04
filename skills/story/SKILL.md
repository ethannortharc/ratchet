---
name: story
description: "Phase 1: Multi-perspective alignment through role-based story generation. Spawns parallel perspective agents (end-user, developer, DevOps, security, QA), synthesizes via PM agent, confirms with user showing all perspectives, then Manager agent sequences into specs. Auto-transitions to spec phase on confirmation."
---

# Story — Multi-Perspective Alignment (Phase 1)

## Overview

Story is Phase 1 — before spec, before code, before constraints. It answers "what are we building, for whom, and from whose perspective?" through role-based analysis and PM synthesis.

```
User: /ratchet:story "Build a REST API for task management"

Agent: selects relevant stakeholder roles for this project
Agent: spawns parallel perspective agents (end-user, developer, DevOps, QA, security)
Agent: each perspective agent produces requirements from their angle
Agent: PM agent synthesizes all perspectives, resolves conflicts
Agent: presents unified view with all perspectives visible
User:  reviews, gives feedback, confirms
Agent: Manager agent sequences confirmed requirements into specs/phases

=== Story phase complete → auto-transition to Spec ===
```

The spec phase then reads the PM synthesis and auto-extracts machine-verifiable constraints. Most of the hard alignment work happens here in story, not in spec.

---

## When to Use

- **New intent**: Always start with `/ratchet:story` for any non-trivial project
- **Standalone spec**: `/ratchet:spec` still works directly for simple projects or when the user already has a clear spec in mind
- **Updates**: User describes changes to an existing project → agent routes here for story-level updates, then cascades to spec

## Artifacts

Story phase produces artifacts in `.ratchet/story/` (flat project) or `.ratchet/phases/{phase-id}/story/` (multi-phase):

| Artifact | File | Purpose |
|----------|------|---------|
| Perspectives | `perspectives/*.md` | Per-role requirements, concerns, scenarios |
| PM Synthesis | `synthesis.md` | Unified requirements, conflict resolutions, prioritized scope |
| Personas | `personas.md` | Behavioral personas enhanced with role-tagged needs |
| Journey | `journey.md` | Narrative walkthrough with cross-cutting annotations |
| Scenarios | `scenarios.md` | Comprehensive scenario table with source-role column |
| Mood + Prototype | `mood.md` + `prototype.html` | Visual direction and clickable skeleton |
| Decisions | `decisions.md` | Every decision made, classified and tracked |
| Plan Overview | `plan-overview.md` | Manager's spec sequencing and milestone mapping |
| Active Roles | `roles.yaml` | Which roles participated in this project |

---

## Step 1: Analyze Intent

### 1.1 Load Profile
Check `~/.config/ratchet/profile.yaml`. If missing, ask 3 quick preference questions and create it.

### 1.2 Domain Research
For domain-specific projects (personality tests, financial tools, medical apps, educational platforms), research the domain BEFORE generating story artifacts:

1. Identify what domain knowledge shapes the user experience (scoring methods, best practices, common pitfalls)
2. Spawn research subagent(s) to gather this knowledge
3. Use findings to inform perspective agents

**Skip** if the domain is generic (CRUD app, landing page, CLI tool) or agent has sufficient knowledge.

### 1.3 Register Intent
If this is a new intent (not an update):

```
Intent ID? [auto-generated from name, user can override]
Workspace? [current dir / create new / custom path]
```

Register in `~/.config/ratchet/state.yaml` with status: `draft`.

---

## Step 2: Role Selection

### 2.1 Load Role Registry

Read `references/role-registry.yaml` for domain role definitions. Check for project-level overrides in `.ratchet/roles.yaml`.

### 2.2 Evaluate Conditional Roles

For each role with `priority: conditional`, evaluate whether the project involves that role's concern area:

```
For each conditional role:
  Read the role's condition field
  Evaluate against the user's intent description and project type
  Include if relevant, exclude if not
```

### 2.3 Present Role Selection to User

```
For this project, I'll gather perspectives from:

  ✓ End User (required) — user flows, usability, accessibility
  ✓ Developer (required) — API design, maintainability, DX
  ✓ DevOps / SRE (included — project deploys to Vercel) — deployment, monitoring
  ✓ Security (included — handles user auth) — auth, data protection
  ✓ QA / Tester (required) — testability, edge cases, scenarios
  ✓ PM (required) — synthesis and prioritization
  ✓ Manager (required) — spec sequencing and planning

  Skipped:
  ✗ (none for this project)

Add or remove any roles? You can also define custom roles.
```

### 2.4 Handle Custom Roles

If user adds custom roles:
- Create entry with name, description, contributes, participates_in
- Save to `.ratchet/roles.yaml` for this project

### 2.5 Save Active Roles

Write `.ratchet/story/roles.yaml`:

```yaml
domain: software_development
active_roles:
  - id: end_user
    name: "End User"
    status: active
  - id: developer
    name: "Developer"
    status: active
  - id: devops
    name: "DevOps / SRE"
    status: active
    reason: "project deploys to Vercel"
  - id: security
    name: "Security"
    status: active
    reason: "handles user auth"
  - id: qa_tester
    name: "QA / Tester"
    status: active
  - id: pm
    name: "Product Manager"
    status: active
  - id: manager
    name: "Engineering Manager"
    status: active
excluded_roles:
  # - id: devops
  #   reason: "pure frontend, no deployment"
custom_roles: []
```

---

## Step 3: Parallel Perspective Gathering

### 3.1 Spawn Perspective Agents

For each active role (except PM and Manager — they come later), spawn a parallel subagent:

```
Agent(
  subagent_type: "general-purpose",
  model: [role's model from registry — typically sonnet],
  prompt: """
    You are the {role_name} perspective agent for a software project.
    
    Project intent: {user_intent_description}
    Domain context: {domain_research_findings if any}
    User profile: {profile preferences}
    
    Your job: analyze this project EXCLUSIVELY from the {role_name} perspective.
    Produce requirements, concerns, scenarios, and constraints that a 
    {role_description} would identify.
    
    Focus on what matters to YOUR perspective. Don't try to cover
    everything — other role agents handle other perspectives.
    
    Output format:
    
    # {role_name} Perspective
    
    ## Context
    What this role cares about for this project.
    
    ## Requirements
    - REQ-1: [requirement] — [rationale]
    - REQ-2: [requirement] — [rationale]
    (list all requirements from this perspective)
    
    ## Concerns
    - CONCERN-1: [what could go wrong from this perspective]
    - CONCERN-2: [risk or gap]
    
    ## Scenarios (from this perspective)
    - SCENARIO-1: [happy path from this role's view]
    - SCENARIO-2: [failure mode this role worries about]
    - SCENARIO-3: [edge case this role would flag]
    
    ## Constraints
    - CONSTRAINT-1: [hard requirement from this perspective]
    
    ## Out of Scope (from this perspective)
    - [what this role considers unnecessary for MVP]
  """,
  run_in_background: true  # All role agents run in parallel
)
```

### 3.2 Collect Perspective Documents

As each perspective agent completes, save its output to `.ratchet/story/perspectives/{role-id}.md`.

Wait for ALL perspective agents to complete before proceeding to PM synthesis.

---

## Step 4: PM Synthesis

### 4.1 Spawn PM Agent

Spawn the PM synthesis agent (on Opus for deeper analysis):

```
Agent(
  subagent_type: "general-purpose",
  model: opus,
  prompt: """
    You are the Product Manager synthesis agent.
    
    Project intent: {user_intent_description}
    Domain context: {domain_research_findings}
    
    You have received perspective documents from these roles:
    {list each role and path to their perspective document}
    
    Read ALL perspective documents carefully. Your job:
    
    1. UNIFIED REQUIREMENTS TABLE
       Merge all requirements across perspectives. For each requirement:
       - Assign an ID (R-01, R-02, ...)
       - Note which role(s) identified it
       - Assign priority (Must / Should / Could / Won't)
       - Note any conflicts between perspectives
    
    2. CONFLICT RESOLUTIONS
       Where perspectives disagree, resolve the conflict:
       - State the conflict clearly
       - List each perspective's position
       - Your resolution and rationale
    
    3. UNIFIED PERSONAS
       Create 1-3 behavioral personas that incorporate needs from all roles.
       Tag each need with which role surfaced it.
       Format:
         ## Primary User: [Name/Role]
         - How they discover the product
         - What they know/don't know
         - What makes them leave
         - What makes them stay
         - Device/context of use
         - [Developer] needs: ...
         - [DevOps] needs: ...
         - [Security] needs: ...
    
    4. UNIFIED JOURNEY
       Write a narrative journey for the primary persona.
       Annotate with cross-cutting concerns:
         "At this step, Security requires X, DevOps needs Y"
       Format: numbered steps, narrative paragraphs, specific details,
       timing expectations, named UI elements.
    
    5. COMPREHENSIVE SCENARIO TABLE
       Merge all scenarios from all perspectives into one table:
         | Scenario | Source Role | Category | Priority |
       Categories: Normal, Interruption, Boundary, Operational, Security
       Include out-of-scope items with consensus notes.
    
    6. SCOPE BOUNDARY
       - In Scope (consensus across roles)
       - Out of Scope (consensus across roles)
       - Debated (PM decided) — with rationale for inclusion/exclusion
    
    7. OPEN DECISIONS
       Items that require the user's input.
       Tag with which role surfaced the question.
    
    Output the complete synthesis document.
  """
)
```

### 4.2 Save Synthesis Artifacts

From the PM synthesis output, create:

- `.ratchet/story/synthesis.md` — the full PM synthesis document
- `.ratchet/story/personas.md` — extracted unified personas
- `.ratchet/story/journey.md` — extracted unified journey
- `.ratchet/story/scenarios.md` — extracted comprehensive scenario table
- `.ratchet/story/decisions.md` — decisions log with role tags

### 4.3 Generate Visual Artifacts

For projects with user-facing interface:

**Mood (.ratchet/story/mood.md)**:

```markdown
## Visual Direction

Mood: [2-4 adjectives describing the feeling]
References: [1-3 reference sites/apps with what to borrow from each]
Anti-patterns: [things to explicitly avoid]

## Color Direction
[General palette direction, not exact hex values]

## Typography Direction
[Font style, sizing philosophy]

## Layout Philosophy
[Mobile-first? Dense? Spacious? Single-page?]
```

**Prototype (.ratchet/story/prototype.html)**:

- 3-5 key screens with real layout and placeholder data
- Inline CSS with actual colors, typography, spacing (not wireframes)
- Click-through navigation between screens
- Mobile viewport meta tag for mobile projects
- Self-contained — no external dependencies

For non-UI projects (CLI, library, API), skip these artifacts.

---

## Step 5: Multi-Perspective User Confirmation

### 5.1 Present PM Synthesis with Perspectives Visible

Present the synthesis so the user can see EACH role's contribution:

```
Story artifacts generated for [project name]:

## Role Perspectives Summary

### End User perspective ([N] requirements, [N] concerns)
  ✓ [key requirement summaries]
  ⚠ [concerns if any]

### Developer perspective ([N] requirements, [N] concerns)
  ✓ [key requirement summaries]
  ⚠ [concerns if any]

### DevOps perspective ([N] requirements, [N] concerns)
  ✓ [key requirement summaries]
  ⚠ [concerns if any]

### Security perspective ([N] requirements, [N] concerns)
  ✓ [key requirement summaries]
  ⚠ [concerns if any]

### QA perspective ([N] requirements, [N] concerns)
  ✓ [key requirement summaries]
  ⚠ [concerns if any]

## PM Synthesis

### Conflict Resolutions ([N] conflicts resolved)
  1. [conflict] — [resolution summary]
  2. [conflict] — [resolution summary]

### Unified Requirements: [N] total
  Must:   [N] requirements
  Should: [N] requirements
  Could:  [N] requirements
  Won't:  [N] requirements (explicitly excluded)

### Personas: [N] personas ([names])
### Journey: [N]-step journey for [primary persona]
### Scenarios: [N] total ([N] normal, [N] boundary, [N] operational, [N] security, [N] excluded)

## Open Questions (need your input)
  1. [question] — flagged by [role]
  2. [question] — flagged by [role]

Approve, adjust, or discuss?
```

### 5.2 Iterate on Feedback

User may:
- Answer open questions → update decisions.md, re-run PM synthesis on affected areas
- Disagree with a conflict resolution → PM re-resolves with user's input
- Add/remove requirements → update synthesis
- Modify personas, journey, scenarios → update affected artifacts
- Request prototype changes → regenerate prototype
- Request a specific role to dig deeper → re-run that perspective agent with more focus

Each change cascades through dependent artifacts. Always show what changed.

### 5.3 Prototype Review (if applicable)

If a prototype was generated, prompt the user to open and click through:

```
Open the prototype and click through the flow:
file://[absolute-path]/.ratchet/story/prototype.html

Tell me what to change — layout, sizing, colors, flow.
```

Iterate on prototype feedback until user approves.

---

## Step 6: Complexity Estimation

After all artifacts are confirmed, estimate complexity:

### 6.1 Story Point Estimation

```yaml
# .ratchet/story/complexity.yaml
total_estimate: [N] points
recommended_split: [1 or N] phases
rationale: "[why this estimate]"
```

### Story Point Scale

```
1-5 points:    Trivial. Single WP, < 30 min agent time.
5-15 points:   Small. 2-4 WPs, one spec, one session.
15-30 points:  Medium. 5-10 WPs, one spec, one session.
30-60 points:  Large. Must split into multiple phases.
60+ points:    Very large. Must split. Each phase < 30 points.
```

### 6.2 Auto-Split (if > 30 points)

If total > 30 points, proceed to Manager agent for phase splitting (Step 7). Otherwise, skip to Step 8.

---

## Step 7: Manager Agent — Spec Sequencing

### 7.1 Spawn Manager Agent

After user confirms the PM synthesis (and for projects > 30 points OR when the Manager determines splitting is beneficial):

```
Agent(
  subagent_type: "general-purpose",
  model: opus,
  prompt: """
    You are the Engineering Manager agent.
    
    Project intent: {user_intent_description}
    Confirmed PM synthesis: {path to synthesis.md}
    Complexity estimate: {total_estimate} points
    
    Your job: decompose the confirmed requirements into specs and phases.
    
    Produce a plan overview with:
    
    1. SPEC DECOMPOSITION
       Which requirements group into which spec/phase.
       Why this grouping (technical dependency, user value, risk).
    
    2. ORDERING
       Which spec/phase comes first.
       Dependency graph between specs.
    
    3. RISK ASSESSMENT
       Which specs are highest risk.
       What should be prototyped or validated first.
    
    4. MILESTONE MAPPING
       What's deliverable after each spec/phase.
       What the user can review/demo after each phase.
    
    Output format:
    
    # Plan Overview
    
    ## Spec Decomposition
    
    ### Phase 1: [name] ([N] points)
    Requirements: [R-01, R-03, R-07, ...]
    Rationale: [why this grouping]
    Deliverable: [what user gets after this phase]
    Risk: [low/medium/high] — [why]
    
    ### Phase 2: [name] ([N] points)
    Requirements: [R-02, R-04, ...]
    Depends on: [Phase 1]
    Rationale: [why this grouping]
    Deliverable: [what user gets]
    Risk: [level] — [why]
    
    ## Dependency Graph
    Phase 1 → Phase 2 → Phase 3
    Phase 1 → Phase 3 (partial)
    
    ## Recommended Order
    1. Phase 1 — [rationale for going first]
    2. Phase 2 — [rationale]
    3. Phase 3 — [rationale]
    
    ## Risk Mitigation
    - [risk] → [mitigation strategy]
  """
)
```

### 7.2 Save Plan Overview

Save to `.ratchet/story/plan-overview.md`.

### 7.3 Present to User

```
Manager's plan:

  Phase 1: [name] ([N] pts) — [deliverable summary]
  Phase 2: [name] ([N] pts) — [deliverable summary]
  Phase 3: [name] ([N] pts) — [deliverable summary]

  Dependencies: Phase 1 → Phase 2 → Phase 3
  Highest risk: Phase [N] — [reason]

OK with this split? Want to adjust?
```

### 7.4 Create Phase Structure

On confirmation, create phase directories:

```
.ratchet/
├── story/                      # Top-level story (big picture)
│   ├── perspectives/           # All perspective documents
│   ├── synthesis.md            # Full PM synthesis
│   ├── personas.md
│   ├── journey.md              # Full journey across all phases
│   ├── scenarios.md            # All scenarios
│   ├── complexity.yaml         # Estimate + phase split
│   ├── plan-overview.md        # Manager's sequencing plan
│   ├── roles.yaml              # Active roles
│   └── decisions.md
├── phases/
│   ├── phase-1/
│   │   └── story/              # Phase 1 subset
│   │       ├── journey.md
│   │       ├── scenarios.md
│   │       └── prototype.html
│   ├── phase-2/
│   │   └── story/
│   │       └── ...
│   └── ...
```

For simple projects (< 30 points), keep flat structure — no phases directory.

---

## Step 8: Confirm and Transition

### 8.1 Final Confirmation

```
Story phase complete. All artifacts confirmed:
  - [N] roles participated ([role names])
  - [N] perspective documents generated
  - PM synthesis: [N] unified requirements, [N] conflicts resolved
  - [N] personas, [N]-step journey
  - [N] scenarios ([N] normal, [N] boundary, [N] excluded)
  - [Visual mood confirmed, prototype approved | N/A for non-UI project]
  - [N] decisions resolved, [N] agent-decided
  [- Manager plan: [N] phases | Single-phase project]

Ready to generate the Intent Spec from these artifacts?
```

### 8.2 Transition to Spec

On confirmation:
1. Mark story phase as complete in state
2. **Auto-invoke the spec skill** — do not wait for user to call `/ratchet:spec`
3. Spec phase reads `.ratchet/story/synthesis.md` and other artifacts as input

### 8.3 Session Boundary (for phases)

If the project was split into phases:
- Generate Phase 1 story artifacts (subset of full story)
- Transition to Phase 1 spec
- After Phase 1 spec confirmation, suggest new session for execution:

```
Phase 1 spec is ready. Starting execution requires a fresh session 
for best quality.

All context has been saved to .ratchet/phases/phase-1/

Please start a new Claude Code session and I'll continue from 
where we left off.
```

---

## Incremental Updates

Story supports updates after initial creation. When the user describes changes to a completed project:

1. Identify which story artifacts are affected
2. Determine which role perspectives are impacted
3. Re-run affected perspective agents if the change is significant enough
4. Re-run PM synthesis on the affected area (not full re-synthesis for small changes)
5. Show what changed, including any new conflict resolutions
6. Cascade: story update → spec re-derivation → test update → execution → full verification
7. Update decision log with new decisions

```
User: "Add rate limiting to the API"

Agent detects: story-level change, impacts Security + DevOps + Developer perspectives.
1. Re-run Security perspective agent on rate limiting specifics
2. Re-run DevOps perspective agent on operational impact
3. PM re-synthesizes affected requirements
4. Update synthesis.md, scenarios.md, decisions.md
5. Cascade to spec (re-derive affected constraints)
```

For minor updates (tweaking a scenario, adjusting a persona detail), skip re-running perspective agents — just update the artifacts directly.

---

## Rules

1. **Perspectives before synthesis.** Always gather role perspectives before producing unified artifacts.
2. **PM synthesizes, user confirms.** The PM agent does the hard work of reconciliation; the user makes final calls.
3. **Perspectives visible during confirmation.** The user must see which roles contributed what, not just the merged result.
4. **Roles are domain-specific.** Use the role registry for the project's domain. Don't invent roles outside the registry without user input.
5. **Parallel execution.** Perspective agents run in parallel for speed. PM and Manager run sequentially after.
6. **Human language only.** No YAML, no test methods, no constraint IDs in story artifacts. Those come in spec.
7. **Out of scope is mandatory.** Every scenario table must have an explicit out-of-scope section.
8. **Iterate until confirmed.** No time limit. The investment here saves rework later.
9. **Decisions are classified.** Every decision is either user-confirmed, agent-decided (with rationale), or open.
10. **Prototype is a skeleton.** Not the final product — direction confirmation only.
11. **Cascade updates.** Any story change flows through to spec, tests, and execution.
12. **Domain research first.** For domain-specific projects, research before spawning perspective agents.
13. **Complexity estimation.** Always estimate story points. Split if > 30 points.
14. **Manager sequences.** For multi-phase projects, the Manager agent decides spec ordering, not the user or PM.
15. **Sonnet for perspectives, Opus for synthesis.** Individual role agents run on Sonnet. PM and Manager run on Opus.
