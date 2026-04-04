---
name: story
description: "Phase 1: Align human understanding through narrative and concrete examples before specification. Produces personas, user journey, scenario coverage, visual mood + prototype, and decision log. Supports both initial creation and incremental updates. Auto-transitions to spec phase on confirmation."
---

# Story — Human-Language Alignment (Phase 1)

## Overview

Story is Phase 1 — before spec, before code, before constraints. It answers "what are we building and for whom?" in human language, through narrative and examples.

```
User: /ratchet:story "Build an Enneagram test website called Lumina"

Agent: generates story artifacts from intent + domain knowledge
Agent: asks clarifying questions about key decisions
User:  answers, agent updates artifacts
Agent: generates scenario table, user reviews
Agent: generates prototype, user clicks through
User:  "This is what I want."

=== Story phase complete → auto-transition to Spec ===
```

The spec phase then reads these confirmed artifacts and auto-extracts machine-verifiable constraints. Most of the hard alignment work happens here in story, not in spec.

---

## When to Use

- **New intent**: Always start with `/ratchet:story` for any non-trivial project
- **Standalone spec**: `/ratchet:spec` still works directly for simple projects or when the user already has a clear spec in mind
- **Updates**: User describes changes to an existing project → agent routes here for story-level updates, then cascades to spec

## Artifacts

Story phase produces five artifacts in `.ratchet/story/` (flat project) or `.ratchet/phases/{phase-id}/story/` (multi-phase):

| Artifact | File | Purpose |
|----------|------|---------|
| Personas | `personas.md` | Who are we building for? Behavioral patterns, not demographics |
| Journey | `journey.md` | Narrative walkthrough of the complete experience |
| Scenarios | `scenarios.md` | Happy path + edge cases + out-of-scope exclusions |
| Mood + Prototype | `mood.md` + `prototype.html` | Visual direction and clickable skeleton |
| Decisions | `decisions.md` | Every decision made, classified and tracked |

---

## Step 1: Analyze Intent

### 1.1 Load Profile
Check `~/.config/ratchet/profile.yaml`. If missing, ask 3 quick preference questions and create it.

### 1.2 Domain Research
For domain-specific projects (personality tests, financial tools, medical apps, educational platforms), research the domain BEFORE generating story artifacts:

1. Identify what domain knowledge shapes the user experience (scoring methods, best practices, common pitfalls)
2. Spawn research subagent(s) to gather this knowledge
3. Use findings to write accurate, specific personas and journey

**Skip** if the domain is generic (CRUD app, landing page, CLI tool) or agent has sufficient knowledge.

### 1.3 Register Intent
If this is a new intent (not an update):

```
Intent ID? [auto-generated from name, user can override]
Workspace? [current dir / create new / custom path]
```

Register in `~/.config/ratchet/state.yaml` with status: `draft`.

---

## Step 2: Generate Story Artifacts

Generate all five artifacts from the user's intent description + domain research. Present them for review.

### 2.1 Personas (.ratchet/story/personas.md)

Who are we building for? Focus on behavioral patterns and expectations, not demographics.

```markdown
## Primary User: [Name/Role]
- How they discover the product
- What they know/don't know
- What makes them leave
- What makes them stay
- Device/context of use

## Secondary User: [Name/Role]
- ...
```

**Rules:**
- 1-3 personas max. More is noise.
- Focus on behaviors that affect product decisions
- Each persona should imply different design trade-offs

### 2.2 User Journey (.ratchet/story/journey.md)

A narrative walkthrough written as a story, not a feature list. Each step is a moment in the user's experience.

```markdown
## Journey: [Persona Name]

1. [Phase Name]
   [Narrative paragraph describing what the user sees, does, feels.
    Include specific UI elements, timing expectations, emotional beats.]

2. [Phase Name]
   [...]
```

**Rules:**
- Write in present tense, specific details
- Include timing expectations ("< 2 seconds", "~5 minutes")
- Name specific UI elements and interactions
- Cover the COMPLETE experience from discovery to completion
- Each step should implicitly define product decisions

### 2.3 Scenario Coverage (.ratchet/story/scenarios.md)

The journey covers the happy path. This covers everything else.

```markdown
## Scenarios

Normal:
  [check] [scenario] -> [expected outcome]
  [check] [scenario] -> [expected outcome]

Interruption:
  [check] [scenario] -> [expected outcome]
  [empty] [scenario] -> [expected outcome] (acceptable)

Boundary:
  [empty] [scenario] -> [expected outcome]
  [empty] [scenario] -> [expected outcome]

Out of scope (explicitly excluded):
  [x] [feature/concern] -- [reason]
  [x] [feature/concern] -- [reason]
```

**Rules:**
- Use checkmarks for confirmed scenarios, empty boxes for unconfirmed
- The "out of scope" section is critical — prevents agent from over-engineering
- Include at least 3 boundary scenarios
- Include at least 2 out-of-scope exclusions

### 2.4 Visual Mood (.ratchet/story/mood.md)

For projects with user-facing interface:

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

For non-UI projects, skip this artifact.

### 2.5 Interactive Prototype (.ratchet/story/prototype.html)

For projects with user-facing interface, generate a clickable HTML prototype:

- 3-5 key screens with real layout and placeholder data
- Inline CSS with actual colors, typography, spacing (not wireframes)
- Click-through navigation between screens
- Mobile viewport meta tag for mobile projects
- Self-contained — no external dependencies

Open with: `open .ratchet/story/prototype.html`

**This is NOT the final product** — it's a skeleton for direction confirmation. The spec phase's mockup (Step 2.5 in spec skill) provides the more polished visual reference.

For non-UI projects (CLI, library, API), skip this artifact.

### 2.6 Decision Log (.ratchet/story/decisions.md)

Every decision made during story phase, classified:

```markdown
## Decisions

### Confirmed by User
- [decision] (user confirmed [date])
- [decision] (user confirmed [date])

### Agent Decided (technical, no user impact)
- [decision] -- [rationale]

### Open (needs user input)
- [question] -- [why it matters] -- [options]
```

**Rules:**
- Every decision gets a classification
- User-confirmed decisions reference the confirmation
- Open decisions must be resolved before story phase completes
- Agent decisions document rationale

---

## Step 3: Present and Iterate

### 3.1 Present All Artifacts

After generating, present a summary:

```
Story artifacts generated for [project name]:

1. Personas: [N] personas defined ([names])
2. Journey: [N]-step journey for [primary persona]
3. Scenarios: [N] normal, [N] interruption, [N] boundary, [N] excluded
4. Mood: [mood adjectives], prototype at .ratchet/story/prototype.html
5. Decisions: [N] confirmed, [N] agent-decided, [N] open

Open questions I need your input on:
1. [question from decisions.md]
2. [question from decisions.md]
3. [question from decisions.md]
```

### 3.2 Ask Clarifying Questions

Surface all `human_must_decide` items from the decision log. These are decisions that fundamentally change the product — present as multiple-choice when possible.

**Rules:**
- Group related questions together
- Multiple choice preferred, one message with all questions
- Only ask about things that affect the user experience
- Never ask about technical implementation details

### 3.3 Iterate on Feedback

User may:
- Answer questions → update decisions.md, regenerate affected artifacts
- Modify personas → update journey and scenarios accordingly
- Modify journey → update scenarios
- Request prototype changes → regenerate prototype
- Add/remove scenarios → update scenarios.md
- Change mood direction → regenerate mood.md and prototype

Each change cascades through dependent artifacts. Always show what changed.

### 3.4 Prototype Review

If a prototype was generated, prompt the user to open and click through:

```
Open the prototype and click through the flow:
file://[absolute-path]/.ratchet/story/prototype.html

Tell me what to change — layout, sizing, colors, flow.
```

Iterate on prototype feedback until user approves.

---

## Step 4: Complexity Estimation

After all artifacts are confirmed, estimate complexity:

### 4.1 Story Point Estimation

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

### 4.2 Auto-Split (if > 30 points)

If total > 30 points, propose a phase split:

```
This is a ~[N] point project. I recommend splitting into [N] phases:

Phase 1: [name] ([N] pts)
Phase 2: [name] ([N] pts)
Phase 3: [name] ([N] pts)

Each phase gets its own spec and runs in a fresh session.
OK with this split? Want to adjust?
```

On confirmation, create phase structure:
```
.ratchet/
├── story/                      # Top-level story (big picture)
│   ├── personas.md
│   ├── journey.md              # Full journey across all phases
│   ├── scenarios.md            # All scenarios
│   ├── complexity.yaml         # Estimate + phase split
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

## Step 5: Confirm and Transition

### 5.1 Final Confirmation

```
Story phase complete. All artifacts confirmed:
  - [N] personas
  - [N]-step journey  
  - [N] scenarios ([N] normal, [N] boundary, [N] excluded)
  - Visual mood confirmed, prototype approved
  - [N] decisions resolved, [N] agent-decided

Ready to generate the Intent Spec from these artifacts?
```

### 5.2 Transition to Spec

On confirmation:
1. Mark story phase as complete in state
2. **Auto-invoke the spec skill** — do not wait for user to call `/ratchet:spec`
3. Spec phase reads `.ratchet/story/` artifacts as input (see Change 15 in spec skill)

### 5.3 Session Boundary (for phases)

If the project was split into phases:
- Generate Phase 1 story artifacts
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
2. Update the artifacts (don't regenerate from scratch)
3. Show what changed
4. Cascade: story update → spec re-derivation → test update → execution → full verification
5. Update decision log with new decisions

```
User: "Add growth advice to the results page"

Agent detects: story-level change.
1. Update journey.md → add "reads growth advice" to results step
2. Update scenarios.md → add "growth advice relevant to type" scenario
3. Update decisions.md → log the change
4. Cascade to spec (re-derive affected constraints)
```

---

## Rules

1. **Story before spec.** For non-trivial projects, always generate story artifacts before converting to constraints.
2. **Human language only.** No YAML, no test methods, no constraint IDs in story artifacts. Those come in spec.
3. **Out of scope is mandatory.** Every scenario table must have an explicit out-of-scope section.
4. **Iterate until confirmed.** No time limit. The investment here saves rework later.
5. **Decisions are classified.** Every decision is either user-confirmed, agent-decided (with rationale), or open.
6. **Prototype is a skeleton.** Not the final product — direction confirmation only.
7. **Cascade updates.** Any story change flows through to spec, tests, and execution.
8. **Domain research first.** For domain-specific projects, research before writing personas and journey.
9. **Complexity estimation.** Always estimate story points. Split if > 30 points.
