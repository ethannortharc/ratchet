---
description: "Start a new intent — define what you want to build through guided conversation, then agent executes autonomously"
---

<IMPORTANT>
This command has loaded the spec workflow. Do NOT invoke the spec skill again via the Skill tool — that causes infinite recursion. Execute the workflow below directly.
</IMPORTANT>

Follow the `spec` skill workflow in `skills/spec/SKILL.md`. Read it and execute each step in order.

If the user provided intent with this command, use it as the project description. Otherwise, ask for their intent.

After spec confirmation, automatically chain: environment preparation → test suite generation → pipeline validation → plan → execution. Do NOT wait for user to invoke separate commands.
