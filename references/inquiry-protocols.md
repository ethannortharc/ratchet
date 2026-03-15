# Inquiry Protocols — Domain Knowledge by Project Type

When generating a spec, use this domain knowledge to auto-fill constraints the user didn't explicitly state. These represent industry best practices — things any experienced practitioner would expect.

## Software Projects

### Auto-generate these invariants (unless user explicitly opts out):
- Build succeeds on target platform(s)
- All tests pass
- No critical linter warnings
- API backwards compatibility (if modifying existing API)
- Error handling for all external calls

### Auto-generate these quality dimensions:
- Test coverage on core logic (threshold: contextual, typically 70-80%)
- Code follows language idioms (verifier: ai_review)
- Error messages are actionable (verifier: ai_review)
- Documentation covers public API (verifier: ai_review)

### Probes — ask only if relevant:
- "Involves network/API?" → add latency, concurrency, auth constraints
- "Involves data storage?" → add schema, migration, backup constraints
- "Involves UI?" → add responsive, accessibility constraints
- "Modifying existing code?" → add backwards compatibility, migration path

### Common confidence gaps:
- Performance requirements (often unstated)
- Error handling strategy (often assumed)
- Concurrency safety (often overlooked)
- Deployment target (often implicit)

## Creative Writing Projects

### Auto-generate these invariants:
- Narrative POV consistency (verify: ai_review)
- Character name/trait consistency across chapters (verify: ai_review)
- Word count per unit within specified range (verify: auto)
- Timeline internal consistency (verify: ai_review)

### Auto-generate these quality dimensions:
- Tone/voice consistency (verify: ai_review, needs anchor works)
- Character arc completeness (verify: ai_review)
- Pacing — balance of action/reflection/dialogue (verify: ai_review or human)
- Chapter-end hooks / reader engagement (verify: ai_review)

### Key things to infer or ask:
- POV (first person / third limited / third omniscient / other)
- Tone anchors — MUST be specific works, not adjectives
- Content boundaries / taboos
- Target audience sophistication level

### Common confidence gaps:
- "What style?" stated as adjective without anchor ("dark" means nothing without a reference)
- Implicit genre conventions not stated
- World-building rules for speculative fiction
- Dialogue style preferences

## Research Projects

### Auto-generate these invariants:
- Minimum number of sources / data points
- Source quality criteria (peer-reviewed, primary sources, recency)
- Coverage of specified dimensions/aspects
- Structured output format (table, report sections, etc.)

### Auto-generate these quality dimensions:
- Source diversity (not all from one outlet/perspective)
- Claim-evidence traceability (every claim has a source)
- Completeness vs. scope definition
- Actionability of conclusions/recommendations

### Key things to infer or ask:
- Scope boundaries (what's in / what's out)
- Output format (report, spreadsheet, presentation, brief)
- Depth vs. breadth tradeoff
- Decision context (why is this research being done?)

## Design Projects

### Auto-generate these invariants:
- Design document covers all specified components
- Diagrams are internally consistent
- Interfaces between components are defined
- Non-functional requirements addressed (scale, security, cost)

### Auto-generate these quality dimensions:
- Clarity — a new team member can understand the design
- Completeness — no major component left unspecified
- Feasibility — design is implementable with stated constraints

## Universal Quality Checks

Apply these regardless of project type when generating spec:

1. **Scan for subjective adjectives without anchors**: "clean", "elegant", "user-friendly", "readable", "fast", "good" → require specific reference or metric
2. **Scan for unbounded scope**: "support all...", "handle any..." → require explicit boundaries
3. **Verify every invariant has a verifier**: no constraint should exist without a verification method
4. **Check for missing "don'ts"**: users often forget to state what they DON'T want. Proactively suggest common exclusions for the project type.
