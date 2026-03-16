# Ratchet Plugin — Change Specification v3

Read DESIGN.md and ratchet-changes-v2.md first for full context.
This document covers changes discussed AFTER v2 was implemented.

## Change 9: Minimize Human Touchpoints

Human interacts at exactly two points: **spec** (provide direction) and **review** (evaluate results). Everything between runs autonomously.

After user confirms spec, agent automatically chains: environment preparation → test suite generation → validation dry-run → plan decomposition → work package execution with ratchet loop → iteration report → queue human-track items → notify user.

**User-facing commands (keep):**
- `/ratchet:spec` — Start new intent
- `/ratchet:review` — Process human review queue  
- `/ratchet:status` — Optional progress check

**Internal-only skills (remove from user-facing commands):**
- plan, verify, report, metrics, update — agent calls these internally, user doesn't need to invoke them. User just says "change X" in conversation for updates.

Files: plugin.json (remove commands), getting-started (simplify), spec (add auto-chaining), DESIGN.md, README.md.

## Change 10: Spec Includes Delivery/UI Direction

Add `delivery` section to spec schema:

```yaml
delivery:
  format: web_app | cli | desktop_app | document | api | library
  ui_direction:
    style: string
    reference_sites: [string]
    layout: string
    key_screens: [{name, description}]
    mood: string
    anti_patterns: [string]
  cli_direction:
    interaction: string
    output_style: string
```

For UI projects, generate 1-2 mockups before spec confirmation so user can validate visual direction early. Add QD-UI-01 (ai_review: visual consistency with spec) and QD-UI-02 (human: overall taste).

Files: spec-schema.md, spec SKILL.md, spec-template.yaml.

## Change 11: Spec Confirmation is Thorough, Not Quick

Remove "max 3 questions, 5 minutes" rule. Spec phase is the highest-ROI human time investment.

Implement **grouped confirmation**: agent generates full spec, presents in collapsible groups. User can confirm whole groups at once ("基础方向全部 OK") or drill into individual items. ⚠️ marks on low-confidence items. No limit on constraint count — if project needs 100, show 100.

For specs with >20 constraints, auto-generate `.ratchet/spec-review.html` — self-contained HTML file opened in browser. Shows grouped constraints, embedded mockups for UI projects, modification inputs, and "Approve & Start" button (writes `.ratchet/approved` file that agent detects).

For specs with ≤20 constraints, conversational confirmation in Claude Code is sufficient.

Files: spec SKILL.md (remove question limit, add grouped confirmation, add HTML generation), DESIGN.md.

## Change 12: Verification Infrastructure Pre-validation (EVA Principle)

After spec confirmation, before plan, validate that ALL verification infrastructure works. Four steps:

**Step 1: Environment preparation** — install tools_required, verify installations.

**Step 2: Test suite generation** — from each constraint's test_method, create concrete files in `.ratchet/test-suite/`:
```
.ratchet/test-suite/
├── auto/           # Executable test scripts
├── ai-review/      # Structured review prompts  
├── human/          # Review checklists
└── manifest.yaml   # Constraint ID → test file mapping
```

**Step 3: Empty test validation** — run test framework with minimal content to verify the FRAMEWORK ITSELF works (npm test doesn't crash, build tool exists, etc).

**Step 4: Scaffold validation** — create minimal project scaffold, run full verification chain (build, serve, test runner). Fix failures HERE, not during execution.

Output: `.ratchet/pre-validation.log`

Files: spec SKILL.md (add pre-validation steps), verify SKILL.md (reference test suite), DESIGN.md.

## Change 13: Subagent Architecture

Create `agents/` directory with specialized subagents:

**agents/env-preparer.md** (Sonnet) — Install tools, validate environment, run scaffold validation. Allowed tools: Bash, Read, Write.

**agents/test-generator.md** (Sonnet) — Generate test suite files from spec test_method fields. Allowed tools: Read, Write, Bash.

**agents/wp-executor.md** (Sonnet) — Execute single work package within workspace boundary. Allowed tools: Read, Write, Edit, Bash, Grep, Glob.

**agents/verifier.md** (Sonnet) — Run three-tier verification, calculate composite score for ratchet decisions. Allowed tools: Read, Bash, Grep, Write.

**agents/report-writer.md** (Haiku) — Generate iteration reports with proof of work from logs and test outputs. Allowed tools: Read, Write, Grep.

**Orchestration after spec confirmation:**
```
1. Parallel: env-preparer + test-generator (both Sonnet)
2. Main agent: validate test infrastructure
3. Main agent: generate plan (needs global view)
4. Per parallel group: spawn N wp-executor subagents
   Each: execute → spawn verifier → improved? keep : discard → repeat until pass or budget
5. Spawn report-writer (Haiku)
6. Queue human-track → notify user
```

**Cost optimization:** wp-executor and verifier on Sonnet (focused tasks), report-writer on Haiku (just summarizing), main orchestrator on whatever model user's session runs (ideally Opus).

Files: create agents/ directory with 5 .md files, plugin.json (add agents path), getting-started SKILL.md, spec SKILL.md (orchestration flow), DESIGN.md.

## Implementation Priority

1. Change 9 (minimize touchpoints) — biggest UX win
2. Change 13 (subagents) — enables parallel execution
3. Change 12 (pre-validation) — catches problems early
4. Change 11 (thorough spec) — better spec = less rework
5. Change 10 (delivery/UI) — important for UI projects

## Updated Complete User Experience

```
Human: /ratchet:spec "做一个在线心理测试网站叫 Prism"

[2-3 intent-level branching questions]
Human: "纯前端、中文、先做九型人格"

[Agent generates complete Intent Spec with delivery/UI direction]
[For UI projects: generates mockup]
[Presents grouped confirmation — user confirms/adjusts groups]
Human: "90题改45题，其他都OK"

[Agent updates spec]
[If >20 constraints: opens spec-review.html in browser]
[If ≤20: confirms in conversation]
Human: "确认，开始吧"

=== Human walks away ===

[env-preparer subagent + test-generator subagent run in parallel]
[Pre-validation: empty tests pass, scaffold builds]
[Plan generated]
[wp-executor subagents execute WPs with ratchet loop]
[verifier subagents check each iteration]
[report-writer generates iteration report]
[Human-track items queued]

=== Agent notifies: "Ready for review" ===
Human: /ratchet:review

[Shows review queue with proof of work]
[Human gives feedback: "search feels slow"]
[Agent converts to auto constraint: "search < 200ms"]
[Spec v1 → v2, new iteration round starts]

Human: /ratchet:review (round 2)

[All pass]
Human: "looks good"

=== Done ===

Total human time: ~35 min spec + ~10 min review = 45 min
Total agent time: hours of autonomous execution
Autonomy ratio: 90%+
```

## Core Philosophy (final form)

> Human provides direction and taste.
> Agent does everything else.
> Agent creates conditions to do more.
> What truly cannot be automated, human reviews.
> Each review makes the next project more autonomous.
