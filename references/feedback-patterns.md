# Feedback Conversion Patterns

Structured patterns for converting subjective human feedback into agent-verifiable constraints. Used by the review skill's feedback conversion engine and during direct feedback processing.

## How to Use

When processing human feedback:
1. Match the feedback against patterns in the relevant domain section
2. If a pattern matches, use the suggested constraint + verifier + test_method
3. If no pattern matches, attempt freeform conversion (see "Conversion Strategy" below)
4. If conversion fails, add to `agent_guidance` and keep as human-track

## Software Domain

| Feedback Pattern | Constraint | Verifier | Test Method |
|-----------------|------------|----------|-------------|
| "feels slow" / "too slow" / "laggy" | response_time < {threshold}ms | auto | Measure render/response time with performance API or time command |
| "code is messy" / "hard to read" | linter passes with zero warnings | auto | Run project linter (eslint, golangci-lint, flake8, etc.) |
| "not accessible" / "can't tab through" | Lighthouse accessibility score >= {threshold} | auto | Run Lighthouse CI or axe-core |
| "looks broken on mobile" / "not responsive" | Renders correctly at 375px, 768px, 1024px widths | auto | Playwright viewport tests at standard breakpoints |
| "navigation confusing" / "can't find X" | Max {N} clicks from landing to any feature | auto | Playwright navigation path tests |
| "crashes when I do X" | No uncaught exceptions during {scenario} | auto | Test the specific scenario with error boundary checks |
| "doesn't work offline" | Core features functional without network | auto | Playwright with network disabled |
| "page is blank" / "nothing loads" | Page renders content within 3s | auto | Playwright waitForSelector + screenshot comparison |
| "button doesn't work" / "clicking X does nothing" | {element} click triggers {expected_action} | auto | Playwright click + assertion |

## Creative Writing Domain

| Feedback Pattern | Constraint | Verifier | Test Method |
|-----------------|------------|----------|-------------|
| "tone shifts" / "inconsistent voice" | tone_consistency >= {threshold}/5 | ai_review | Compare tone across sections against reference passage |
| "too verbose" / "wordy" | avg_sentence_length <= {threshold} words | auto | Word count per sentence analysis |
| "characters feel flat" / "no depth" | character_depth >= {threshold}/5 | ai_review | Evaluate character arc, internal conflict, growth per character |
| "dialogue sounds unnatural" | dialogue_naturalness >= {threshold}/5 | ai_review | Evaluate dialogue for distinct voices, appropriate register |
| "pacing too slow" / "drags" | scene_pacing >= {threshold}/5 | ai_review | Evaluate scene density, tension arc, unnecessary exposition |
| "story is boring" / "not engaging" | — | human | Add to agent_guidance: increase conflict density, stakes, surprises |
| "plot doesn't make sense" | plot_coherence >= {threshold}/5 | ai_review | Check causal chain, foreshadowing, resolution consistency |

## Research Domain

| Feedback Pattern | Constraint | Verifier | Test Method |
|-----------------|------------|----------|-------------|
| "sources are weak" / "not credible" | All citations from peer-reviewed or primary sources | ai_review | Verify source credibility and recency |
| "too biased" / "one-sided" | Presents >= {N} perspectives per claim | ai_review | Count distinct viewpoints per major claim |
| "conclusions don't follow" | Each conclusion traces to evidence in findings | ai_review | Map conclusion → evidence chain |
| "missing context" / "assumes too much" | Key terms defined on first use | auto | Grep for technical terms, verify definition precedes usage |

## Design Domain

| Feedback Pattern | Constraint | Verifier | Test Method |
|-----------------|------------|----------|-------------|
| "too cluttered" / "overwhelming" | Max {N} elements per viewport | auto | Count visible elements per screen via Playwright |
| "colors clash" / "ugly palette" | Color palette passes contrast checks | auto | WCAG contrast ratio check on all color pairs |
| "text too small" | Min font size >= {threshold}px | auto | Playwright computed style check on all text elements |
| "inconsistent spacing" | Spacing uses {N}px grid increments | auto | Computed style analysis for margin/padding values |

## Conversion Strategy (When No Pattern Matches)

1. **Identify the observable:** What would a user see/measure if the issue were fixed?
2. **Find a proxy metric:** Can the improvement be measured automatically?
3. **Determine verifier:** auto (measurable) > ai_review (judgable) > human (subjective)
4. **Write test_method:** How specifically would you verify the constraint?
5. **If no proxy exists:** Add specific direction to `agent_guidance` and keep as human-track

## Unconvertible Feedback

Some feedback has no good automated proxy. Acknowledge this and handle gracefully:
- "I don't like it" → Ask for specifics, then try again
- "It doesn't feel right" → Ask what "right" would look like
- "Story is boring" → Add to agent_guidance with specific direction (more conflict, higher stakes, etc.)
- "Design doesn't match brand" → Keep human-track, provide brand guidelines in agent_guidance
