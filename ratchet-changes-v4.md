# Ratchet Plugin — Change Specification v4

Read DESIGN.md, ratchet-changes-v2.md, and ratchet-changes-v3.md first.
This document covers ALL changes discussed after v3, based on two weeks of real usage.

---

## Summary

The core insight from real usage: **tests pass ≠ intent satisfied.** Code can be correct but not what the user wanted. The root cause is that we've been mixing two fundamentally different activities in one step — understanding intent (human language) and defining verification (machine language). This change spec separates them and adds the missing layers.

Major changes:
1. New Phase 1: Story (human-language alignment before spec)
2. Proof of Completion per work package
3. Decision classification in spec
4. New command: /ratchet:coverage
5. Auto-verification on every code change
6. Static checking (lint) as Level 1
7. Command restructuring
8. Incremental story/spec updates with full re-verification
9. Complex story splitting with story point estimation (each spec = one sprint)
10. Session management — each spec must run in a new session, file is truth

---

## Change 14: Story Phase (Phase 1 — Before Spec)

### Problem
Spec mixes "what are we building" with "how do we verify it's correct." The spec phase moves too fast, producing constraints that are technically precise but miss the user's actual intent. Users see the final product and say "that's not what I meant" despite all tests passing.

### Solution
Split into two phases. Phase 1 (Story) aligns human understanding through narrative and concrete examples. Phase 2 (Spec) converts the confirmed story into machine-verifiable constraints.

### Story phase produces four artifacts

**1. User Personas (.ratchet/story/personas.md)**

Who are we building for? Not demographic data — behavioral patterns and expectations.

```markdown
## Primary User: Casual Explorer
- Saw a friend's result on social media, curious
- No knowledge of Enneagram theory
- Will leave if first 3 questions are boring
- First instinct after results: share with friends
- Uses mobile phone, not desktop

## Secondary User: Psychology Enthusiast  
- Has taken personality tests before
- Cares about scoring methodology
- Will read type descriptions carefully
- Skeptical of oversimplified results
```

**2. User Journey (.ratchet/story/journey.md)**

A narrative walkthrough of the complete experience. Written as a story, not a feature list.

```markdown
## Journey: First-time User

1. Discovery
   Xiao Hong sees a friend's result card on WeChat moments.
   It shows "Type 5 — The Observer" with a beautiful radar chart.
   She taps the shared link.

2. Landing
   A calm, elegant page loads. The headline says "Discover Your 
   Personality Spectrum." Below: "Start Test" button and "~5 minutes" 
   estimate. She taps Start without hesitation.

3. Answering
   One question at a time, large text, clear options.
   Progress bar at top shows "3/45".
   Questions are introspective, not obvious.
   Midway through, a phone call interrupts. She closes the browser.
   Later she returns — progress is preserved. She continues.

4. Results
   After the last question, a brief loading animation (<2 seconds).
   A radar chart appears with her scores across all 9 types.
   Type 4 stands out. Below is a detailed description that feels 
   personally relevant — specific behavioral examples, not vague 
   adjectives. She scrolls down to see her wing type explained.

5. Sharing
   She taps "Share Result", gets a beautiful result card image.
   Copies the link to WeChat. Her friends can see her result AND 
   start their own test from the same link.
```

This journey implicitly defines dozens of product decisions without writing a single constraint.

**3. Scenario Coverage Table (.ratchet/story/scenarios.md)**

The journey covers the happy path. This table covers everything else.

```markdown
## Scenarios

Normal:
  ✅ Complete all 45 questions → correct result
  ✅ Share link → friend sees result and can start own test
  ✅ Switch language mid-test → questions change, progress preserved

Interruption:
  ✅ Close browser mid-test → resume on return
  ✅ Switch language after completion → results page translates
  ⬜ Clear browser cache → progress lost (acceptable, show message)

Boundary:
  ⬜ All questions answered with middle value (3) → show balanced result
  ⬜ Very slow network → graceful loading states
  ⬜ Old mobile browser → must not white-screen, degraded OK

Out of scope (explicitly excluded):
  ✗ Cheating prevention — not an exam
  ✗ Multi-device sync — not needed for MVP  
  ✗ Accessibility — not MVP, can add later
  ✗ Analytics/tracking — privacy-first
```

The "out of scope" section is critical — it prevents agent from over-engineering.

**4. Visual Mood + Interactive Prototype**

Visual direction described in words (.ratchet/story/mood.md):
```markdown
Mood: quiet, deep, textured — like a good book cover
References: calm.com (serenity), stripe.com (polish)
Anti-patterns: BuzzFeed quiz style, flashy animations, neon colors
```

Plus a clickable HTML prototype (.ratchet/story/prototype.html):
- 3-5 key screens with real layout and placeholder data
- User can click through the flow
- Not the final product — just the skeleton for direction confirmation

**5. Decision Log (.ratchet/story/decisions.md)**

Every decision made during story phase, for traceability:
```markdown
- Immediate result display, no email gate (user confirmed)
- Generate image card for sharing, not just link (user confirmed)  
- localStorage for progress, no account system (user confirmed)
- Tiebreak on equal scores: show both types (user confirmed)
```

### Story phase interaction flow

```
/ratchet:story "Build an Enneagram test website called Lumina"

Agent: generates all 4 artifacts from intent + industry knowledge

Agent: "Here's the user journey I drafted. A few questions:
        1. Show results immediately, or require email first?
        2. Share as image card or just a link?
        3. Progress save: localStorage enough or need accounts?"

User: "Immediate, image card, localStorage is fine"

Agent: updates journey, generates scenario table

Agent: "Here's the scenario coverage. Check the boundary and 
        out-of-scope sections especially."

User: "Add a scenario: user finishes one test and wants another (MBTI later)"

Agent: updates scenarios, generates prototype HTML

Agent: "Open this prototype and click through:
        file:///.ratchet/story/prototype.html"

User: [clicks through] "Radar chart needs to be bigger, 
       type description should be on the right not below"

Agent: updates prototype

User: "This is what I want."

=== Story phase complete, all artifacts confirmed ===
=== Auto-transition to Spec phase ===
```

### Files to create
- `skills/story/SKILL.md` — new skill for story phase
- Template files for each story artifact

### Files to modify
- `skills/getting-started/SKILL.md` — document story as primary entry point
- `skills/spec/SKILL.md` — spec now reads from .ratchet/story/ as input, auto-extracts constraints
- `DESIGN.md` — document two-phase approach
- `README.md` — update flow description
- `references/spec-schema.md` — document story artifact formats

---

## Change 15: Spec Auto-Extraction from Story

### Problem
Currently spec constraints are generated from scratch by analyzing user intent. This misses nuances that were discussed in story phase.

### Solution
Spec phase reads confirmed story artifacts and auto-extracts constraints:

```
From journey.md:
  "closes browser, returns, progress preserved" 
  → INV: localStorage progress persistence
  
  "less than 2 seconds for results" 
  → INV: scoring computation < 2s

  "beautiful result card image"
  → WP: share card generation feature

From scenarios.md:
  "all questions answered 3" 
  → test case for boundary scoring
  
  "out of scope: multi-device sync"
  → do NOT generate sync-related constraints

From prototype.html:
  radar chart size and position 
  → UI verification criteria
  
  layout structure 
  → visual consistency checks

From decisions.md:
  "tiebreak: show both types"
  → scoring logic constraint
```

The spec phase becomes mostly automatic — agent shows the extracted constraints, user does a quick confirmation. Most of the hard alignment work was already done in story phase.

### Files to modify
- `skills/spec/SKILL.md` — rewrite to read story artifacts and auto-extract
- `references/spec-schema.md` — document extraction rules

---

## Change 16: Decision Classification in Spec

### Problem
Agent makes decisions silently during execution that the user should have confirmed, or asks about decisions it could have made itself.

### Solution
Every decision point in the spec is classified:

```yaml
decisions:
  human_must_decide:
    - "Tiebreak rule when types have equal scores"
    - "Wing calculation: adjacent types only or all types?"
    - "Unanswered questions: score as 0 or skip?"
    
  agent_can_decide:
    - "Internal data structure format"
    - "Function decomposition approach"
    - "CSS organization method"
    - "Build tool configuration"
    
  unknown:
    - "Share URL encoding format"
    - "Radar chart library choice"
```

Rules:
- `human_must_decide`: Must be resolved in story/spec phase. Do not proceed without answer.
- `agent_can_decide`: Agent chooses freely, documents choice in Proof of Completion.
- `unknown`: Agent attempts to resolve. If it affects user experience → escalate to human. If purely technical → decide and document.

### Files to modify
- `references/spec-schema.md` — add decisions section to schema
- `skills/spec/SKILL.md` — classify decisions during spec generation
- `skills/story/SKILL.md` — surface human_must_decide items during story phase

---

## Change 17: Proof of Completion per Work Package

### Problem
Agent says "WP done, tests pass" but user has no way to judge WHAT was actually done, what decisions were made, and what wasn't covered.

### Solution
Every WP completion produces a human-readable proof document at `.ratchet/proofs/wp-{id}.md`:

```markdown
## WP-03: Enneagram Scoring Engine — Proof of Completion

### What I Built
- scoringEngine.ts with 3 core functions:
  - calculateScores(): 45 answers → 9 type scores
  - determinePrimaryType(): highest scoring type
  - determineWing(): highest adjacent type to primary

### Design Decisions I Made (agent_can_decide)
- Each question contributes to 1-3 types with weights from questionBank
- Wing only considers two adjacent types, not all 9
- Scores stored as integers, not floats

### Decisions You Already Confirmed (from story/spec)
- Tiebreak: show both types (confirmed in story phase)
- Unanswered questions: score as 0 (confirmed in spec phase)

### Scenario Coverage
| Scenario | Input | Expected | Actual | Status |
|----------|-------|----------|--------|--------|
| Type 7 clear winner | [specific answers] | Primary: 7 | ✅ Type 7 | pass |
| Type 2 and 3 tied | [specific answers] | Show both | ✅ Both shown | pass |
| All answers = 3 | [45 threes] | Balanced, show top 2 | ✅ Correct | pass |
| Only half answered | [22 answers] | Calculate from answered | ✅ Correct | pass |
| All answers = 5 | [45 fives] | Equal scores, show all | ✅ Correct | pass |

### What I Did NOT Cover (needs your judgment)
- ❓ When all 9 types score equally — current: show type 1 first. OK?
- ❓ Decimal precision in percentage display — current: round to integer. OK?

### How You Can Verify
1. Open http://localhost:3000
2. Complete the test normally — result should feel accurate
3. Try: answer all 3s — result should show balanced profile
4. Check browser console for errors
```

### Rules for proof generation
- Proof is mandatory. A WP is not "complete" without it.
- "What I did NOT cover" section is the most important — forces agent to be honest about gaps.
- "Design Decisions I Made" makes implicit choices visible.
- Proof references story artifacts: "you confirmed X in story phase."

### Files to modify
- `skills/verify/SKILL.md` — require proof generation after WP verification
- `agents/wp-executor.md` — executor must produce proof before reporting completion
- `agents/report-writer.md` — include proof summaries in iteration report
- `DESIGN.md` — document proof of completion concept

---

## Change 18: /ratchet:coverage Command

### What
A new command that shows a structured, three-layer coverage dashboard at any time.

### Three layers

**Layer 1: User Story Coverage** — Which user stories and journey steps are implemented?

**Layer 2: Scenario Coverage** — Which scenarios from the scenario table are tested?

**Layer 3: Test Coverage** — Code coverage, auto test results, AI review scores, human review status.

Plus a **Gaps** section highlighting what's missing and what's recommended to add.

### Data sources
No new data collection needed. Coverage skill cross-references existing files:
```
.ratchet/story/journey.md     → Layer 1 step list
.ratchet/story/scenarios.md   → Layer 2 scenario list  
.ratchet/test-suite/manifest.yaml → which scenarios have tests
.ratchet/review_log.yaml     → test results
code coverage tool output     → Layer 3 code coverage
```

### Implementation
Create `skills/coverage/SKILL.md`. It reads all the above files, cross-references them, and produces the layered dashboard view.

For projects with many scenarios (>20), auto-generate `.ratchet/coverage-report.html` — a self-contained HTML file with expandable sections, color-coded status, and progress bars. Open in browser for better readability.

### Files to create
- `skills/coverage/SKILL.md` — new skill

### Files to modify
- `skills/getting-started/SKILL.md` — list coverage as available command
- `DESIGN.md` — document coverage concept

---

## Change 19: Auto-Verification on Every Change

### Problem
After modifications, agent doesn't automatically verify. User has to manually run verification or ask someone to test.

### Solution
Any code change triggers automatic full verification. This is non-negotiable.

### Implementation
In the verify skill and getting-started skill, establish this as an absolute rule:

```
After ANY code modification (regardless of source — WP execution, 
bug fix, spec update, manual edit):

  1. Level 1: Static checks (MUST pass before proceeding)
     - TypeScript compilation: tsc --noEmit
     - Linter: eslint . 
     - Formatter check: prettier --check .
     - Language-specific: golangci-lint / ruff+mypy / cargo clippy
     
  2. Level 2: Unit + component tests
     - Run full test suite (not just changed files)
     - Code coverage measurement
     
  3. Level 3: Integration verification
     - Build the project
     - Start the application
     - Run key scenario checks (curl endpoints, check rendering)
     - Stop the application

  All pass → report results, continue
  Any failure → attempt auto-fix → re-verify (ratchet loop)
  Cannot fix → report failure with details, queue for human
```

### Static checking tools by project type

```yaml
# During environment preparation, install appropriate lint tools:

web_app (React/TypeScript):
  - typescript (tsc --noEmit)
  - eslint + @typescript-eslint
  - prettier
  
go:
  - golangci-lint
  - go vet
  
python:
  - ruff (replaces flake8+isort+pyupgrade)
  - mypy (type checking)
  
rust:
  - cargo clippy
  - cargo fmt --check
```

These tools are installed during pre-validation (Change 12 from v3) and run as part of every Level 1 check.

### Files to modify
- `skills/verify/SKILL.md` — add lint as Level 1, enforce auto-trigger rule
- `skills/spec/SKILL.md` — environment preparation installs lint tools
- `skills/getting-started/SKILL.md` — establish auto-verification as absolute rule
- `references/verifier-guide.md` — document lint tool configuration per project type

---

## Change 20: Incremental Story/Spec Updates with Full Re-verification

### Problem
User sees results and wants changes. Currently unclear how modifications flow through the system.

### Solution
Any modification triggers a complete chain: story update → spec re-derivation → test update → execution → full verification.

### How it works

```
User: "Add growth advice to the results page"

Agent detects: this is a story-level change.

1. Update .ratchet/story/journey.md
   → Add "user reads personalized growth advice" to step 5

2. Update .ratchet/story/scenarios.md  
   → Add scenario: "growth advice is relevant to user's type"

3. Re-derive affected spec constraints
   → New INV: "each type has growth advice section"
   → New QD: "growth advice quality" (ai_review)
   → spec_version: v2 → v3

4. Update test suite
   → New test: growth advice section exists for all 9 types
   → New ai_review prompt: evaluate growth advice quality

5. Execute the change

6. Full verification (ALL tests, not just new ones)
   → Ensures the new feature didn't break anything

7. Generate proof of completion for the change

8. Update coverage dashboard
```

The user doesn't need to trigger any of these steps. They just say "add growth advice" and the entire chain executes.

### Spec version tracking

```yaml
# spec.yaml changelog grows:
changelog:
  - version: 1
    source: story_phase
    change: "Initial spec from confirmed story"
  - version: 2
    source: review_feedback  
    change: "Added tiebreak display rule"
  - version: 3
    source: user_request
    change: "Added growth advice to results page"
    story_updated: true  # Indicates story artifacts also changed
```

### Files to modify
- `skills/getting-started/SKILL.md` — document modification chain
- `skills/story/SKILL.md` — support incremental updates (not just initial creation)
- `skills/spec/SKILL.md` — support re-derivation from updated story
- `DESIGN.md` — document the modification chain

---

## Change 21: Command Restructuring

### Final command structure

**User-facing (daily use):**

| Command | Purpose | When |
|---------|---------|------|
| `/ratchet:story` | Define what to build (personas, journey, scenarios, prototype) | Starting a new intent |
| `/ratchet:spec` | Convert story to verifiable constraints (usually auto-triggered) | After story, or standalone |
| `/ratchet:review` | Review results, give feedback | When agent notifies completion |
| `/ratchet:coverage` | View three-layer coverage dashboard | Anytime |
| `/ratchet:status` | View execution progress across intents | Anytime |
| `/ratchet:profile` | Set personal preferences | One-time setup |

**Internal (agent calls automatically):**

| Skill | Purpose | Triggered by |
|-------|---------|-------------|
| plan | Decompose spec into work packages | After spec confirmation |
| verify | Three-tier verification with lint | After any code change |
| report | Generate iteration reports with proof | After each WP/iteration |
| metrics | Track time, tokens, automation stats | Embedded in report/status |
| update | Process story/spec modifications | User says "change X" in conversation |

**Routing logic (in getting-started):**

```
User says something → Agent determines:

  Mentions existing intent name/keyword?
    → Route to that intent
    → If status=done: reactivate, enter modification chain
    → If status=running: queue modification for next iteration
    → If ambiguous: ask which intent

  Describes something new?
    → /ratchet:story to create new intent

  Asks about progress?
    → /ratchet:status

  Asks about coverage?
    → /ratchet:coverage
    
  Gives feedback on results?
    → /ratchet:review flow (or direct modification chain)
```

### Files to modify
- `.claude-plugin/plugin.json` — update commands list
- `skills/getting-started/SKILL.md` — routing logic, command overview
- Create `skills/story/SKILL.md` — new
- Create `skills/coverage/SKILL.md` — new
- `DESIGN.md` — update architecture overview
- `README.md` — update usage section

---

## Updated EVA Concept

The complete EVA chain, refined through two weeks of usage:

```
Understanding (story) → Specification (spec) → Verification (test) → Execution (code) → Proof (evidence)

Each step is a formalization of the previous:
  Human intuition → Human language → Machine language → Machine execution → Human-readable evidence
```

The original EVA insight ("agent autonomy = f(verification capability)") still holds, but gains a predecessor: verification capability depends on specification quality, which depends on understanding alignment.

**Full principle: Understanding-first, then verification-first, then execution.**

---

## Change 22: Complex Story Splitting with Story Point Estimation

### Problem
Large intents (e.g. "build a full personality test platform with 3 test types") are too big for a single spec → execution cycle. Agent tries to do everything in one session, context fills up, quality degrades in later work packages. The "first iteration looks great but doesn't actually solve the problem" issue is largely a complexity management failure.

### Solution
Each spec is a sprint. Large stories are split into multiple specs (phases), each estimated with story points and executed in its own session.

### Story point estimation

During story phase, after generating the scenario table, agent estimates total complexity:

```yaml
# .ratchet/story/complexity.yaml
total_estimate: 55 points
recommended_split: 3 phases

phases:
  - id: phase-1
    name: "Framework + Enneagram test"
    points: 25
    includes:
      - Landing page and test catalog
      - Enneagram question flow (45 questions)
      - Scoring engine
      - Results page with radar chart
      - Share functionality
      - Bilingual i18n framework
      - Test registry architecture
    depends_on: []
    
  - id: phase-2
    name: "MBTI test"
    points: 18
    includes:
      - MBTI question bank (60 questions, A/B format)
      - MBTI scoring (4 dimensions)
      - MBTI results page (spectrum bars)
      - Validate test registry extensibility
    depends_on: [phase-1]
    
  - id: phase-3
    name: "IQ test + platform polish"
    points: 12
    includes:
      - IQ test question bank
      - Timed question format
      - Score normalization
      - Cross-test analytics dashboard
    depends_on: [phase-1, phase-2]
```

### Story point scale

```
1-5 points:    Trivial. Single WP, < 30 min agent time.
5-15 points:   Small. 2-4 WPs, < 2 hours agent time. One spec, one session.
15-30 points:  Medium. 5-10 WPs, 2-6 hours. One spec, one session 
               (but may need session restart mid-execution).
30-60 points:  Large. Must split into multiple specs/phases.
60+ points:    Very large. Must split. Each phase should be < 30 points.
```

### Auto-split trigger

```
Agent estimates total complexity during story phase.

If total > 30 points:
  Agent: "This is a ~55 point project. I recommend splitting into 
          3 phases. Here's my proposed split:
          
          Phase 1: Framework + Enneagram (25 pts) — ~4 hours
          Phase 2: MBTI (18 pts) — ~3 hours  
          Phase 3: IQ + polish (12 pts) — ~2 hours
          
          Each phase gets its own spec and runs in a fresh session.
          Phase 2 builds on Phase 1's output.
          
          OK with this split? Want to adjust?"

User confirms or adjusts the split.
```

### Each phase is independent

```
Phase 1:
  .ratchet/phases/phase-1/
  ├── story/          # Phase 1 specific story artifacts
  ├── spec.yaml       # Phase 1 specific constraints
  ├── test-suite/     # Phase 1 tests
  ├── proofs/         # Phase 1 completion proofs
  └── coverage.yaml   # Phase 1 coverage data

Phase 2:
  .ratchet/phases/phase-2/
  ├── story/          # Phase 2 story (references Phase 1 output)
  ├── spec.yaml       # Phase 2 constraints
  ├── ...
  └── inputs.yaml     # Explicit: "Phase 2 assumes Phase 1 delivered X, Y, Z"
```

Each phase has its own story artifacts, spec, tests, and proofs. Phase 2's story can reference Phase 1's deliverables as starting conditions.

### Phase lifecycle in state.yaml

```yaml
intents:
  - id: lumina
    workspace: /Users/coder/projects/lumina
    total_points: 55
    phases:
      - id: phase-1
        name: "Framework + Enneagram"
        points: 25
        status: done
        spec_version: 3
        completed_at: 2026-03-20T14:00:00
        
      - id: phase-2
        name: "MBTI"
        points: 18
        status: active       # Current phase
        spec_version: 1
        session_hint: "Start new session for this phase"
        
      - id: phase-3
        name: "IQ + polish"
        points: 12
        status: pending
        depends_on: [phase-1, phase-2]
```

### Files to modify
- `skills/story/SKILL.md` — add complexity estimation and auto-split logic
- `skills/getting-started/SKILL.md` — detect phase status, guide user to correct phase
- `references/spec-schema.md` — document phase structure and story point scale
- `DESIGN.md` — document sprint/phase model

---

## Change 23: Session Management — File is Truth, Session is Disposable

### Problem
Long sessions degrade AI quality. Context window fills up, responses slow down, agent "gets dumber." This is a structural limitation of LLMs, not a bug we can fix. But we can design around it.

### Core principle
**Files are the single source of truth. Sessions are disposable.**

Everything that matters is persisted to .ratchet/ files. Any session can pick up from where any previous session left off by reading files. No critical state exists only in conversation history.

### Rule: Each spec/phase MUST start a new session

```
Phase 1 story complete → spec generated → 

Agent: "Phase 1 spec is ready. Starting execution requires a 
        fresh session for best quality.
        
        All context has been saved to .ratchet/phases/phase-1/
        
        Please start a new Claude Code session and I'll 
        continue from where we left off."

New session:
  → getting-started loads
  → Reads state.yaml: lumina phase-1 status=active, has spec, no execution yet
  → "Lumina Phase 1 (Framework + Enneagram) is ready to execute. 
     Spec v1 confirmed. Starting autonomous execution."
  → Begins with full 200k context, clean and fast
```

### What gets persisted (survives session death)

```
Always persisted to files:
  .ratchet/story/*                — All story discussion results
  .ratchet/phases/*/story/        — Per-phase story artifacts
  .ratchet/phases/*/spec.yaml     — Constraints and verification
  .ratchet/phases/*/test-suite/   — Test cases
  .ratchet/phases/*/proofs/       — Completion evidence
  .ratchet/execution-state.yaml   — Execution progress checkpoint
  .ratchet/review_log.yaml        — All verification results
  ~/.config/ratchet/state.yaml    — Global intent + phase registry
  ~/.config/ratchet/review_queue.yaml — Pending human reviews
```

### What is NOT persisted (lost on session end, and that's OK)

```
  Conversation history
  Agent's reasoning process
  Intermediate build artifacts
  Temporary exploration results
```

### Session checkpoint during execution

```
During long execution, agent periodically saves checkpoint:

.ratchet/execution-state.yaml:
  intent: lumina
  phase: phase-1
  checkpoint_at: 2026-03-20T12:30:00
  work_packages:
    wp-01: done       # Framework scaffold
    wp-02: done       # Question bank
    wp-03: running    # Scoring engine, iteration 3 of 8
    wp-04: pending    # Results page
    wp-05: pending    # Share functionality
  current_wp:
    id: wp-03
    iteration: 3
    best_score: 0.72
    last_failure: "tiebreak logic not handling edge case"
  ratchet_state:
    total_iterations: 12
    total_commits: 8
    total_resets: 4
```

### Session transition triggers

```
Trigger 1: Phase complete
  → Save all results → Prompt user to start new session for next phase

Trigger 2: Context getting full (agent detects slowness or compact triggered)
  → Save execution-state.yaml checkpoint
  → Agent: "Session is getting long. I've saved progress at wp-03 iteration 3.
            Start a new session to continue with fresh context."

Trigger 3: Story discussion exceeds ~30 minutes
  → All story artifacts already saved to files
  → Agent: "We've been discussing for a while. All decisions are saved.
            Want to continue here or start fresh?"
            
Trigger 4: User explicitly asks
  → "Let's continue in a new session"
  → Agent saves checkpoint → user starts new session
```

### Getting-started behavior on session start

```
Every new session, getting-started does:

1. Read ~/.config/ratchet/state.yaml
   → Find all intents and their phases

2. For current workspace's intent:

   Case A: Story in progress (story files exist, no spec)
     → "We were discussing Lumina's user journey. 
        Last confirmed: personas and journey.
        Still need to confirm: scenarios and prototype.
        Let's continue."
     → Load story files into context

   Case B: Spec confirmed, execution not started
     → "Lumina Phase 1 spec is ready. Starting execution."
     → Begin autonomous execution

   Case C: Execution in progress (execution-state.yaml exists)
     → "Lumina Phase 1: 2/5 WPs complete. 
        WP-03 (scoring engine) was at iteration 3, score 0.72.
        Resuming from checkpoint."
     → Continue execution from checkpoint

   Case D: Phase complete, next phase pending
     → "Lumina Phase 1 complete! 
        Phase 2 (MBTI) is next. Ready to start story phase?"

   Case E: All phases done
     → "Lumina is complete. All 3 phases done.
        Want to review, check coverage, or make modifications?"
        
3. If multiple intents exist and not in a specific workspace:
   → Show summary of all intents with their current state
   → Ask which one to work on
```

### File structure for multi-phase project

```
.ratchet/
├── story/                      # Top-level story (the big picture)
│   ├── personas.md
│   ├── journey.md              # Full journey across all phases
│   ├── scenarios.md            # All scenarios
│   ├── complexity.yaml         # Story point estimate + phase split
│   └── decisions.md
├── phases/
│   ├── phase-1/
│   │   ├── story/              # Phase 1 specific details
│   │   │   ├── journey.md      # Phase 1 journey subset
│   │   │   ├── scenarios.md    # Phase 1 scenarios
│   │   │   └── prototype.html
│   │   ├── spec.yaml
│   │   ├── plan.yaml
│   │   ├── test-suite/
│   │   ├── proofs/
│   │   └── reports/
│   ├── phase-2/
│   │   ├── story/
│   │   ├── spec.yaml
│   │   ├── inputs.yaml         # "Assumes Phase 1 delivered X"
│   │   └── ...
│   └── phase-3/
│       └── ...
├── execution-state.yaml        # Current execution checkpoint
├── review_log.yaml
└── coverage.yaml               # Cross-phase coverage data
```

### For simple projects (< 30 points)

No phases needed. Everything stays flat:

```
.ratchet/
├── story/
├── spec.yaml
├── test-suite/
├── proofs/
└── ...
```

The phase structure only kicks in when agent estimates > 30 points and user confirms the split.

### Files to modify
- `skills/getting-started/SKILL.md` — session resumption logic, phase detection
- `skills/story/SKILL.md` — complexity estimation, phase splitting
- `skills/spec/SKILL.md` — phase-aware spec generation
- `skills/status/SKILL.md` — show phase progress
- `skills/coverage/SKILL.md` — cross-phase coverage
- `references/spec-schema.md` — document phase structure, execution-state schema, story point scale
- `DESIGN.md` — document session management philosophy and phase model

---

## Implementation Priority (Updated)

1. **Change 14: Story phase** — Highest impact. Fixes root cause.
2. **Change 15: Spec auto-extraction** — Natural follow-on from story.
3. **Change 23: Session management** — Critical for quality. Each spec = new session.
4. **Change 22: Story splitting + story points** — Handles complexity.
5. **Change 21: Command restructuring** — Expose story, coverage commands.
6. **Change 19: Auto-verification + lint** — Essential quality gate.
7. **Change 18: Coverage command** — User visibility into gaps.
8. **Change 17: Proof of Completion** — Improves review quality.
9. **Change 16: Decision classification** — Reduces silent wrong decisions.
10. **Change 20: Incremental updates** — Enables iteration after delivery.

---

## Testing the Changes

After implementation, test with a new Lumina project:

```
SESSION 1: Story Phase

1. /ratchet:story "Build a beautiful Enneagram personality test 
   web app called Lumina. Bilingual Chinese/English. Premium calm 
   design. Pure frontend, deployable to Vercel."

2. Verify story artifacts generated in .ratchet/story/

3. Click through prototype.html

4. Verify complexity estimation — should be < 30 points 
   for Enneagram only, no phase split needed

5. Confirm story → spec auto-generated

6. Agent should say: "Spec ready. Start new session for execution."


SESSION 2: Execution

7. Start new Claude Code session in same directory

8. Agent should detect: "Lumina spec confirmed, starting execution"

9. Watch auto-execution with lint checks at Level 1

10. Each WP completion should produce proof document in .ratchet/proofs/

11. If session gets slow, agent should checkpoint and suggest new session


SESSION 3: Review

12. /ratchet:review — see results with proof summaries

13. /ratchet:coverage — verify three-layer dashboard

14. Make a modification: "add growth advice to results"
    → Full chain: story update → spec → test → execute → verify

15. /ratchet:coverage again — verify it reflects the change


LARGE PROJECT TEST:

16. /ratchet:story "Build Lumina with Enneagram, MBTI, and IQ tests"

17. Verify: agent estimates > 30 points, proposes 3-phase split

18. Confirm split → Phase 1 story + spec generated

19. Start new session → Phase 1 executes

20. After Phase 1 done → start new session → Phase 2 begins
    with Phase 1 output as input
```
