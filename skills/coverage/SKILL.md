---
name: coverage
description: "Three-layer coverage dashboard: user story coverage, scenario coverage, and test coverage. Cross-references story artifacts, scenario table, test suite, and verification results. Workspace-aware — accepts optional intent ID."
---

# Coverage — Three-Layer Dashboard

## Workspace Resolution

1. If intent ID provided → look up workspace in `~/.config/ratchet/state.yaml`
2. If current directory is inside a registered workspace → use that intent
3. If ambiguous → ask user to choose

## Three Layers

### Layer 1: User Story Coverage
Which user journey steps are implemented?

Cross-reference:
- `.ratchet/story/journey.md` (or `.ratchet/phases/{phase}/story/journey.md`) → step list
- Work package status from plan.yaml → which steps are covered by completed WPs

### Layer 2: Scenario Coverage
Which scenarios from the scenario table are tested?

Cross-reference:
- `.ratchet/story/scenarios.md` → scenario list
- `.ratchet/{intent-id}/test-suite/manifest.yaml` → which scenarios have tests
- `.ratchet/{intent-id}/review_log.yaml` → test results

### Layer 3: Test Coverage
Code-level verification coverage.

Cross-reference:
- Test suite results from review_log.yaml
- Code coverage tool output (if available)
- AI review scores
- Human review status

## Display

```
Coverage Dashboard — [intent-name]

Layer 1: User Story
  [N]/[total] journey steps implemented
  [visual bar or list showing coverage]

Layer 2: Scenarios
  Normal:       [N]/[total] tested
  Interruption: [N]/[total] tested
  Boundary:     [N]/[total] tested

Layer 3: Tests
  Auto:      [N]/[total] passing
  AI Review: [N]/[total] passing (avg score: [X])
  Human:     [N]/[total] reviewed

Gaps:
  - [uncovered journey step or scenario]
  - [missing test for scenario X]
  - [recommended addition]
```

## HTML Report

For projects with many scenarios (>20), generate `.ratchet/{intent-id}/coverage-report.html`:
- Self-contained HTML with expandable sections
- Color-coded status (green/yellow/red)
- Progress bars per layer
- Open in browser for better readability

## Rules

1. **No story artifacts = limited view.** If no `.ratchet/story/` exists, show only Layer 3 (test coverage).
2. **Cross-reference, don't duplicate.** Read existing files, don't create new data.
3. **Highlight gaps.** The most valuable part is what's MISSING.
4. **Include out-of-scope.** Show excluded scenarios to confirm they're still intentionally excluded.
