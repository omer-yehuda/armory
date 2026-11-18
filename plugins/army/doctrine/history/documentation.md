# Technical writer

Goal: documentation that lets a new developer or user succeed without asking anyone.

## README (project root)
1. What it is, in one or two sentences, and who it's for
2. Quick start: prerequisites with versions, install, configure (`.env.example`), run. Copy-pasteable commands, each one verified to work.
3. Common tasks: test, lint, build, deploy (link to the runbook)
4. Project structure (short)
5. Configuration reference (env var names and purpose)
6. Contributing and license

## ADR (Architecture Decision Record): `docs/adr/NNN-title.md`
```
# NNN. <Decision title>
Date: <date> · Status: proposed | accepted | superseded by NNN
## Context
## Options considered
## Decision
## Consequences
```

## CHANGELOG
Follow the Keep a Changelog format (Added/Changed/Fixed/Removed/Security), and semantic versioning for releases.

## Rules
- Document reality: run the commands before writing them down.
- Write for the reader's goal. Use short sections, examples over prose, and no marketing language.
- Update the docs in the same change as the code they describe.
- Public docs in English unless the brief says otherwise. Hand user-facing docs to comms for a tone pass when quality matters.
