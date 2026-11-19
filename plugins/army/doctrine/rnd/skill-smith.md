# Skill smith

Goal: when the same kind of task keeps coming back, give it its own command (a Claude Code skill), so it runs better and cheaper every time.

## When to build a skill
The task recurred at least twice (check `.army/lessons.md` and mission logs), it has a stable procedure, and the user would benefit from invoking it directly.

## Design
1. **Trigger:** the `description` field says exactly when Claude should use the skill, in specific words. Vague descriptions cause false triggers or missed triggers.
2. **Scope:** one job. If it does three things, it's three skills, or one skill with clear modes.
3. **Body:** the procedure in numbered steps, the inputs (`$ARGUMENTS`), the output format, and the guardrails. Keep `SKILL.md` short and move long reference material to separate files that the skill tells Claude when to read.
4. **Paths:** reference bundled files with `${CLAUDE_PLUGIN_ROOT}` (plugin skills) or relative paths (project or personal skills).
5. **Location:** personal (`~/.claude/skills/`), project (`.claude/skills/`), or a plugin in the user's marketplace, depending on who should use it.

## Rules
- Write the skill as a draft in the mission folder first. Installing it in any location is a HANDBACK item for the user to approve.
- Hand the draft to rnd/proving-ground before recommending it.

## Output
The draft skill folder, a short explanation of when it triggers, and the test results from the proving ground.
