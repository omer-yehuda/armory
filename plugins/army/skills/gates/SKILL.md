---
name: gates
description: Show or switch the army safety gates (on or off).
argument-hint: "[on|off]"
disable-model-invocation: true
---

Run:

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/army.js" gates "$ARGUMENTS" --data "${CLAUDE_PLUGIN_DATA}"
```

Reply in one line with the current state:
- **on** (default): during a mission, a hook asks before irreversible or external actions:
  - git push, history rewrites and discarding changes
  - deleting files or data
  - deployments and publishing
  - new dependencies, and downloaded scripts or packages
  - GitHub writes and external MCP actions
  - changes to the army's own state
- **off**: the army proceeds without asking. Claude Code's normal permission prompts still apply.

The gate is a speed bump, not a sandbox: it reads shell commands, but not what runs inside scripts. If the user turned the gates off, add a one-line reminder of what that allows. If a mission is active, this command asks for approval.
