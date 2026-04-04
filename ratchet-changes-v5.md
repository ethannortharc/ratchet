# Ratchet Plugin — Change Specification v5

Read DESIGN.md and ratchet-changes-v4.md first.
This document covers the role-based perspective system, based on the realization that "from whose perspective?" must be answered explicitly throughout the entire pipeline.

---

## Summary

The core insight: **features serve multiple stakeholders with competing concerns, but Ratchet treats "the user" as monolithic.** A search feature looks completely different to an end-user (fast, intuitive), a developer (clean API, extensible), DevOps (scalable, monitorable), and QA (testable, edge-case-covered). When we build from a single perspective, we ship blind spots.

The solution is not to add all perspectives in one phase — it's to distribute the right roles across the entire pipeline. Story phase needs end-users and developers at the table. Verification needs QA. Planning needs a manager. And a PM synthesizes it all.

Major changes:
1. Role-based perspective agents distributed across the pipeline
2. Domain-specific role registry (software development as first supported domain)
3. PM synthesis agent for story phase
4. Manager agent for spec sequencing
5. Multi-perspective user confirmation
6. Role-aware verification (QA perspective in verify phase)
7. Perspective Acceptance Review — validate built output against original perspectives

---

## Change 24: Role-Based Perspective System

### Problem

Today's story phase generates personas that describe end-users of the product being built. But "who are we building for?" is only one question. The equally important question — "who needs to be in the room when we decide what to build?" — is never asked.

A developer building a REST API needs to think about:
- **End-user**: "I call the endpoint, I get data, it's fast"
- **Developer** (peer/consumer): "The API is well-documented, consistent, easy to integrate"
- **DevOps/SRE**: "I can deploy it, scale it, monitor it, roll it back"
- **QA/Tester**: "I can test it deterministically, edge cases are defined"
- **Security**: "Auth is solid, data is protected, inputs are validated"

These aren't product personas — they're **stakeholder perspectives** that shape requirements. Missing any one of them means discovering gaps during execution or (worse) after deployment.

### Solution

Introduce **role agents** — subagents that inhabit specific stakeholder perspectives and contribute requirements from their angle. Roles are distributed across the pipeline, participating where their expertise matters.

### Role distribution across phases

```
Phase           | Active Roles              | Purpose
----------------|---------------------------|----------------------------------
Story           | End-user, Developer,      | Each role produces requirements
                | DevOps, Security          | from their perspective
                |                           |
PM Synthesis    | PM (reads all role output) | Reconciles conflicts, produces
                |                           | unified requirements document
                |                           |
User Confirm    | Human (sees all angles)   | Final authority with full picture
                |                           |
Spec            | (auto-derived from PM     | Constraints tagged by source role
                |  synthesis output)        |
                |                           |
Planning        | Manager                   | Sequences specs, manages deps,
                |                           | decides phase ordering
                |                           |
Execution       | (autonomous, as today)    | wp-executor, existing agents
                |                           |
Verification    | QA/Tester                 | Reviews test coverage, edge cases,
                |                           | validates scenario completeness
                |                           |
Review          | PM (summary), optional    | Structured review from relevant
                | role-specific review      | perspectives
```

### Key principle: roles are not phases

A role doesn't own a phase — it **participates** in phases where its expertise matters. The PM doesn't just appear once; it synthesizes during story and summarizes during review. QA doesn't just verify; it can flag testability concerns during story discussion.

---

## Change 25: Domain-Specific Role Registry

### Problem

Different domains need different roles. A mobile app project needs a UX designer perspective. An infrastructure project needs a platform engineer perspective. A data pipeline needs a data engineer perspective. Hardcoding roles doesn't scale.

### Solution

Define role registries per domain. Software development is the first (and currently only) supported domain. The registry defines which roles exist, what they contribute, and in which phases they participate.

### Software development role registry

```yaml
# references/role-registry.yaml
domain: software_development

roles:
  end_user:
    name: "End User"
    description: "Represents the people who will directly use the product"
    contributes:
      - User flows and expectations
      - Usability requirements
      - Accessibility needs
      - Performance expectations (perceived speed)
    participates_in: [story]
    priority: required  # Must always participate

  developer:
    name: "Developer"
    description: "Represents developers who build, maintain, or integrate with this system"
    contributes:
      - API design and developer experience
      - Code maintainability requirements
      - Extensibility and integration points
      - Documentation needs
    participates_in: [story]
    priority: required

  devops:
    name: "DevOps / SRE"
    description: "Represents operational concerns — deployment, monitoring, reliability"
    contributes:
      - Deployment and rollback requirements
      - Monitoring and observability needs
      - Scaling and performance constraints
      - Infrastructure dependencies
    participates_in: [story]
    priority: conditional  # Include when project has deployment/infra concerns

  security:
    name: "Security"
    description: "Represents security posture — auth, data protection, threat surface"
    contributes:
      - Authentication and authorization requirements
      - Data handling and privacy constraints
      - Input validation requirements
      - Threat surface analysis
    participates_in: [story]
    priority: conditional  # Include when project handles user data or external input

  qa_tester:
    name: "QA / Tester"
    description: "Represents testability and quality assurance"
    contributes:
      - Testability requirements
      - Edge case identification
      - Scenario completeness review
      - Test strategy recommendations
    participates_in: [story, verification]
    priority: required

  pm:
    name: "Product Manager"
    description: "Synthesizes all perspectives into a unified, prioritized requirements document"
    contributes:
      - Conflict resolution between perspectives
      - Prioritization and scope decisions
      - Unified user stories
      - Acceptance criteria
    participates_in: [story_synthesis, review]
    priority: required  # Always the synthesizer

  manager:
    name: "Engineering Manager"
    description: "Plans execution sequence, manages dependencies and phasing"
    contributes:
      - Spec sequencing and dependency ordering
      - Phase splitting decisions
      - Risk identification
      - Resource allocation guidance
    participates_in: [planning]
    priority: required  # Always handles sequencing
```

### Role selection logic

Not every project needs every role. During story phase initialization:

```
1. Agent reads the user's intent description
2. Agent reads the role registry for the domain
3. For each role with priority: conditional
   → Evaluate: does this project involve the role's concern area?
   → e.g., "pure frontend, no auth" → skip Security
   → e.g., "CLI tool, single binary" → skip DevOps
4. Present selected roles to user for confirmation:
   "For this project, I'll gather perspectives from:
    - End User (required)
    - Developer (required)
    - QA/Tester (required)
    - DevOps (your project deploys to Vercel)
    - Security (skipped — no auth, no user data)
    Add or remove any?"
5. User confirms or adjusts
```

### Custom roles

Users can define project-specific roles:

```yaml
# .ratchet/roles.yaml (per-project override)
additional_roles:
  data_engineer:
    name: "Data Engineer"
    description: "Represents data pipeline and quality concerns"
    contributes:
      - Data validation and schema requirements
      - Pipeline reliability
      - Data freshness and consistency
    participates_in: [story, verification]

exclude_roles: [devops]  # Not relevant for this project
```

### Files to create
- `references/role-registry.yaml` — domain role definitions

### Files to modify
- `skills/story/SKILL.md` — role selection + role agent spawning
- `references/spec-schema.md` — document role registry format
- `DESIGN.md` — document role-based perspective system

---

## Change 26: Perspective Agents in Story Phase

### Problem

Currently, the story phase is a single agent generating all artifacts. It tries to think of everything, but inevitably has blind spots — because it's one mind, not a team.

### Solution

During story phase, spawn parallel subagents — one per active role — that each produce requirements from their perspective. These run concurrently for speed, then feed into PM synthesis.

### Workflow

```
User: /ratchet:story "Build a REST API for task management"

Step 1: Role Selection
  Agent: "For this project, I'll gather perspectives from:
          ✓ End User — API consumers
          ✓ Developer — maintainability, DX
          ✓ DevOps — deployment, monitoring
          ✓ Security — auth, data protection
          ✓ QA — testability, edge cases
          ✓ PM — synthesis (always)
          ✓ Manager — planning (always)
          
          Adjust?"
  
  User: "Add a 'Data Engineer' role — we have complex data models"

Step 2: Parallel Perspective Gathering (subagents)
  Each role agent receives:
    - The user's intent description
    - Domain context
    - User's profile preferences
    
  Each produces a structured perspective document:
  
  .ratchet/story/perspectives/
  ├── end-user.md
  ├── developer.md
  ├── devops.md
  ├── security.md
  ├── qa-tester.md
  └── data-engineer.md

Step 3: PM Synthesis (subagent)
  PM agent reads ALL perspective documents and produces:
    - Unified personas (enhanced — each persona now has role-tagged needs)
    - Unified journey (the primary flow, annotated with cross-cutting concerns)
    - Comprehensive scenario table (each scenario tagged with source role)
    - Conflict resolution log (where perspectives disagreed, PM's resolution)
    - Prioritized requirements (MoSCoW or similar)
  
  Output: .ratchet/story/synthesis.md

Step 4: User Confirmation (with perspectives visible)
  Agent presents synthesis WITH the underlying perspectives:
  
  "PM Synthesis:
   
   The Developer perspective wants versioned API endpoints.
   DevOps flagged that versioning adds deployment complexity.
   PM resolution: Version from day 1 using URL prefix (/v1/) —
   low cost now, high value later.
   
   Security requires rate limiting on all endpoints.
   Developer notes this affects local development experience.
   PM resolution: Rate limiting in production only, disabled in dev.
   
   Do you agree with these resolutions? Any concerns?"

Step 5: After confirmation → existing flow continues
  (spec auto-extraction, planning, execution, verification)
```

### Perspective document format

Each role agent produces a structured document:

```markdown
# [Role Name] Perspective

## Context
What this role cares about for this project.

## Requirements
- REQ-1: [requirement] — [rationale]
- REQ-2: [requirement] — [rationale]

## Concerns
- CONCERN-1: [what could go wrong from this perspective]
- CONCERN-2: [risk or gap]

## Scenarios (from this perspective)
- SCENARIO-1: [happy path from this role's view]
- SCENARIO-2: [failure mode this role worries about]

## Constraints
- CONSTRAINT-1: [hard requirement from this perspective]

## Out of Scope (from this perspective)
- [what this role considers unnecessary for MVP]
```

### PM synthesis document format

```markdown
# PM Synthesis

## Unified Requirements
| ID | Requirement | Source Roles | Priority | Conflicts |
|----|-------------|-------------|----------|-----------|
| R-01 | Versioned API endpoints | Developer, DevOps | Must | DevOps: adds deploy complexity → Resolution: URL prefix versioning |
| R-02 | Rate limiting | Security | Must | Developer: affects local DX → Resolution: prod-only |
| R-03 | OpenAPI spec auto-generated | Developer, QA | Should | None |

## Conflict Resolutions
| Conflict | Perspectives | Resolution | Rationale |
|----------|-------------|------------|-----------|
| API versioning complexity | Developer (wants) vs DevOps (concerned) | URL prefix /v1/ | Low overhead, standard practice |

## Unified Personas
(Enhanced with role-tagged needs — each persona annotated with
 which role surfaced which need)

## Unified Journey
(Primary flow with cross-cutting annotations:
 "At this step, Security requires X, DevOps needs Y")

## Comprehensive Scenario Table
| Scenario | Source Role | Category | Priority |
|----------|-----------|----------|----------|
| Create task via API | End User | Happy path | Must |
| API rate limit exceeded | Security | Boundary | Must |
| Zero-downtime deploy | DevOps | Operational | Should |
| Concurrent task updates | QA | Edge case | Must |

## Scope Boundary
### In Scope (consensus)
- ...
### Out of Scope (consensus)
- ...
### Debated (PM decided)
- [item] — [why included/excluded]
```

### Implementation detail: role agents as subagents

```
# Each role agent is spawned as a subagent with:
Agent(
  subagent_type: "general-purpose",
  prompt: """
    You are the {role_name} perspective agent.
    
    Project intent: {user_intent}
    Domain: {domain}
    
    Your job: analyze this project from the {role_name} perspective.
    Produce requirements, concerns, scenarios, and constraints
    that a {role_description} would identify.
    
    Focus on what matters to YOUR perspective. Don't try to cover
    everything — other role agents handle other perspectives.
    
    Output format: [perspective document format]
  """,
  run_in_background: true  # All role agents run in parallel
)
```

### Files to modify
- `skills/story/SKILL.md` — major rewrite: role selection, parallel agent spawning, PM synthesis step
- `DESIGN.md` — document role-based story generation

---

## Change 27: Manager Agent for Spec Sequencing

### Problem

Today, the transition from confirmed story to specs is handled by the spec skill and plan skill in sequence. For large projects, the phase splitting happens during story (Change 22 in v4) based on story points. But this misses a crucial planning perspective: **what order should things be built in, what are the technical dependencies, and how should work be distributed across specs?**

### Solution

After PM synthesis is confirmed by the user, a Manager agent handles the planning layer — deciding how to decompose the confirmed requirements into specs and phases.

### Manager agent responsibilities

```
Input: PM synthesis document (confirmed by user)

Manager produces:
1. Spec decomposition
   - Which requirements group into which spec
   - Why this grouping (technical dependency, user value, risk)
   
2. Ordering
   - Which spec/phase comes first
   - Dependency graph between specs
   
3. Risk assessment
   - Which specs are highest risk
   - What should be prototyped first
   
4. Milestone mapping
   - What's deliverable after each spec
   - What the user can review/demo after each phase

Output: .ratchet/story/plan-overview.md
```

### How it connects to existing planning

```
Before (v4):
  Story → Spec → Plan (decompose spec into WPs) → Execute

After (v5):
  Story (with roles) → PM Synthesis → User Confirm
    → Manager (decompose requirements into specs/phases)
    → Per spec: Spec → Plan (decompose into WPs) → Execute
```

The Manager operates at a **higher level** than the Plan skill. Manager decides "we need 3 specs." Plan decomposes each spec into work packages.

### Files to modify
- `skills/story/SKILL.md` — integrate Manager step after PM synthesis confirmation
- `skills/getting-started/SKILL.md` — understand Manager output for routing
- `DESIGN.md` — document two-level planning (Manager → Plan)

---

## Change 28: Role-Aware Verification

### Problem

Today's verification is mechanical: run tests, check coverage, compute scores. It doesn't ask "would QA be satisfied with this test suite?" or "does this deployment config meet DevOps standards?"

### Solution

During verification, the QA/Tester perspective agent reviews the test suite and verification results, adding qualitative assessment to the mechanical scores.

### QA agent in verification

```
After standard 3-level verification (static → unit → integration):

QA agent reviews:
1. Scenario coverage: are all scenarios from the PM synthesis tested?
2. Edge case coverage: are the edge cases from the QA perspective document covered?
3. Test quality: are tests actually testing meaningful behavior, or just asserting trivialities?
4. Missing scenarios: did execution reveal behaviors that should have tests but don't?

QA agent produces:
  .ratchet/{intent}/verification-review.md
  
  Contains:
  - Coverage gaps (scenarios without tests)
  - Test quality assessment
  - Recommended additional test cases
  - Sign-off or concerns
```

### Integration with ratchet loop

```
Standard verification score (existing): 0.0 - 1.0
QA perspective score (new):             0.0 - 1.0

Composite score considers both.
If QA flags critical gaps → score reduced → triggers ratchet retry.
```

### Files to modify
- `skills/verify/SKILL.md` — add QA perspective review step
- `agents/verifier.md` — integrate QA agent scoring
- `references/verifier-guide.md` — document QA review criteria

---

## Change 29: Multi-Perspective User Confirmation

### Problem

Today, the user confirms the story by looking at artifacts. But they see them through their own lens — they might miss DevOps concerns or security gaps because those aren't their primary expertise.

### Solution

When presenting the PM synthesis for confirmation, explicitly surface each role's perspective so the user can make informed decisions, even outside their expertise.

### Confirmation format

```markdown
## Ready for your review

### End User perspective (3 requirements, 0 concerns)
✓ All happy-path flows covered
✓ Error messages are user-friendly

### Developer perspective (5 requirements, 1 concern)
✓ API follows RESTful conventions
✓ Clear extension points
⚠ Concern: No pagination strategy defined for list endpoints

### DevOps perspective (2 requirements, 1 concern)
✓ Health check endpoint included
⚠ Concern: No logging strategy — will be hard to debug in production

### Security perspective (4 requirements, 0 concerns)
✓ JWT auth on all endpoints
✓ Input validation on all user-facing fields
✓ Rate limiting in production

### QA perspective (3 requirements, 0 concerns)
✓ All scenarios are deterministically testable
✓ Clear boundary conditions defined

### PM Resolution Summary
- 2 conflicts resolved (see details above)
- 1 item moved to "debated" scope

### Open items requiring your decision
1. Pagination: offset-based or cursor-based? (Developer flagged)
2. Log retention: 7 days or 30 days? (DevOps flagged)

Approve, adjust, or discuss?
```

This format ensures the user sees gaps they might not have thought to look for, while the PM has already done the heavy lifting of synthesis and prioritization.

### Files to modify
- `skills/story/SKILL.md` — confirmation presentation format
- `references/spec-schema.md` — document multi-perspective confirmation schema

---

## Updated Architecture Overview

```
User: "I want to build X"
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│ Role Selection (based on domain + intent)               │
│   Identify required + conditional roles                 │
│   User confirms role set                                │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ Parallel Perspective Gathering (subagents)              │
│   End-user agent → end-user.md                         │
│   Developer agent → developer.md                        │
│   DevOps agent → devops.md (if active)                  │
│   Security agent → security.md (if active)              │
│   QA agent → qa-tester.md                               │
│   [Custom roles] → [role].md                            │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ PM Synthesis (subagent)                                 │
│   Reads all perspectives → resolves conflicts           │
│   Produces: unified requirements, personas, journey,    │
│   scenarios, scope boundary, conflict log               │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ User Confirmation (multi-perspective view)              │
│   Each role's concerns visible                          │
│   PM resolutions explained                              │
│   Open decisions surfaced                               │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ Manager Agent — Spec Sequencing                         │
│   Decompose confirmed requirements into specs/phases    │
│   Dependency ordering, risk assessment                  │
│   Milestone mapping                                     │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
          Per spec/phase (existing flow enhanced):
┌─────────────────────────────────────────────────────────┐
│ Spec (auto-derived from PM synthesis, role-tagged)      │
│ Plan (decompose into WPs)                               │
│ Execute (wp-executor, ratchet loop)                     │
│ Verify (3-level + QA perspective review)                │
│ Report (proof of completion, role-tagged coverage)      │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ Acceptance Review (once per spec/phase completion)      │
│   Re-spawn role agents against actual built output      │
│   Each role: does built product match my perspective?   │
│   PM acceptance summary + verdict                       │
│   Gaps → new constraints → ratchet retry if needed      │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ Review (acceptance summary + human review items)        │
└─────────────────────────────────────────────────────────┘
```

### Updated EVA Concept

```
Perspectives → Understanding → Specification → Verification → Execution → Proof → Acceptance

Each step formalizes the previous:
  Stakeholder concerns → Human language → Machine language → Machine execution → Evidence → Perspective validation

The v5 additions:
- BEFORE understanding: establish WHO needs to understand and WHAT each stakeholder cares about
- AFTER proof: circle back to original perspectives and validate the built output against them
```

---

## Updated File Layout

### New files in story artifacts

```
.ratchet/story/
├── personas.md              # (existing, now enhanced with role tags)
├── journey.md               # (existing, now with cross-cutting annotations)
├── scenarios.md             # (existing, now with source-role column)
├── mood.md                  # (existing)
├── prototype.html           # (existing)
├── decisions.md             # (existing)
├── complexity.yaml          # (existing)
├── perspectives/            # NEW: per-role perspective documents
│   ├── end-user.md
│   ├── developer.md
│   ├── devops.md
│   ├── security.md
│   ├── qa-tester.md
│   └── [custom-role].md
├── synthesis.md             # NEW: PM synthesis output
├── plan-overview.md         # NEW: Manager spec sequencing
└── roles.yaml               # NEW: active roles for this project
```

---

## Implementation Priority

1. **Change 25: Role registry** — Foundation. Define roles before using them.
2. **Change 26: Perspective agents in story** — Core feature. Parallel role agents + PM synthesis.
3. **Change 29: Multi-perspective confirmation** — User-facing value. See all angles before confirming.
4. **Change 27: Manager agent** — Planning layer. Handles spec decomposition.
5. **Change 28: Role-aware verification** — Quality gate. QA perspective in verification.
6. **Change 30: Perspective Acceptance Review** — Closes the loop. Validates built output against original perspectives.
7. **Change 24: Role distribution** — Framework. Already implicit in 25-30, this documents the principle.

---

## Interaction with v4 Changes

- **Story phase (Change 14)**: Enhanced, not replaced. Perspective agents produce the raw input; PM synthesis replaces the single-agent story generation.
- **Spec auto-extraction (Change 15)**: Now extracts from PM synthesis document instead of raw story artifacts. Role tags on requirements flow into role-tagged constraints.
- **Decision classification (Change 16)**: PM synthesis includes conflict resolutions, which become classified decisions.
- **Proof of completion (Change 17)**: Proof now references which role's requirements each WP addresses.
- **Coverage (Change 18)**: Coverage dashboard gains a perspective axis — "which role's requirements are covered?"
- **Story splitting (Change 22)**: Manager agent replaces the complexity estimation logic; splitting is now a Manager decision.
- **Session management (Change 23)**: Unchanged. Sessions remain disposable.

---

## Change 30: Perspective Acceptance Review

### Problem

Verification checks the **spec**, not the **story**. Constraints are abstractions of intent — information is lost at each formalization step:

```
Rich perspectives → Narrow constraints → Binary tests → Pass/fail
   (100% intent)     (~70% captured)     (~50% tested)   (loses nuance)
```

An API can pass all invariants (< 200ms per call) while the end-user experience is terrible (15 sequential calls = 3 seconds). DevOps said "needs monitoring" — but is the monitoring strategy actually operational? The Developer perspective wanted "clean API" — but is the API actually ergonomic to use?

We gather rich perspectives at the start, convert them into narrow constraints in the middle, and **never circle back** to validate against the original perspectives. The verification checks the spec, not the intent.

### Solution

After all WPs in a spec/phase pass verification, re-spawn the original role agents (the same ones from story phase) and ask them to review the **actual built output** against their **original perspective document**. This is User Acceptance Testing, but from every stakeholder's perspective.

### When it runs

```
All WPs pass verification → status: agent_complete
  ↓
Perspective Acceptance Review (NEW)
  ↓
PM Acceptance Summary (NEW)
  ↓
Human review (existing — now enriched with acceptance data)
```

This runs ONCE per spec/phase completion — not per-WP, not during ratchet iterations.

### Acceptance review flow

```
Step 1: Spawn parallel acceptance agents (one per active story role)

  Each receives:
  - Their original perspective document (.ratchet/story/perspectives/{role}.md)
  - The PM synthesis document (what was agreed)
  - The actual built output (code, running app, API, etc.)
  - Proof of completion documents (.ratchet/{intent}/proofs/)
  - Verification results (.ratchet/{intent}/review_log.yaml)

  Each produces an acceptance review:
  
  .ratchet/{intent}/acceptance/
  ├── end-user.md
  ├── developer.md
  ├── devops.md
  ├── security.md
  └── qa-tester.md

Step 2: PM Acceptance Summary

  PM agent reads all acceptance reviews and produces:
  .ratchet/{intent}/acceptance/summary.md
  
  Contains:
  - Per-role satisfaction rating (satisfied / concerns / unsatisfied)
  - Gaps between what was asked and what was built
  - Issues that passed constraints but fail the spirit of the perspective
  - Recommendations for next iteration or future work
```

### Acceptance review document format (per-role)

```markdown
# [Role Name] Acceptance Review

## Original Requirements (from perspective document)
| Req ID | Requirement | Delivered? | Notes |
|--------|-------------|-----------|-------|
| REQ-1  | [requirement] | ✓ fully / △ partially / ✗ not delivered | [detail] |
| REQ-2  | [requirement] | ✓ / △ / ✗ | [detail] |

## Original Concerns — Addressed?
| Concern | Addressed? | How |
|---------|-----------|-----|
| CONCERN-1 | ✓ yes / ✗ no | [what was done or what's missing] |

## Experience Assessment
[2-3 paragraphs from this role's perspective: does the built product
actually deliver what this stakeholder needs? Not just "do tests pass"
but "would a real [role] be satisfied?"]

## Issues Found
- [issue]: [passed constraints but violates the perspective's intent]

## Satisfaction
Rating: satisfied | concerns | unsatisfied
Summary: [one sentence]
```

### PM Acceptance Summary format

```markdown
# PM Acceptance Summary

## Overall Assessment
[1-2 paragraphs: does the built product satisfy the unified requirements?]

## Per-Role Satisfaction
| Role | Rating | Key Gap |
|------|--------|---------|
| End User | satisfied | — |
| Developer | concerns | API pagination not implemented |
| DevOps | satisfied | — |
| Security | satisfied | — |
| QA | concerns | 2 boundary scenarios untested |

## Gaps (passed spec, failed perspective)
These items passed all constraints but were flagged by acceptance review:
1. [gap] — flagged by [role] — [recommendation]
2. [gap] — flagged by [role] — [recommendation]

## Recommendations
- [For next iteration]: [specific actionable items]
- [For future work]: [items that can wait]

## Verdict
Ready for human review: yes / yes with caveats / needs another iteration
```

### Integration with existing flow

```
If PM verdict = "needs another iteration":
  → Convert gaps into new constraints (with source: acceptance_review)
  → Trigger ratchet iteration on affected WPs
  → Re-verify
  → Re-run acceptance review (only for affected roles)

If PM verdict = "yes" or "yes with caveats":
  → Include acceptance summary in human review queue
  → User sees: test results + acceptance results + PM assessment
  → User makes final call
```

### What makes this different from verification

| Aspect | Verification (existing) | Acceptance Review (new) |
|--------|------------------------|------------------------|
| Checks against | Spec constraints (narrow) | Original perspectives (broad) |
| Evaluates | "Does the code satisfy the constraint?" | "Does the product satisfy the stakeholder?" |
| Timing | Per-WP, during ratchet loop | Once, after all WPs complete |
| Can trigger retry | Yes (ratchet loop) | Yes (if PM says "needs another iteration") |
| Finds | Constraint violations | Intent gaps, experience issues |
| Example | "API < 200ms" passes | "15 sequential calls = 3s" flagged |

### Files to modify
- `skills/verify/SKILL.md` — document acceptance review as post-verification step
- `skills/execute/SKILL.md` — trigger acceptance review after all WPs pass
- `skills/review/SKILL.md` — include acceptance summary in human review
- `agents/verifier.md` — document acceptance agents
- `references/spec-schema.md` — document acceptance review schemas
- `DESIGN.md` — update architecture to include acceptance review step

---

## Design Decisions

1. **Role agent model**: Individual perspective agents run on Sonnet (fast, cheap, focused). PM synthesis runs on Opus (deeper analysis, better conflict resolution). Manager agent on Opus.

2. **No direct role agent interaction**: Users cannot talk to individual role agents directly. Instead, users review perspective outputs and give feedback through the PM synthesis confirmation flow. The PM agent incorporates feedback and re-synthesizes. This keeps interaction simple while preserving the ability to influence any perspective.

3. **Cross-domain roles**: When we support domains beyond software development, how do role registries compose? A "data science" project might need both software dev roles and data-specific roles. (Open — future work.)

4. **Role memory**: Should role agents learn from past projects? e.g., "In the last 3 projects, the DevOps agent flagged logging — maybe this team has a pattern of neglecting observability." (Open — future work.)
