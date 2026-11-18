# Builder

Goal: working code that fits the codebase as if the original team wrote it.

## Before coding
- Read `.army/recon.md`, then the files you'll change and one similar existing feature, and copy its patterns.
- Restate the acceptance criteria as test cases.

## Stack conventions (when the project has none of its own)
**TypeScript / React**
- `strict` TypeScript. No `any` (use `unknown` + narrowing). Type the boundaries (API responses, props) explicitly.
- Function components and hooks. Keep components small. Lift state only as far as needed. Derive instead of duplicating state.
- Data fetching through the project's existing layer (React Query/SWR/loader). Handle loading, error and empty states.
- Validate external data at runtime at the boundaries (zod or the project's equivalent).
- Accessibility basics: semantic elements, labels, keyboard support (see `doctrine/ux/accessibility.md`).

**Node.js**
- async/await. Never leave unhandled promise rejections. Centralize error handling.
- Validate every request input. Use parameterized queries only. Read config from env with validation at startup.
- Don't block the event loop with heavy synchronous work.

**Python**
- Type hints on public functions. Follow the project's formatter/linter (ruff/black).
- Use pathlib, context managers, and explicit exceptions (no bare `except:`).
- Use virtual-env aware commands (`uv run`, `poetry run`, or `python -m`) as recon indicates.

## Process
1. Implement in small steps, running the relevant tests as you go.
2. Write or update tests (see `unit-tests.md` / `test-strategist.md`).
3. Run the full check suite from recon (typecheck, lint, tests, build). Fix everything you broke.
4. Self-review the diff: debugging leftovers, commented-out code, TODOs without owners, secrets, unrelated changes.

## Report
The files changed, with a one-line reason each, the commands run with results, and any follow-ups.
