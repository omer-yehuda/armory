<div align="center">

# Omer Yehuda · Claude Code Plugins

**A curated marketplace of production-grade plugins for [Claude Code](https://code.claude.com).**

[![Validate](https://github.com/omer-yehuda/plugins/actions/workflows/validate.yml/badge.svg)](https://github.com/omer-yehuda/plugins/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin%20marketplace-d97757)
![Node](https://img.shields.io/badge/node-%3E%3D18-339933)

</div>

---

## Quick start

Run this in Claude Code (v2.1.275 or later):

```
/plugin install army --marketplace omer-yehuda/plugins
```

<details>
<summary>Older Claude Code versions</summary>

```
/plugin marketplace add omer-yehuda/plugins
/plugin install army@omer-plugins
```
</details>

Restart Claude Code (or run `/reload-plugins`), then type:

```
raise the army build a landing page for my habit-tracking app
```

To update later, run `/plugin marketplace update omer-plugins`.

## Plugin catalog

| Plugin | What it does | Version |
|---|---|---|
| [**army**](plugins/army/README.md) | Multi-agent orchestration. A Chief of Staff commands 14 specialist units (intel, engineering, defense, legal, comms and more) as subagents. Includes cost-aware model routing, safety gates and local lessons-learned memory. | 1.0.0 |

---

## Featured: Army

> Give Claude a mission, not a prompt.

Say **"raise the army"** and Claude becomes a Chief of Staff. It asks its briefing questions once, writes an operation order, and dispatches specialist units in parallel, each on the most cost-effective model for its job. An independent Inspector General checks the result against your requirements before anything is reported back.

```mermaid
flowchart LR
    U([You]) -->|mission| HQ{{Chief of Staff}}
    HQ -->|briefing questions, once| U
    HQ --> R[Recon]
    HQ --> O[Ops & Planning]
    HQ --> I[Intel]
    HQ --> E[Engineering]
    HQ --> D[Defense]
    HQ --> L[Legal]
    HQ --> C[Comms]
    HQ --> X[UX · Logistics · Treasury · Growth · Rescue]
    R & O & I & E & D & L & C & X -->|SITREP| HQ
    HQ --> IG[Inspector General]
    IG -->|verdict| HQ
    HQ --> H[History: lessons learned]
    HQ -->|final report| U
```

### Highlights

- **14 specialist units, 40+ specialist playbooks:** competitor research, unit and E2E testing, OWASP review, secrets scanning, OSS license and privacy-law checks, UX copy, Hebrew/RTL localization, CI/CD, SEO/ASO and more.
- **Cost-aware model routing:** a `lean` profile for the Pro plan (Sonnet and Haiku only) and a `full` profile for the Max plan (Opus for critical units). Switch with `/army:mode`.
- **Token discipline by design:** units write full reports to disk and return SITREPs of at most 200 words. The codebase map is cached per commit, and playbooks load only on demand.
- **Safety gates:** during a mission, a `PreToolUse` hook asks for approval before pushes, deploys, publishing, deletions, data drops and new dependencies. Toggle with `/army:gates`.
- **Learns per project:** a local `.army/lessons.md` file is read at the start of every mission. It is never committed to git.
- **Turbo mode:** `raise the entire army` (or `all units on board`) engages every unit.

See the full documentation in [plugins/army/README.md](plugins/army/README.md).

---

## Privacy & safety

- **No telemetry.** Plugins in this marketplace send nothing anywhere on their own.
- **Local memory only.** Project memory lives in `.army/` inside your project, and is excluded from git automatically through `.git/info/exclude`. Per-user settings live in Claude Code's plugin data directory.
- **Human in the loop.** Irreversible actions require your approval by default.
- **Defensive security only.** The red-team specialist is restricted to your own project in a local or test environment.
- The legal unit produces an automated risk review, **not legal advice**.

## Repository structure

```
.claude-plugin/marketplace.json   Marketplace catalog
plugins/
  army/
    .claude-plugin/plugin.json    Plugin manifest
    skills/                       raise · raise-all · mode · gates · status
    agents/                       14 unit subagents
    doctrine/                     Specialist playbooks, loaded on demand
    hooks/hooks.json              Safety gate hook
    scripts/army.js               Zero-dependency control script
    tests/                        Safety gate tests
templates/plugin-template/        Scaffold for new plugins
tools/                            Maintenance scripts
.github/workflows/validate.yml    CI: manifest validation + tests
```

## Contributing a new plugin

1. Scaffold it: `cp -r templates/plugin-template plugins/<name>`
2. Edit `plugins/<name>/.claude-plugin/plugin.json` (kebab-case name, description, version).
3. Add skills (`skills/<skill>/SKILL.md`), agents (`agents/*.md`) and hooks (`hooks/hooks.json`) as needed.
4. Register it in `.claude-plugin/marketplace.json`:
   ```json
   { "name": "<name>", "source": "./plugins/<name>", "description": "..." }
   ```
5. Validate it:
   ```bash
   claude plugin validate .
   claude plugin validate plugins/<name>
   ```
6. Try it locally: `claude --plugin-dir plugins/<name>`
7. Bump `version` in `plugin.json` for every release. Users stay on a pinned version until it changes.

Plugin names must not start with `claude-` or `anthropic-`, because those prefixes are reserved.

## Development

```bash
node --test plugins/army/tests/gate.test.js   # safety gate test suite
node tools/sync-standing-orders.js            # run after editing doctrine/shared/standing-orders.md
claude plugin validate .                      # validate the marketplace
```

CI runs all of the above on every push and pull request.

## License

[MIT](LICENSE) © 2026 Omer Yehuda
