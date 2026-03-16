---
name: update
description: Update a project's Intent Spec mid-execution. Add constraints, modify thresholds, change agent_guidance, or change direction. Automatically increments spec version, regenerates affected test files, and triggers a new iteration round. Workspace-aware — accepts optional intent ID.
---

# Update — Mid-Project Intent Spec Changes

## Usage

```
/ratchet:update "add markdown export feature"
/ratchet:update prism "tighten test coverage to 90%"
/ratchet:update "don't use external dependencies for this"
```

## Workspace Resolution

1. If intent ID provided as first argument → use that intent's workspace
2. If current directory is inside a registered workspace → use that intent
3. If ambiguous → ask user to choose

## Workflow

1. Load current `.ratchet/spec.yaml` (Intent Spec) from resolved workspace
2. Analyze the user's update request
3. Determine what changes:
   - New invariant? → add with track + verifier + test_method + tools_required
   - Modified threshold? → update quality_dimension
   - Agent guidance change? → update agent_guidance section
   - New feature? → add constraints + will need new WP in plan
4. Show diff to user for confirmation
5. Increment `spec_version`, append to `changelog`
6. **Regenerate affected test files** in `.ratchet/test-suite/` and update manifest
7. If plan.yaml exists, flag that `/ratchet:plan` should be re-run to add new WPs
8. If agent is running, the next iteration will pick up the new spec version
9. Update `last_activity` in `~/.config/ratchet/state.yaml`

## Converting Human Feedback to Agent Constraints

When the user's update is subjective ("search feels slow", "code is messy"), try to convert it:

```
User: "search feels slow"
→ INV-new: "Search completes in < 200ms for 1000 notes"
  track: agent, verifier: auto
  check: "benchmark search latency"
  test_method: |
    Benchmark test: index 1000 notes, measure search latency
    across 10 representative queries. P95 must be < 200ms.
  tools_required:                        # use the project's actual test runner
    - id: [project-test-runner]
      install: "[install command]"
      agent_can_install: true

This was originally a human observation but is now machine-verifiable.
```

Always show the conversion and ask if it captures what they meant.
