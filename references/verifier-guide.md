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

### Patterns by capability:

**Go projects (requires: go)**
```bash
go build ./...                          # Compiles
go test ./...                           # Tests pass
go test -cover ./... | grep -v 'ok'     # Coverage check
go vet ./...                            # Static analysis
```

**Node projects (requires: node)**
```bash
npm test                    # Tests pass
npm run build               # Build succeeds
npm run lint                # Linter passes
```

**Python projects (requires: python3)**
```bash
python -m pytest            # Tests pass
python -m mypy .            # Type check
python -m flake8 .          # Lint
```

**Docker (requires: docker)**
```bash
docker build -t test .              # Image builds
docker run --rm test npm test       # Tests in container
```

**Text/content checks (no special requirements)**
```bash
wc -w < file.md                        # Word count
grep -c 'pattern' file                  # Pattern presence
yamllint file.yaml                      # YAML valid
python3 -c "import json; json.load(open('f.json'))"  # JSON valid
```

**Git checks (requires: git)**
```bash
git diff --name-only HEAD~1     # What changed
git log --oneline -5            # Recent history
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
| Performance (latency) | auto (with runtime env) | human (without) |
| Security | auto (with scanner) + ai_review | human (without scanner) |
| Accessibility | auto (with axe/lighthouse) | ai_review (without) |

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

When a new capability becomes available, these constraints can be upgraded:

| New Capability | Constraints Upgraded | From → To |
|---------------|---------------------|-----------|
| Docker | Cross-platform build, integration tests | human → auto |
| golangci-lint | Code quality, style | ai_review → auto |
| Playwright | UI testing, responsive check | human → auto |
| pytest | Python test execution | human → auto |
| Superpower plugin | TDD enforcement, code review | human → auto/ai_review |
| Lighthouse | Performance, accessibility | human → auto |
