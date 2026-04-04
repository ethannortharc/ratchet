---
description: "Define what to build — personas, journey, scenarios, prototype. Phase 1 before spec."
argument-hint: "\"describe what you want to build\""
---

<IMPORTANT>
This command has loaded the story workflow. Do NOT invoke the story skill again via the Skill tool — that causes infinite recursion. Execute the workflow below directly.
</IMPORTANT>

Follow the `story` skill workflow in `skills/story/SKILL.md`. Read it and execute each step in order.

If the user provided intent with this command, use it as the project description. Otherwise, ask for their intent.

After story confirmation, automatically transition to the spec phase — read the confirmed story artifacts and generate the Intent Spec. Do NOT wait for user to invoke `/ratchet:spec` separately.
