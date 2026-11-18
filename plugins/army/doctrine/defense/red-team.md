# Red team (own project only)

Goal: attack the user's own application the way a motivated attacker would, and prove which defenses fail.

## Rules of engagement (mandatory)
- Target ONLY the user's own project, running locally or in a test environment the brief names. Never touch production, third-party systems, or other people's services.
- No denial-of-service, no destructive actions against data you didn't create, and no real user data.
- Use test accounts you create locally. Stop and hand back if you find yourself needing anything outside these limits.

## Playbook
1. Map the attack surface from recon and the code: routes, API endpoints, server actions, file uploads, webhooks, auth flows, admin areas, LLM features.
2. Try, against localhost:
   - **Auth bypass:** call protected endpoints without a token, with an expired or modified token, or with another user's token.
   - **IDOR:** change IDs in URLs and bodies to access other users' objects.
   - **Mass assignment:** add `role`, `isAdmin`, `price` or `ownerId` fields to requests.
   - **Business logic:** negative quantities, coupon reuse, race conditions (parallel requests for single-use actions), skipping steps in multi-step flows.
   - **Input attacks:** XSS payloads in every stored field, SQL/NoSQL injection probes, path traversal in file parameters, oversized payloads within reason.
   - **Upload:** wrong MIME types, double extensions, SVG with scripts.
   - **LLM features:** prompt injection through user content, attempts to extract the system prompt, tool misuse.
3. For each successful attack, record the exact request or steps to reproduce, the impact, and the fix.

## Output
Attack log (attempt · result · evidence), confirmed vulnerabilities with reproduction steps, and recommended regression tests for engineering.
