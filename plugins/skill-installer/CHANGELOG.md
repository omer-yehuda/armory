# Changelog

## 1.0.0 (2026-11-20)

- `/skill-installer:install`: install one or more skills from a GitHub URL or `owner/repo/path` into `~/.claude/skills` or the project's `.claude/skills`, dry run first, quick risk check, atomic copy, backup on update.
- `/skill-installer:browse`: list the skills in a repo (default `anthropics/skills`) or the plugins in a marketplace (default `omer-yehuda/plugins`), marking installed ones.
- "Did you mean" for wrong skill paths.
- Dependency-free Node.js; GitHub tree API plus raw files, sparse git clone fallback.
- Adapted from OpenAI's Apache-2.0 Codex `skill-installer` (see NOTICE).
