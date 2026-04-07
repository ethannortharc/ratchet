---
name: coverage
description: "Multi-layer coverage dashboard using DB queries and file cross-references. Shows story coverage, perspective coverage, scenario coverage, regression coverage, and backlog stats."
---

# Coverage — Multi-Layer Dashboard

## Data Sources

- Story scenarios: `.ratchet/story/scenarios.md`
- Perspectives: `.ratchet/story/perspectives/*.md`
- Regression manifest: `regression/manifest.yaml`
- DB backlog: `python tools/ratchet.py backlog stats`
- DB regression: `python tools/ratchet.py regression status`

## Layers

### Layer 1: User Story Coverage
Which user journey steps are implemented?

Cross-reference:
- `.ratchet/story/journey.md` for step list
- Work package completion status from DB

### Layer 1.5: Perspective Coverage
Which role perspectives are addressed by the implementation?

Cross-reference:
- `.ratchet/story/perspectives/*.md` for requirements per role
- `.ratchet/story/synthesis.md` for unified requirements with source_roles
- Work package completion status

Display:
```
Perspective Coverage:
  End User:    [N]/[total] requirements covered
  Developer:   [N]/[total] requirements covered
  DevOps:      [N]/[total] requirements covered
  Security:    [N]/[total] requirements covered
  QA:          [N]/[total] requirements covered
```

### Layer 2: Scenario Coverage
Which scenarios from the scenario table are tested?

Cross-reference:
- `.ratchet/story/scenarios.md` for scenario list
- `regression/manifest.yaml` for which scenarios have regression tests
- Sprint verification results from DB

### Layer 3: Test / Regression Coverage
Code-level verification and regression status.

Run: `python tools/ratchet.py regression status`

Shows:
- Total regression tests in manifest
- Tests passing / failing / not yet run
- Coverage gaps (scenarios without regression tests)

### Backlog Coverage

Run: `python tools/ratchet.py backlog stats`

Shows:
- Total backlog items by type and status
- Items blocked vs prioritized vs completed
- Bug vs improvement vs feature breakdown

## Display

```
Coverage Dashboard

Layer 1: User Story
  [N]/[total] journey steps implemented

Layer 1.5: Perspectives
  [role]: [N]/[total] requirements covered
  ...

Layer 2: Scenarios
  Normal:       [N]/[total] tested
  Interruption: [N]/[total] tested
  Boundary:     [N]/[total] tested

Layer 3: Regression
  [N]/[total] regression tests passing
  [N] scenarios without regression coverage

Backlog:
  [N] total items | [N] bugs | [N] improvements
  [N] blocked | [N] prioritized | [N] completed

Gaps:
  - [uncovered journey step or scenario]
  - [missing regression test for scenario X]
  - [recommended addition]
```

## Rules

1. **No story artifacts = limited view.** If no `.ratchet/story/` exists, show only Layer 3 and backlog stats. If no perspectives exist, skip Layer 1.5.
2. **Cross-reference, don't duplicate.** Read existing files, don't create new data.
3. **Highlight gaps.** The most valuable part is what's MISSING.
4. **Include out-of-scope.** Show excluded scenarios to confirm they're still intentionally excluded.
