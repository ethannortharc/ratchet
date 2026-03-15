---
name: profile
description: Set up or update personal preferences applied across all Ratchet projects. One-time setup, update as needed. Covers technical, creative, and work style preferences. Use on first run or when user says "update profile", "change preferences", "I switched to Rust".
---

# Profile — Personal Preferences

## Storage
`~/.config/ratchet/profile.yaml`

## First-Time Setup (keep under 3 minutes)

Ask only what's relevant based on user context:

1. **Domains**: "What kinds of projects do you typically do?" → software / writing / research
2. **Technical**: "Primary languages/tools?" → populates defaults
3. **Intervention level**: "How much involvement during execution?" → minimal / moderate / active
4. **Quality vs speed**: "Fast with rough edges, or slower but polished?" → adjusts thresholds
5. **Risk tolerance**: "OK if agent guesses wrong and redoes, or always ask first?" → adjusts auto-proceed

Domain-specific questions only if relevant (see DESIGN.md for full schema).

## Schema

```yaml
profile:
  created: datetime
  updated: datetime
  name: string
  domains:
    primary: [string]
  technical:
    languages: [string]
    testing: tdd | test_after | minimal
    style_reference: string
  creative:
    genres: [string]
    tone_anchors: [{work: string, aspect: string}]
    content_boundaries: [string]
  work_style:
    intervention: minimal | moderate | active
    quality_speed: quality_first | balanced | speed_first
    risk_tolerance: high | medium | low
  environment:
    known_capabilities: [string]
```

## How Profile Is Used
- `/ratchet:spec` applies profile as defaults (overridable per project)
- Ratchet budgets adjust based on quality_speed preference
- Human checkpoint frequency adjusts based on intervention level
- Agent auto-proceeds on assumptions based on risk_tolerance
