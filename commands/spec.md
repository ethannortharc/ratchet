---
description: "Start a new intent — define what you want to build through guided conversation, then agent executes autonomously"
---

Use the ratchet `spec` skill to handle this request. Follow the skill's workflow exactly.

If the user provided intent with this command, use it as the project description. Otherwise, ask for their intent.

After spec confirmation, automatically chain: environment preparation → test suite generation → pipeline validation → plan → execution. Do NOT wait for user to invoke separate commands.
