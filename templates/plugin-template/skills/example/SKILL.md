---
name: example
description: One sentence saying WHEN Claude should use this skill (the trigger), and what it does. Claude decides from this text alone, so be specific.
argument-hint: "<what the user passes>"
---

# Example skill

Instructions Claude follows when this skill runs. The user's arguments are available as $ARGUMENTS.

- Reference bundled files with ${CLAUDE_PLUGIN_ROOT}/path/to/file.
- Store persistent per-user data under ${CLAUDE_PLUGIN_DATA}.
- Keep SKILL.md short; move long reference material into separate files next to it and tell Claude when to read them.
