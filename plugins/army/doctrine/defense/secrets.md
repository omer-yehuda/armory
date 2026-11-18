# Secrets hunter

Goal: no credential is exposed in code, git history, config, logs or client bundles.

## Scan
1. If `gitleaks` or `trufflehog` is already installed, run it on the working tree and history (`gitleaks detect --source . -v`, `gitleaks git`). Don't install them: recommend them as a HANDBACK item.
2. Otherwise, grep for high-signal patterns (exclude lockfiles, node_modules and build output):
   - `AKIA[0-9A-Z]{16}` (AWS), `ghp_|gho_|github_pat_` (GitHub), `sk-[A-Za-z0-9_-]{20,}` (OpenAI/Anthropic-style), `sk_live_|rk_live_` (Stripe), `xox[baprs]-` (Slack), `AIza[0-9A-Za-z_-]{35}` (Google), `-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY`, `eyJhbGciOi` (hardcoded JWTs), connection strings with passwords (`postgres://user:pass@`, `mongodb+srv://`)
   - assignments like `(api[_-]?key|secret|token|password)\s*[:=]\s*['"][^'"]{8,}`
3. Check git history for files that were committed and later deleted: `git log --all --diff-filter=D --name-only -- '*.env*' '*.pem' '*.key'` and `git log -p -S '<pattern>'` for suspects.
4. Check that `.gitignore` covers `.env*` (except `.env.example`), key files and credentials JSON.
5. Client exposure: env vars with public prefixes (`NEXT_PUBLIC_`, `VITE_`, `REACT_APP_`, `EXPO_PUBLIC_`) must hold only non-secret values. Built bundles (`dist/`, `.next/static`) must not contain secrets.
6. CI config: secrets referenced from the secret store, not inline. No `echo` of secrets in logs.

## Reporting
- Never write a full secret into the report. Show the type, the location and the first 4 characters only.
- A leaked live secret is CRITICAL. The fix order is: **rotate or revoke first** (HANDBACK, because it involves the provider), then remove it from the code, then consider a history rewrite (HANDBACK, because it is irreversible) and invalidating caches and forks.
- Recommend preventive controls: a pre-commit hook (gitleaks), GitHub push protection, and `.env.example` with placeholder values.
