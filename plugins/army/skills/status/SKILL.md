---
name: status
description: Show the army's status (mode, safety gates, active mission, memory size). Use only when the user explicitly asks for army status or runs /army:status.
---

Run:

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/army.js" status --data "${CLAUDE_PLUGIN_DATA}"
```

Reply with a compact summary: mode, gates, active mission (if any), number of missions logged, and lessons-learned size. If the user also asks to see the lessons, read `.army/lessons.md` and show it.
