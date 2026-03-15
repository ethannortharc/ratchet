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
    source: string           # human | agent_suggestion | review_feedback
    change: string
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
    track: string             # agent | human
    confidence: string        # high | medium | low
    verifier: string          # auto | ai_review | human
    requires: [string]        # Capability IDs
    check: string             # Command or method to verify
    test_method: string       # Detailed test scenarios for agent (what to test, edge cases, expected behaviors)
    tools_required:           # Structured tool requirements
      - id: string            # e.g. vitest, pytest, golangci-lint
        install: string        # Install command or "built-in"
        agent_can_install: bool
    ratchet_metric: string    # Quantified progress (e.g. "pass_rate", "score")
    fallback_verifier: string
    fallback_check: string

quality_dimensions:
  - id: string               # QD-01, QD-02, ...
    dimension: string
    track: string
    confidence: string
    verifier: string
    rubric: string            # 5/3/1 scoring
    threshold: number
    test_method: string       # How to evaluate this dimension (rubric application, artifacts to review)
    tools_required:           # Structured tool requirements
      - id: string
        install: string
        agent_can_install: bool
    ratchet_metric: string

preferences:
  - string

agent_guidance: string        # Natural language prompt for the agent — context, constraints, what to do when stuck
                              # Replaces the flat exploration_hints list with a richer, more natural format

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

## Global State Registry (~/.config/ratchet/state.yaml)

```yaml
intents:
  - id: string                          # Unique identifier (kebab-case, auto-generated from name)
    name: string                         # Human-readable name
    workspace: string                    # Absolute path, locked at creation
    type: string                         # software | creative_writing | research | design | general
    status: string                       # See Intent Lifecycle below
    spec_version: int
    created: datetime
    last_activity: datetime
    # Ticket-like fields:
    priority: string                     # low | normal | high | urgent
    tags: [string]
    brief: string                        # One-line summary
    current_blocker: string              # null, or description of what's blocking (e.g. "human review needed for QD-02")
```

## Intent Lifecycle

### States

| State | Meaning |
|-------|---------|
| `draft` | Intent Spec exists but not yet confirmed |
| `active` | Intent Spec confirmed, plan exists or being created |
| `agent_running` | Agent is executing work packages with ratchet loop |
| `agent_complete` | All agent-track constraints pass, human items queued |
| `human_review` | Waiting for human to process review queue |
| `done` | All constraints (agent + human) verified, project complete |
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

## Test Suite Structure (.ratchet/test-suite/)

Generated automatically after Intent Spec confirmation, before planning.

```
.ratchet/test-suite/
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
  - constraint_id: string  # INV-01, QD-01, etc.
    type: string            # auto | ai_review | human
    file: string            # Relative path to test file
    status: string          # generated | modified | skipped
    reason: string          # If skipped, why
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

# Invariant — page load
test_method: |
  Integration test:
  - Page renders without errors
  - All critical elements present (header, question area, progress bar)
  - No console errors
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

  - id: golangci-lint
    install: "go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest"
    agent_can_install: true
```

Tools are deduplicated into `environment.capabilities` during spec generation.

## agent_guidance Guidelines

The `agent_guidance` field is a natural language prompt giving the agent project-specific context, constraints, and direction:

```yaml
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

This replaces the old `exploration_hints` list with a richer, more natural format. It serves as the "agent prompt" for this intent — policy and constraints in one place.

## Ratchet Metric Guidelines

Every constraint should have a `ratchet_metric` that is continuous (not just pass/fail):
- auto test: "passed_tests / total_tests" (0.0 to 1.0)
- ai_review: rubric score (1 to 5)
- word count: "abs(actual - target) / target" (0.0 = perfect)
- coverage: "covered / total" (0.0 to 1.0)

This lets the ratchet detect improvement even when a constraint isn't fully passing yet.
