# Changelog

## 1.0.0 (2026-11-19)

- `/critics:taste`: three independent critics (presentation, kitchen, recipe) score your work 0-3 stars, a head critic merges the cards into one review.
- `/critics:retaste <id>`: critics re-check only their send-back items and show stars before -> after.
- `/critics:menu`: explains the rubric.
- `scripts/critics.js`: `open`, `list`, `stars` (zero dependencies, protects `.critics/` with its own `.gitignore`).
- Security: no user text on any command line (`open --input-file`, ids made by the script), planted-state checks on `list` and `stars`, symlinked state folders refused.
