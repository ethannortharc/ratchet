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
Agent: Manager agent plans sprints (each spec = one sprint)

=== Story phase complete → auto-transition to Spec ===
```

The spec phase then reads the PM synthesis and auto-extracts machine-verifiable constraints. Most of the hard alignment work happens here in story, not in spec.

---

## When to Use

- **New intent**: Always start with `/ratchet:story` for any non-trivial project
- **Standalone spec**: `/ratchet:spec` still works directly for simple projects or when the user already has a clear spec in mind
- **Updates**: User describes changes to an existing project → agent routes here for story-level updates, then cascades to spec

## Artifacts

Story phase produces artifacts in `.ratchet/story/` (single sprint) or `.ratchet/sprints/{sprint-id}/story/` (multi-sprint):

| Artifact | File | Purpose |
|----------|------|---------|
| Perspectives | `perspectives/*.md` | Per-role requirements, concerns, scenarios |
| PM Synthesis | `synthesis.md` | Unified requirements, conflict resolutions, prioritized scope |
| Personas | `personas.md` | Behavioral personas enhanced with role-tagged needs |
| Journey | `journey.md` | Narrative walkthrough with cross-cutting annotations |
| Scenarios | `scenarios.md` | Comprehensive scenario table with source-role column |
| Mood + Prototype | `mood.md` + `prototype.html` | Visual direction and clickable skeleton |
| Decisions | `decisions.md` | Every decision made, classified and tracked |
| Sprint Plan | `sprint-plan.md` | Manager's sprint planning and milestone mapping |
| Active Roles | `roles.yaml` | Which roles participated in this project |

---

## Step 1: Analyze Intent + Context

### 1.1 Load Profile
Check `~/.config/ratchet/profile.yaml`. If missing, ask 3 quick preference questions and create it.

### 1.2 Detect Project Mode

Determine whether this is a **greenfield** (new project) or **existing project** (code already exists):

```
Check workspace for existing code:
  - Source files exist? (*.ts, *.py, *.go, etc.)
  - Package manager files? (package.json, go.mod, Cargo.toml, etc.)
  - Existing architecture? (directories, configs, deployment files)

Mode A: Greenfield — no existing code
  → Domain research only
  → Perspective agents generate from intent + domain knowledge

Mode B: Existing project — code already exists
  → Codebase analysis FIRST (understand what exists)
  → Domain research if needed
  → Perspective agents generate from intent + codebase context + domain knowledge
```

### 1.3 Codebase Analysis (existing project only)

For existing projects, spawn a **Codebase Analyst** subagent (Explore agent) to understand the current state:

```
Agent(
  subagent_type: "Explore",
  prompt: """
    Analyze this codebase and produce a concise architecture summary:
    
    1. Tech stack: languages, frameworks, libraries, build tools
    2. Architecture: directory structure, key patterns, layers
    3. Existing conventions: API style (REST/GraphQL), auth mechanism,
       testing setup, deployment config, CI/CD
    4. Dependencies: external services, databases, third-party APIs
    5. Gaps: missing tests, missing docs, obvious technical debt
    6. Constraints: what's already committed to and hard to change
    
    Be factual. Report what IS, not what should be.
  """
)
```

Save output to `.ratchet/story/codebase-analysis.md`. This becomes input to all perspective agents.

### 1.4 Domain Research

For domain-specific projects, research the domain BEFORE deriving roles:

1. Identify what domain knowledge shapes the requirements
2. Spawn research subagent(s) with explicit tools:
   - **WebSearch** for domain best practices, industry standards, competitor analysis
   - **context7 MCP** for library/framework documentation
   - **WebFetch** for specific reference materials (specs, standards, regulations)
3. Save findings to `.ratchet/story/domain-research.md`

**Skip** if the domain is generic (CRUD app, landing page, CLI tool) or agent has sufficient knowledge.

### 1.5 Register Intent

If this is a new intent (not an update):

```
Intent ID? [auto-generated from name, user can override]
Workspace? [current dir / create new / custom path]
```

Register in `~/.config/ratchet/state.yaml` with status: `draft`.

---

## Step 2: Derive Roles from Intent

Roles are **not picked from a static list** — they are derived from what the intent needs. The role registry (`references/role-registry.yaml`) is a **template library** of common roles, not a checklist to filter.

### 2.1 Analyze What Expertise Is Needed

From the intent description, domain research, and codebase analysis (if existing project), determine:

```
What do we need to understand to build this correctly?
What perspectives would catch blind spots?
What expertise is required that isn't obvious from the intent?
```

**Think in terms of expertise gaps, not job titles.** Examples:

```
Intent: "Build a real-time stock trading dashboard"
  Expertise needed:
  → Financial domain (regulations, data feeds, pricing) — not in registry
  → Low-latency data handling (WebSockets, streaming) — specialized Developer
  → Regulatory compliance — not in registry
  → Real-time UX patterns — specialized End User
  → High availability — DevOps
  → Financial data security — Security

Intent: "Add dark mode to existing React app"
  Expertise needed:
  → Existing codebase constraints — from codebase analysis
  → CSS/theming patterns — Developer
  → Accessibility (contrast ratios) — End User
  → NO need for: DevOps, Security, domain research

Intent: "Build a CLI tool for parsing CSV files"
  Expertise needed:
  → CLI ergonomics (flags, help text, exit codes) — End User (CLI-focused)
  → CSV edge cases (encoding, escaping, malformed) — QA
  → Library API design — Developer
  → NO need for: DevOps, Security, UI design
```

### 2.2 Match to Role Templates or Create New Roles

For each expertise need:
1. Check if a role template in the registry matches → use it as a starting point
2. If no template matches → create a new role on the fly
3. Customize the role description to be specific to THIS project

**The registry is a starting point, not a boundary.** If the intent needs a "Compliance Officer" or "Data Engineer" or "Performance Engineer" perspective, create it — don't force-fit into existing templates.

### 2.3 Always Include PM and Manager

PM (synthesis) and Manager (planning) are structural roles — they always participate regardless of intent. They are part of the process, not part of the domain.

### 2.4 Present Derived Roles to User

```
Based on what we're building, I need these perspectives:

  ✓ End User (CLI-focused) — CLI ergonomics, help text, error messages
  ✓ Developer — library API design, extensibility, code quality
  ✓ QA / Tester — CSV edge cases, encoding issues, malformed input
  ✓ PM — synthesis and prioritization
  ✓ Manager — spec sequencing

  Not needed for this project:
  ✗ DevOps — no deployment, single binary distribution
  ✗ Security — no network, no user data, no auth

  Why these roles: This is a data processing CLI tool. The critical
  perspectives are input edge cases (QA), developer experience (Developer),
  and CLI usability (End User). No operational or security concerns.

Add, remove, or adjust any roles?
```

**Key difference from static approach**: The agent explains WHY each role was chosen (or excluded) based on the intent. The user sees the reasoning, not just a checklist.

### 2.5 Save Active Roles

Write `.ratchet/story/roles.yaml`:

```yaml
derived_from: "intent analysis"  # NOT "registry filter"
project_mode: greenfield | existing
active_roles:
  - id: end_user_cli
    name: "End User (CLI-focused)"
    description: "CLI ergonomics, help text, error messages, piping behavior"
    reason: "CLI tool — usability is the primary UX concern"
    based_on: end_user  # Registry template used as starting point (or "custom")
    model: sonnet
  - id: developer
    name: "Developer"
    description: "Library API design, extensibility, code quality"
    reason: "Tool may be used as a library — API design matters"
    based_on: developer
    model: sonnet
  - id: qa_tester
    name: "QA / Tester"
    description: "CSV edge cases, encoding issues, malformed input handling"
    reason: "Data parsing is the core function — edge cases are critical"
    based_on: qa_tester
    model: sonnet
  - id: pm
    name: "Product Manager"
    reason: "structural — always present"
    based_on: pm
    model: opus
  - id: manager
    name: "Engineering Manager"
    reason: "structural — always present"
    based_on: manager
    model: opus
excluded_roles:
  - id: devops
    reason: "No deployment — single binary distribution"
  - id: security
    reason: "No network, no user data, no authentication"
```

---

## Step 3: Parallel Perspective Gathering

### 3.1 Spawn Perspective Agents

For each active role (except PM and Manager — they come later), spawn a parallel subagent:

```
Agent(
  subagent_type: "general-purpose",
  model: [role's model — typically sonnet],
  prompt: """
    You are the {role_name} perspective agent for a software project.
    
    Project intent: {user_intent_description}
    Project mode: {greenfield | existing}
    Domain context: {domain_research_findings if any}
    Codebase context: {codebase_analysis if existing project, else "N/A — greenfield"}
    User profile: {profile preferences}
    
    Your role description: {role_description}
    Why you were included: {role_reason}
    
    Your job: analyze this project EXCLUSIVELY from the {role_name} perspective.
    Produce requirements, concerns, scenarios, and constraints that someone
    with your expertise would identify.
    
    IMPORTANT for existing projects:
    - Read the codebase analysis carefully — your requirements must be
      compatible with what already exists
    - Don't suggest replacing established patterns without strong justification
    - Identify what the existing codebase does well AND what it's missing
      from your perspective
    
    IMPORTANT for greenfield projects:
    - Use domain research findings to ground your requirements in real-world
      best practices, not generic advice
    - Be specific to THIS project, not generic platitudes
    
    Focus on what matters to YOUR perspective. Don't try to cover
    everything — other role agents handle other perspectives.
    
    Output format:
    
    # {role_name} Perspective
    
    ## Context
    What this role cares about for this project.
    [For existing projects: what the current codebase does well/poorly
     from this perspective]
    
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

## Step 6: Backlog Estimation

After all artifacts are confirmed, the PM synthesis output IS the **product backlog** — a prioritized list of requirements from all perspectives. Now estimate complexity:

### 6.1 Story Point Estimation

```yaml
# .ratchet/story/complexity.yaml
total_estimate: [N] points
rationale: "[why this estimate]"
```

### Story Point Scale

```
1-5 points:    Trivial. Single WP, one sprint.
5-15 points:   Small. 2-4 WPs, likely one sprint.
15-30 points:  Medium. 5-10 WPs, one or two sprints.
30-60 points:  Large. Multiple sprints needed.
60+ points:    Very large. Multiple sprints, each < 30 points.
```

---

## Step 7: Sprint Planning (Manager Agent)

The Manager agent **always runs** — even for small projects. Sprint planning is not triggered by a threshold; it's a structural step. The Manager decides how many sprints are needed, not a number.

```
Agile mapping:
  Product Backlog  =  PM synthesis output (prioritized requirements)
  Sprint Planning  =  Manager agent (this step)
  Sprint           =  Spec (one subset of backlog, executed to completion)
  Sprint Execution =  Plan → Execute → Verify → Acceptance
  Sprint Review    =  /ratchet:review
```

### 7.1 Spawn Manager Agent

```
Agent(
  subagent_type: "general-purpose",
  model: opus,
  prompt: """
    You are the Engineering Manager agent doing sprint planning.
    
    Project intent: {user_intent_description}
    Product backlog (PM synthesis): {path to synthesis.md}
    Complexity estimate: {total_estimate} points
    Codebase context: {codebase_analysis if existing project}
    
    The PM synthesis contains the prioritized product backlog.
    Your job: decide how to break this backlog into sprints.
    
    Each sprint becomes one Spec — a self-contained unit of work
    that produces a deliverable result.
    
    SPRINT PLANNING RULES:
    - Each sprint should be completable in one session (~30 points max)
    - Each sprint should produce something the user can review/demo
    - Earlier sprints should deliver higher-priority (Must) requirements first
    - Dependencies determine ordering — don't schedule work before its prerequisites
    - It's OK to plan just one sprint if the backlog is small enough
    
    Produce a sprint plan:
    
    1. SPRINT DECOMPOSITION
       Which backlog items go into which sprint.
       Why this grouping (dependency, value, risk).
    
    2. ORDERING
       Which sprint comes first.
       Dependency graph between sprints.
    
    3. RISK ASSESSMENT
       Which sprints are highest risk.
       What should be prototyped or validated first.
    
    4. MILESTONE MAPPING
       What's deliverable after each sprint.
       What the user can review/demo after each sprint.
    
    Output format:
    
    # Sprint Plan
    
    ## Number of sprints: [N]
    ## Rationale: [why this number — "backlog fits in one sprint" is valid]
    
    ### Sprint 1: [name] ([N] points)
    Backlog items: [R-01, R-03, R-07, ...]
    Rationale: [why this grouping]
    Deliverable: [what user gets after this sprint]
    Risk: [low/medium/high] — [why]
    
    ### Sprint 2: [name] ([N] points)  (if needed)
    Backlog items: [R-02, R-04, ...]
    Depends on: [Sprint 1]
    Rationale: [why this grouping]
    Deliverable: [what user gets]
    Risk: [level] — [why]
    
    ## Dependency Graph
    Sprint 1 → Sprint 2 → Sprint 3
    
    ## Recommended Order
    1. Sprint 1 — [rationale for going first]
    2. Sprint 2 — [rationale]
    
    ## Risk Mitigation
    - [risk] → [mitigation strategy]
  """
)
```

### 7.2 Save Sprint Plan

Save to `.ratchet/story/sprint-plan.md`.

### 7.3 Present to User

**Single sprint:**
```
Sprint plan:

  Sprint 1: [name] ([N] pts) — covers all backlog items
  
  This project fits in a single sprint. All [N] requirements
  will be delivered together.

OK to proceed?
```

**Multiple sprints:**
```
Sprint plan:

  Sprint 1: [name] ([N] pts) — [deliverable summary]
  Sprint 2: [name] ([N] pts) — [deliverable summary]
  Sprint 3: [name] ([N] pts) — [deliverable summary]

  Dependencies: Sprint 1 → Sprint 2 → Sprint 3
  Highest risk: Sprint [N] — [reason]

  Each sprint generates its own Spec and runs in a fresh session.

OK with this plan? Want to adjust?
```

### 7.4 Create Sprint Structure

**Single sprint** — flat structure, no sprints directory:

```
.ratchet/
├── story/                      # Product backlog (story artifacts)
│   ├── perspectives/
│   ├── synthesis.md            # = product backlog
│   ├── sprint-plan.md          # Manager's plan (1 sprint)
│   ├── ...
└── {intent-id}/                # Sprint 1 = the only sprint
    ├── spec.yaml
    ├── plan.yaml
    ├── test-suite/
    └── ...
```

**Multiple sprints** — each sprint gets its own directory:

```
.ratchet/
├── story/                      # Product backlog (full picture)
│   ├── perspectives/
│   ├── synthesis.md            # = product backlog
│   ├── sprint-plan.md          # Manager's sprint plan
│   ├── complexity.yaml
│   ├── ...
├── sprints/
│   ├── sprint-1/
│   │   └── story/              # Sprint 1 backlog subset
│   │       ├── journey.md
│   │       ├── scenarios.md
│   │       └── prototype.html
│   ├── sprint-2/
│   │   └── story/
│   │       └── ...
│   └── ...
```

---

## Step 8: Confirm and Transition

### 8.1 Final Confirmation

```
Story phase complete. All artifacts confirmed:

  Product Backlog:
    - [N] roles contributed perspectives
    - [N] unified requirements ([N] Must, [N] Should, [N] Could)
    - [N] conflicts resolved by PM
    - [N] personas, [N]-step journey
    - [N] scenarios ([N] normal, [N] boundary, [N] excluded)
    [- Visual mood confirmed, prototype approved | N/A]

  Sprint Plan:
    - [N] sprint(s) planned by Manager
    [- Sprint 1: [name] ([N] pts) — [deliverable]]
    [- Sprint 2: [name] ([N] pts) — [deliverable]]

Ready to start Sprint 1?
```

### 8.2 Transition to Spec (= Start Sprint 1)

On confirmation:
1. Mark story phase as complete in state
2. **Auto-invoke the spec skill** for Sprint 1
3. Spec phase reads sprint backlog items from synthesis.md + sprint-plan.md

For single-sprint projects, the spec covers the entire backlog.
For multi-sprint projects, the spec covers Sprint 1's backlog items only.

### 8.3 Session Boundary (for multi-sprint projects)

Each sprint should start in a fresh session for best quality:

```
Sprint 1 spec is ready. Starting execution requires a fresh session.

All context has been saved to .ratchet/sprints/sprint-1/

Please start a new Claude Code session and I'll continue from 
where we left off.
```

After Sprint 1 completes → review → start new session for Sprint 2.

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

1. **Roles derive from intent.** Don't filter a static list — analyze what expertise the intent needs. The registry is a template library, not a checklist.
2. **Codebase context for existing projects.** Always run codebase analysis before spawning perspectives. Perspective agents must know what exists.
3. **Perspectives before synthesis.** Always gather role perspectives before producing unified artifacts.
4. **PM synthesizes, user confirms.** The PM agent does the hard work of reconciliation; the user makes final calls.
5. **Perspectives visible during confirmation.** The user must see which roles contributed what, not just the merged result.
6. **Explain role choices.** When presenting derived roles, explain WHY each was included or excluded based on the intent.
7. **Parallel execution.** Perspective agents run in parallel for speed. PM and Manager run sequentially after.
8. **Human language only.** No YAML, no test methods, no constraint IDs in story artifacts. Those come in spec.
9. **Out of scope is mandatory.** Every scenario table must have an explicit out-of-scope section.
10. **Iterate until confirmed.** No time limit. The investment here saves rework later.
11. **Decisions are classified.** Every decision is either user-confirmed, agent-decided (with rationale), or open.
12. **Prototype is a skeleton.** Not the final product — direction confirmation only.
13. **Cascade updates.** Any story change flows through to spec, tests, and execution.
14. **Domain research with real tools.** Use WebSearch, context7, WebFetch — not just LLM knowledge. Ground perspectives in facts.
15. **Complexity estimation.** Always estimate story points.
16. **Manager always runs.** Sprint planning is structural, not triggered by a threshold. The Manager decides how many sprints — even if the answer is "one."
17. **Spec = Sprint.** Each spec executes one sprint's worth of backlog items. Story output is the product backlog; specs are sprints that consume it.
17. **Sonnet for perspectives, Opus for synthesis.** Individual role agents run on Sonnet. PM and Manager run on Opus.
