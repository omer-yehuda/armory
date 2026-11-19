---
name: mode
description: Show or switch the army model profile (lean or full).
argument-hint: "[lean|full]"
disable-model-invocation: true
---

Run:

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/army.js" mode "$ARGUMENTS" --data "${CLAUDE_PLUGIN_DATA}"
```

The output includes `models`, the resolved unit→model map. Reply with the mode and a compact summary of that map, grouped by model.
- **lean** (default, suited to the Pro plan): no unit runs on Opus.
- **full** (suited to the Max plan): critical units run on Opus.

Tip for **full** mode: HQ runs on the main session's model, so use `/model opus` too.

If a mission is active, this command asks for approval (the safety gate protects the army's settings during missions).
