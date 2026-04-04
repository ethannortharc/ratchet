# Intent Spec (spec.yaml) Schema Reference

## Complete Schema

```yaml
project:
  name: string              # kebab-case
  type: string              # software | creative_writing | research | design | general
  description: string
  created: datetime
  status: string            # See Intent Lifecycle below

spec_version: int            # Increments on every update
changelog:
  - version: int
    date: datetime
    source: string           # story_phase | human | agent_suggestion | review_feedback | user_request
    change: string
    story_updated: bool      # Whether story artifacts also changed
    added: [string]
    modified: [string]
    removed: [string]

environment:
  capabilities:
    - id: string
      type: string           # runtime | tool | agent | service
      version: string
      detected: bool
      enables: [string]
  absent:
    - id: string
      impact: string
      install_hint: string
      agent_can_install: bool

invariants:
  - id: string               # INV-01, INV-02, ...
    claim: string
    source: string            # Story artifact reference: "journey.md step 3" or "standalone"
    track: string             # agent | human
    confidence: string        # high | medium | low
    verifier: string          # auto | ai_review | human
    requires: [string]        # Capability IDs
    check: string             # Command or method to verify
    test_method: string       # Detailed test scenarios for agent
    tools_required:
      - id: string
        install: string
        agent_can_install: bool
    ratchet_metric: string
    fallback_verifier: string
    fallback_check: string

quality_dimensions:
  - id: string               # QD-01, QD-02, ...
    dimension: string
    source: string            # Story artifact reference or "standalone"
    track: string
    confidence: string
    verifier: string
    rubric: string            # 5/3/1 scoring
    threshold: number
    test_method: string
    tools_required:
      - id: string
        install: string
        agent_can_install: bool
    ratchet_metric: string

preferences:
  - string

decisions:
  human_must_decide:
    - string                  # Must be resolved before execution
  agent_can_decide:
    - string                  # Agent chooses, documents in proof
  unknown:
    - string                  # To be resolved — UX impact → human, technical → agent

delivery:                     # Conditional — only for projects with user-facing output
  format: string              # web_app | cli | desktop_app | document | api | library
  ui_direction:
    style: string
    key_screens:
      - name: string
        purpose: string
        elements: [string]
    user_journey: [string]
    mood: string
    anti_patterns: [string]
  cli_direction:
    interaction: string
    output_style: string

agent_guidance: string

ratchet:
  enabled: bool
  default_budget: int
  strategy: string            # keep_best | keep_last
  backend: string             # git | filesystem (auto-detected)
  composite_score:
    method: string            # weighted_average | single_metric
    weights:
      auto_pass_rate: float
      ai_review_avg: float

profile_applied:
  - key: string
    value: string
    source: string            # profile | project-override
```

## Story Artifact Schemas

### personas.md

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

Rules: 1-3 personas max. Behavioral patterns, not demographics.

### journey.md

```markdown
## Journey: [Persona Name]

1. [Phase Name]
   [Narrative paragraph: what user sees, does, feels.
    Include timing, UI elements, emotional beats.]

2. [Phase Name]
   [...]
```

Rules: Present tense, specific details, cover complete experience.

### scenarios.md

```markdown
## Scenarios

Normal:
  [check/empty] [scenario] -> [expected outcome]

Interruption:
  [check/empty] [scenario] -> [expected outcome]

Boundary:
  [check/empty] [scenario] -> [expected outcome]

Out of scope (explicitly excluded):
  [x] [feature/concern] -- [reason]
```

Rules: Check = confirmed, empty = unconfirmed, x = excluded. Out-of-scope is mandatory.

### mood.md

```markdown
## Visual Direction
Mood: [adjectives]
References: [sites/apps]
Anti-patterns: [things to avoid]

## Color Direction
[Palette direction]

## Typography Direction
[Font style, sizing]

## Layout Philosophy
[Mobile-first? Dense? Spacious?]
```

### prototype.html

Self-contained HTML file with:
- 3-5 key screens
- Inline CSS with actual colors and typography
- Click-through navigation
- Mobile viewport meta tag if applicable

### decisions.md

```markdown
## Decisions

### Confirmed by User
- [decision] (user confirmed [date])

### Agent Decided (technical, no user impact)
- [decision] -- [rationale]

### Open (needs user input)
- [question] -- [why it matters] -- [options]
```

### complexity.yaml

```yaml
total_estimate: int           # Story points
recommended_split: int        # Number of phases (1 = no split)
rationale: string

phases:                       # Only if recommended_split > 1
  - id: string               # phase-1, phase-2, ...
    name: string
    points: int
    includes: [string]
    depends_on: [string]
```

### Story Point Scale

```
1-5 points:    Trivial. Single WP, < 30 min agent time.
5-15 points:   Small. 2-4 WPs, < 2 hours. One spec, one session.
15-30 points:  Medium. 5-10 WPs. One spec, one session.
30-60 points:  Large. Must split into multiple phases.
60+ points:    Very large. Must split. Each phase < 30 points.
```

## Constraint Source Tracking

When story artifacts exist, each constraint tracks its source:

```yaml
invariants:
  - id: INV-01
    claim: "Progress preserved on browser close"
    source: "journey.md step 3: 'closes browser, returns, progress preserved'"
    # ...

  - id: INV-02
    claim: "Scoring produces results in < 2 seconds"
    source: "journey.md step 4: 'brief loading animation (<2 seconds)'"
    # ...

quality_dimensions:
  - id: QD-01
    dimension: "Visual consistency with prototype"
    source: "prototype.html, mood.md"
    # ...
```

For standalone specs (no story), source is `"standalone"`.

## Decision Classification

```yaml
decisions:
  human_must_decide:
    - "Tiebreak rule when types have equal scores"
    - "Wing calculation: adjacent types only or all types?"

  agent_can_decide:
    - "Internal data structure format"
    - "Function decomposition approach"
    - "CSS organization method"

  unknown:
    - "Share URL encoding format"
    - "Chart library choice"
```

Rules:
- `human_must_decide`: Must be resolved in story/spec phase. Block execution until answered.
- `agent_can_decide`: Agent chooses, documents in Proof of Completion.
- `unknown`: If UX impact → escalate to human. If technical → decide and document.

## Phase Structure (multi-phase projects)

### Phase in state.yaml

```yaml
intents:
  - id: lumina
    workspace: /path/to/project
    total_points: 55
    phases:
      - id: phase-1
        name: "Framework + Enneagram"
        points: 25
        status: done
        spec_version: 3
        completed_at: datetime

      - id: phase-2
        name: "MBTI"
        points: 18
        status: active
        spec_version: 1
        session_hint: "Start new session for this phase"

      - id: phase-3
        name: "IQ + polish"
        points: 12
        status: pending
        depends_on: [phase-1, phase-2]
```

### Per-Phase Files

```
.ratchet/phases/{phase-id}/
├── story/              # Phase-specific story subset
│   ├── journey.md      # Phase journey subset
│   ├── scenarios.md    # Phase scenarios
│   └── prototype.html  # Phase prototype
├── spec.yaml           # Phase-specific constraints
├── plan.yaml
├── test-suite/
├── proofs/
├── reports/
└── inputs.yaml         # "Assumes Phase N-1 delivered X, Y, Z"
```

### inputs.yaml

```yaml
assumed_deliverables:
  - phase: phase-1
    deliverable: "Landing page with test catalog"
    verified: true
  - phase: phase-1
    deliverable: "Enneagram scoring engine"
    verified: true
```

## Execution State (execution-state.yaml)

Persisted checkpoint for session resumption:

```yaml
intent: string
phase: string               # if multi-phase
checkpoint_at: datetime
work_packages:
  wp-01: done
  wp-02: done
  wp-03: running
  wp-04: pending
current_wp:
  id: string
  iteration: int
  best_score: float
  last_failure: string
ratchet_state:
  total_iterations: int
  total_commits: int
  total_resets: int
```

## Proof of Completion (proofs/wp-{id}.md)

```markdown
## WP-{id}: [Name] — Proof of Completion

### What I Built
- [files, functions, components]

### Design Decisions I Made (agent_can_decide)
- [decision] -- [rationale]

### Decisions You Already Confirmed (from story/spec)
- [decision] (confirmed in [story/spec] phase)

### Scenario Coverage
| Scenario | Input | Expected | Actual | Status |
|----------|-------|----------|--------|--------|
| ... | ... | ... | ... | pass/fail |

### What I Did NOT Cover (needs your judgment)
- [gap or question]

### How You Can Verify
1. [manual verification step]
```

## Global State Registry (~/.config/ratchet/state.yaml)

```yaml
intents:
  - id: string
    name: string
    workspace: string                    # Absolute path, locked at creation
    type: string
    status: string
    spec_version: int
    story_complete: bool                 # Whether story phase is confirmed
    total_points: int                    # Story point estimate
    phases: [phase]                      # If multi-phase (see Phase Structure)
    created: datetime
    last_activity: datetime
    priority: string                     # low | normal | high | urgent
    tags: [string]
    brief: string
    current_blocker: string
```

## Intent Lifecycle

### States

| State | Meaning |
|-------|---------|
| `draft` | Story or spec in progress, not yet confirmed |
| `active` | Intent Spec confirmed, plan exists or being created |
| `agent_running` | Agent is executing work packages with ratchet loop |
| `agent_complete` | All agent-track constraints pass, human items queued |
| `human_review` | Waiting for human to process review queue |
| `done` | All constraints verified, project complete |
| `paused` | User paused execution |
| `archived` | User archived (hidden from active views) |

### State Transitions

```
draft → active          : User confirms Intent Spec
active → agent_running  : Plan created, execution starts
agent_running → agent_complete : All agent-track pass (or budget exhausted)
agent_complete → human_review  : Human items queued
human_review → agent_running   : Human feedback triggers spec update + new round
human_review → done            : All human reviews pass
any → paused                   : User runs /ratchet:pause
paused → active                : User runs /ratchet:resume
any → archived                 : User archives
```

## Test Suite Structure (.ratchet/{intent-id}/test-suite/)

Generated automatically after Intent Spec confirmation, before planning.

```
.ratchet/{intent-id}/test-suite/
├── manifest.yaml          # Maps constraint IDs to test files
├── INV-01.test.ts         # or .py, .go — auto verifier test
├── INV-02.test.ts
├── QD-01.review.md        # Structured review prompt for ai_review
├── QD-02.checklist.md     # Review checklist for human verifier
└── ...
```

### manifest.yaml schema

```yaml
generated: datetime
spec_version: int
project_type: string
test_runner: string        # vitest | pytest | go test | etc.
entries:
  - constraint_id: string
    type: string            # auto | ai_review | human
    file: string
    status: string          # generated | modified | skipped
    reason: string
```

## Track Assignment Rules

- `track: agent` → constraint drives the ratchet loop, verified without human
- `track: human` → queued for async review, does NOT block agent execution
- Default to `agent` unless genuinely subjective with no automated proxy

## Verifier Priority

`auto` > `ai_review` > `human` — always use the most automated option available.

## test_method Guidelines

The `test_method` field describes WHAT to test in enough detail for the agent to generate a test suite. It is NOT the check command — it's the test design.

Examples:

```yaml
# Invariant — scoring logic
test_method: |
  Unit tests covering:
  - All perfect-score scenarios (one type maxed out)
  - Tied scores with tiebreak logic
  - Boundary cases (minimum/maximum inputs)
  - Invalid input handling (missing answers, out-of-range values)

# Quality dimension — description quality
test_method: |
  AI review evaluates each type description against rubric:
  - Accuracy: matches established definitions
  - Tone: empathetic, non-judgmental
  - Actionability: includes growth suggestions
  - Length: 150-300 words per type
```

## tools_required Guidelines

Each entry is a structured object with install info:

```yaml
tools_required:
  - id: vitest
    install: "npm install -D vitest"
    agent_can_install: true

  - id: go-test
    install: "built-in with Go"
    agent_can_install: false
```

## agent_guidance Guidelines

Natural language prompt giving the agent project-specific context and constraints. References story decisions and mockup when available.

## Ratchet Metric Guidelines

Every constraint should have a `ratchet_metric` that is continuous (not just pass/fail):
- auto test: "passed_tests / total_tests" (0.0 to 1.0)
- ai_review: rubric score (1 to 5)
- word count: "abs(actual - target) / target" (0.0 = perfect)
- coverage: "covered / total" (0.0 to 1.0)
