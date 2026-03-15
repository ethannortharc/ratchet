---
name: update
description: Update a project's spec mid-execution. Add constraints, modify thresholds, add exploration hints, or change direction. Automatically increments spec version and triggers a new iteration round. Use when the user says "add feature", "change requirement", "I also want", or provides feedback that should become a permanent constraint.
---

# Update — Mid-Project Spec Changes

## Usage

```
/ratchet:update "add markdown export feature"
/ratchet:update "tighten test coverage to 90%"
/ratchet:update "don't use external dependencies for this"
```

## Workflow

1. Load current `.ratchet/spec.yaml`
2. Analyze the user's update request
3. Determine what changes:
   - New invariant? → add with track + verifier
   - Modified threshold? → update quality_dimension
   - New exploration hint? → append to hints
   - New feature? → add constraints + will need new WP in plan
4. Show diff to user for confirmation
5. Increment `spec_version`, append to `changelog`
6. If plan.yaml exists, flag that `/ratchet:plan` should be re-run to add new WPs
7. If agent is running, the next iteration will pick up the new spec version

## Converting Human Feedback to Agent Constraints

When the user's update is subjective ("search feels slow", "code is messy"), try to convert it:

```
User: "search feels slow"
→ INV-new: "Search completes in < 200ms for 1000 notes"
  track: agent, verifier: auto
  check: "benchmark search latency"
  
This was originally a human observation but is now machine-verifiable.
```

Always show the conversion and ask if it captures what they meant.
