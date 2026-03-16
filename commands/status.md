---
description: "Check progress across all intents — lifecycle state, WP progress, pending reviews, metrics"
argument-hint: "[INTENT_ID]"
---

<IMPORTANT>
This command has loaded the status workflow. Do NOT invoke the status skill again via the Skill tool — that causes infinite recursion. Execute the workflow below directly.
</IMPORTANT>

Follow the `status` skill workflow in `skills/status/SKILL.md`. Read it and execute each step in order. Pass the user's argument as the intent ID if provided. Include metrics (autonomy ratio, verification coverage, iteration counts) in the display.
