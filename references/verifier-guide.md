# Verifier Guide

## Assignment Priority

Always prefer the most automated option available:

```
auto > ai_review > human
```

A constraint should only be `human` if:
1. No automated proxy exists, AND
2. The dimension is genuinely subjective, AND
3. ai_review cannot reliably approximate human judgment for this specific case

## Implementing auto Verifiers

Auto verifiers MUST be executable commands that return exit code 0 (pass) or non-zero (fail).

### Verification Capabilities

Do not hardcode specific tools. Instead, identify what **capability** is needed and use whatever tool the environment provides (as recorded in `.ratchet/pre-validation.log`).

| Capability | What it verifies | How to find |
|-----------|-----------------|-------------|
| Build/compile | Code compiles without errors | Detect from project files (package.json scripts, Makefile, go.mod, Cargo.toml, etc.) |
| Test runner | Tests pass | Detect from project config or test directory conventions |
| Linter | Code style, static analysis | Detect from project config (.eslintrc, .golangci.yml, setup.cfg, etc.) |
| Type checker | Type safety | Detect from project config (tsconfig.json, mypy.ini, etc.) |
| Browser testing | UI renders, interactions work | Check pre-validation.log capabilities; always use headless mode |
| HTTP client | API endpoints respond correctly | Any available HTTP tool (curl, httpie, language-native) |
| Container runtime | Cross-platform, isolated tests | Check if container runtime is available |

### Common Patterns (Examples, Not Exhaustive)

These are examples of how auto verifiers work in practice. The agent should discover the right commands for the specific project, not copy these verbatim:

```bash
# Build verification — use the project's own build command
[package-manager] run build    # or make, cargo build, go build, etc.

# Test verification — use the project's own test command
[package-manager] test         # or the test runner directly

# Lint verification — use whatever linter the project configures
[package-manager] run lint     # or the linter directly

# Content checks — generally shell-native
wc -w < file.md               # Word count
yamllint file.yaml             # YAML valid
```

## Implementing ai_review Verifiers

For ai_review, construct a review prompt that includes:

1. **The constraint being verified** (from spec)
2. **The rubric** (scoring criteria)
3. **The artifact** (what to review)
4. **Context** (relevant spec sections, setting docs, etc.)

Template:
```
You are reviewing an artifact against a quality specification.

CONSTRAINT: [constraint claim]
RUBRIC:
[rubric text]
THRESHOLD: [minimum score]

ARTIFACT TO REVIEW:
[artifact content or file reference]

CONTEXT:
[relevant project context]

Please evaluate the artifact against the rubric.
Output EXACTLY this format:
SCORE: [number]
PASS: [yes/no]
JUSTIFICATION: [2-3 sentences explaining the score]
ISSUES: [list specific issues if any, or "none"]
```

## Implementing human Verifiers

For human verification, present:
1. What they need to evaluate
2. The criteria/rubric
3. Where to find the artifact
4. A clear pass/fail/revise prompt

## Verifier Assignment by Common Constraint Types

| Constraint Type | Default Verifier | Upgrade Path |
|----------------|-----------------|--------------|
| Compiles/builds | auto | — |
| Tests pass | auto | — |
| Word count range | auto | — |
| Schema/format valid | auto | — |
| Code style | auto (with linter) | ai_review (without linter) |
| POV consistency | ai_review | — |
| Tone consistency | ai_review (with anchor) | human (without anchor) |
| Character consistency | ai_review | — |
| "Feels compelling" | human | — |
| Performance (latency) | auto (with benchmarking capability) | human (without) |
| Security | auto (with scanning capability) + ai_review | human (without scanner) |
| Accessibility | auto (with accessibility testing capability) | ai_review (without) |

## Ratchet Budget by Domain

| Domain | Default Budget | Rationale |
|--------|---------------|-----------|
| Software | 8-10 | Auto metrics are precise, ratchet is very effective |
| Research | 5-7 | Coverage metrics are precise, quality metrics less so |
| Creative Writing | 3-5 | ai_review has noise, diminishing returns after ~5 |
| Design | 3-5 | Similar to creative — ai_review is proxy not ground truth |

If spec has >70% agent-track constraints → use high budget.
If spec has >50% human-track constraints → use low budget (ratchet helps less).

## Environment Capability → Verifier Upgrades

When a new capability becomes available, constraints can be upgraded. The agent should identify these upgrade opportunities during environment negotiation and `/ratchet:review`:

| New Capability | Constraints Upgraded | From → To |
|---------------|---------------------|-----------|
| Container runtime | Cross-platform build, integration tests | human → auto |
| Linting tool | Code quality, style | ai_review → auto |
| Browser testing (headless) | UI testing, responsive check, interaction testing | human → auto |
| Test framework | Language-specific test execution | human → auto |
| Performance testing | Latency, throughput, bundle size | human → auto |
| Accessibility testing | WCAG compliance, contrast, navigation | human → auto |
