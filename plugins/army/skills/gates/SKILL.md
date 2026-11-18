---
name: gates
description: Show or switch the army's safety gates (on or off). Use only when the user explicitly asks to check or change army safety gates / approvals, or runs /army:gates. Never change this on your own initiative.
argument-hint: "[on|off]"
---

Run:

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/army.js" gates $ARGUMENTS --data "${CLAUDE_PLUGIN_DATA}"
```

Then reply in one line with the current state:
- **on** (default): during a mission, the army stops and asks before irreversible actions: git push, deploy, publish, deleting files or data, history rewrites, schema migrations and installing new dependencies.
- **off**: the army proceeds without asking. Claude Code's normal permission prompts still apply.

If the user turned the gates off, add a short reminder that this lets the army push, deploy and delete without asking.
