# Skill Installer

**Install Claude skills straight from GitHub, with a dry run and a quick risk check first.**

```
/plugin install skill-installer --marketplace omer-yehuda/plugins
```

Then just ask:

```
install the frontend-design skill from anthropics/skills
/skill-installer:install https://github.com/anthropics/skills/tree/main/skills/pdf
/skill-installer:browse                      # skills in anthropics/skills, installed ones marked
/skill-installer:browse market               # every plugin in this marketplace, with install lines
install pdf, docx and xlsx from anthropics/skills, project only
```

## What it does

| Step | What happens |
|---|---|
| Browse | Lists every folder with a `SKILL.md` in a repo (default `anthropics/skills`) with its description, and marks the ones you already have. `browse market` lists a plugin marketplace (default `omer-yehuda/plugins`). |
| Dry run | Downloads just that skill folder (not the whole repo), checks the `SKILL.md` frontmatter, counts files and size, and notes whether it ships scripts. Nothing is written. |
| Quick risk check | Flags a download piped into a shell, base64 decode-and-run, whole-folder deletes, reads of SSH keys or credentials, text telling Claude to drop its earlier rules and invisible characters. If anything is flagged, or the skill ships scripts, Claude asks before installing and offers `/customs:inspect` when the Customs plugin is installed. |
| Install | Writes to a temp folder, then renames it into place: never a half-installed skill. Updating keeps the old copy as `.name.backup-<time>`. |
| Typos | A wrong path answers with "Did you mean ...?" and the list of skills that do exist. |

Where skills go: `~/.claude/skills/<name>` (or `CLAUDE_CONFIG_DIR/skills`) by default, `<project>/.claude/skills/<name>` when you say "project only". Restart Claude Code or run `/reload-plugins` afterwards.

## Tested

Run on 2026-11-19 against the public `anthropics/skills` repo:

| Test | Result |
|---|---|
| Browse `anthropics/skills` | 19 skills listed with descriptions |
| Install `frontend-design` | 2 files, 0.8 s |
| Install `pdf`, `docx`, `xlsx` in one go | 126 files, 5.4 s |
| Same skill again | refused ("Already installed"), update keeps a backup |
| Typo `fronted-design` | "Did you mean skills/frontend-design?" |
| Dry run of all 19 skills | 442 files, 11.5 MB, 11 ship scripts, 1 skill flagged (3 warnings) |
| Private repo / API limit | falls back to a sparse git clone (13-file skill in 3.9 s) |

Limits, honestly: the risk check is a handful of patterns, not a security review. The one skill it flagged (`claude-api`) is documentation that quotes install commands, so expect false positives, and a clean result does not mean a skill is safe. For a real scan use [Customs](../customs/README.md). Plugins are installed with `/plugin install`, not with this skill.

## Safety

- Only `https://github.com` sources. Owner, repo, branch and paths are checked (no `..`, no absolute paths, no option-looking branches).
- User text never reaches the shell: the skill writes a request file and the script reads it.
- Symlinks and submodules are refused; a skill is capped at 300 files and 10 MB.
- Nothing from a downloaded skill is ever run. The git fallback runs with hooks and symlinks off and no prompts.
- `GITHUB_TOKEN` or `GH_TOKEN` is used for the GitHub API when set (private repos, higher limits).

Behind a proxy, set `NODE_USE_ENV_PROXY=1` (Node 22.21+); otherwise the git fallback is used.

## Credits

Adapted from the `skill-installer` skill that ships with OpenAI Codex ([openai/skills](https://github.com/openai/skills), Apache-2.0). Ported to Node.js and Claude Code, with the dry run, risk check, atomic install, project scope and marketplace listing added. See [NOTICE](NOTICE). Licensed under Apache-2.0 ([LICENSE](LICENSE)).

Not affiliated with, sponsored or endorsed by OpenAI or Anthropic.
