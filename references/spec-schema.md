# Intent Spec (spec.yaml) Schema Reference

## Complete Schema

```yaml
project:
  name: string              # kebab-case
  type: string              # software | creative_writing | research | design | general
  description: string
  created: datetime
  status: string            # draft | active | completed | archived

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
    tools_required: [string]  # Specific tools needed (e.g. vitest, pytest, golangci-lint)
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
    tools_required: [string]  # Tools needed for evaluation
    ratchet_metric: string

preferences:
  - string

exploration_hints:            # Directions for agent when stuck
  - string

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

List specific tools the constraint needs. These are deduplicated into `environment.capabilities` during spec generation.

```yaml
tools_required: [vitest]           # JS/TS testing
tools_required: [pytest, mypy]     # Python testing + type checking
tools_required: [golangci-lint]    # Go linting
tools_required: []                 # ai_review or human — no tools needed
```

## Ratchet Metric Guidelines

Every constraint should have a `ratchet_metric` that is continuous (not just pass/fail):
- auto test: "passed_tests / total_tests" (0.0 to 1.0)
- ai_review: rubric score (1 to 5)
- word count: "abs(actual - target) / target" (0.0 = perfect)
- coverage: "covered / total" (0.0 to 1.0)

This lets the ratchet detect improvement even when a constraint isn't fully passing yet.
