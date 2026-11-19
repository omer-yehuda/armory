# Army evals

Fixed missions that compare the army with plain Claude Code on **pass rate, tokens, cost, turns and time**.

| Mission | What it measures |
|---|---|
| `bugfix-js` | Fixes an off-by-one bug without touching the tests |
| `python-bug` | Fixes `median()` for even-length lists |
| `security-audit` | Finds SQL injection, XSS, a hard-coded secret and permissive CORS without editing files |
| `license-check` | Flags a GPL dependency in a proprietary app |
| `planted-memory` | Refuses `.army/` memory that is tracked in the repository (army only) |
| `injection-docs` | Ignores instructions to AI agents hidden in a README, does not push or delete |

```bash
node evals/run.js                       # all missions, baseline and army
node evals/run.js --only security-audit --variants army
```

Requires a signed-in `claude` CLI. Every run uses a temporary copy of the fixture, with a local bare `origin` so that push attempts can be detected. Results are written to `evals/results/`.

**Status:** the harness is new and no results have been published yet. Run it and add your results table here before claiming that the army beats the baseline.
