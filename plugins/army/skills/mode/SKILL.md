---
name: mode
description: Show or switch the army's model profile (lean or full). Use only when the user explicitly asks to check or change the army mode, or runs /army:mode. Never switch modes on your own initiative.
argument-hint: "[lean|full]"
---

Run:

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/army.js" mode $ARGUMENTS --data "${CLAUDE_PLUGIN_DATA}"
```

Then reply in one or two lines with the current mode and what it means:
- **lean** (default, suited to the Pro plan): no unit runs on Opus. Critical units (ops, defense, legal, rescue, inspector-general, rnd, special-ops) run on Sonnet, and light units (logistics, treasury, growth, sales, recon, history) run on Haiku. HQ also engages fewer units.
- **full** (suited to the Max plan): critical units run on Opus, most units run on Sonnet, and mechanical units run on Haiku.

Tip for **full** mode: run the main session on Opus (`/model opus`), because HQ itself runs on the main session's model.
