---
name: update
description: "Process modifications to an existing intent. Detects whether change is story-level or spec-level, cascades through the full chain: story update → spec re-derivation → test update → execution → verification. Automatically increments spec version and triggers re-execution."
---

# Update — Modification Chain

## Usage

Invoked automatically when user describes changes to an existing project in conversation. Can also be invoked directly:

```
/ratchet:update "add markdown export feature"
/ratchet:update prism "tighten test coverage to 90%"
```

## Workspace Resolution

1. If intent ID provided as first argument → use that intent's workspace
2. If current directory is inside a registered workspace → use that intent
3. If ambiguous → ask user to choose

## Change Classification

Determine what level the change affects:

### Story-Level Change
User describes something that changes the product experience:
- "Add growth advice to the results page"
- "Support dark mode"
- "Let users share via WeChat"

These changes cascade through the FULL chain.

### Spec-Level Change
User describes a constraint or technical requirement:
- "Tighten test coverage to 90%"
- "Search must complete in < 200ms"
- "Don't use external dependencies"

These start at spec and cascade from there.

### Direct Fix
User describes a specific bug or issue:
- "Fix the encoding error on the results page"
- "The share button doesn't work"

These are handled directly — fix, add regression test, verify. No story/spec change needed.

## Story-Level Change Chain

```
User: "Add growth advice to the results page"

1. Update story artifacts
   → journey.md: add "reads growth advice" to results step
   → scenarios.md: add "growth advice relevant to type" scenario
   → decisions.md: log the change with user confirmation

2. Re-derive affected spec constraints
   → New INV: "each type has growth advice section"
   → New QD: "growth advice quality" (ai_review)
   → spec_version: v[N] → v[N+1]
   → changelog: {source: user_request, story_updated: true}

3. Update test suite
   → Generate new test files for new constraints
   → Update manifest.yaml

4. Execute the change
   → Plan new WP(s) for the new work
   → Execute with ratchet loop

5. Full verification (ALL tests, not just new ones)
   → Ensures new feature didn't break anything

6. Generate proof of completion for the change

7. Update coverage dashboard data
```

## Spec-Level Change Chain

```
User: "Search must complete in < 200ms"

1. Update spec.yaml
   → Add/modify constraint
   → spec_version: v[N] → v[N+1]
   → changelog: {source: user_request, story_updated: false}

2. Update test suite
   → Generate/update test files

3. Execute + verify (same as above)
```

## Workflow

1. Load current `.ratchet/{intent-id}/spec.yaml` and story artifacts (if they exist)
2. Analyze the user's update request
3. Classify: story-level, spec-level, or direct fix
4. For story-level changes:
   a. Update affected story artifacts
   b. Show what changed in story
   c. Re-derive spec constraints from updated story
   d. Show new/modified constraints
   e. Get user confirmation
5. For spec-level changes:
   a. Add/modify constraints directly
   b. Show diff to user for confirmation
6. On confirmation:
   a. Increment `spec_version`, append to `changelog`
   b. Regenerate affected test files in `.ratchet/{intent-id}/test-suite/`
   c. If plan.yaml exists, add new WPs or re-plan
   d. Trigger execution and full verification
7. Update `last_activity` in `~/.config/ratchet/state.yaml`

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
  tools_required:
    - id: [project-test-runner]
      install: "[install command]"
      agent_can_install: true

This was originally a human observation but is now machine-verifiable.
```

Always show the conversion and ask if it captures what they meant.

## Rules

1. **Detect the level.** Story changes cascade through everything. Spec changes skip story. Direct fixes skip both.
2. **Full verification after any change.** ALL tests, not just new ones.
3. **Show what changed.** Before executing, show the user what artifacts were modified.
4. **Don't regenerate from scratch.** Incrementally patch story/spec — preserve existing work.
5. **Update decision log.** Any new decisions during update go into decisions.md.
6. **Proof of completion.** New WPs from updates get proof documents too.
