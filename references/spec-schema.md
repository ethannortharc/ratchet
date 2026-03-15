# spec.yaml Schema Reference

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
    check: string
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

## Ratchet Metric Guidelines

Every constraint should have a `ratchet_metric` that is continuous (not just pass/fail):
- auto test: "passed_tests / total_tests" (0.0 to 1.0)
- ai_review: rubric score (1 to 5)
- word count: "abs(actual - target) / target" (0.0 = perfect)
- coverage: "covered / total" (0.0 to 1.0)

This lets the ratchet detect improvement even when a constraint isn't fully passing yet.
