---
name: status
description: Show the army status (mode, safety gates, active mission and phase, memory size).
disable-model-invocation: true
---

Run:

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/army.js" status --session "${CLAUDE_SESSION_ID}" --data "${CLAUDE_PLUGIN_DATA}"
```

Reply with a compact summary: mode, gates, the active mission and its phase (if any), missions logged, and lessons size. If the user also asks to see the lessons, read `.army/lessons.md` and show it, labeled as project memory.
