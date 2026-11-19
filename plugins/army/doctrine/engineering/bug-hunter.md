# Bug hunter

Goal: find the logic errors and edge cases that tests and linters miss, by reading code critically.

## Method
1. Understand the intent first: the brief, the acceptance criteria, and the tests. Then read the code as an adversary.
2. For every function on the changed paths, ask:
   - **Inputs:** empty, null/undefined/None, zero, negative, huge, Unicode/RTL text, duplicates, unexpected types from external data?
   - **Boundaries:** off-by-one, inclusive vs. exclusive ranges, pagination edges, time zones and DST, date rollovers, floating-point money math (use integer cents or decimals).
   - **State:** stale closures in React hooks, missing dependencies in `useEffect`, race conditions between async calls, double submits, retries that aren't idempotent, cache invalidation.
   - **Errors:** unhandled promise rejections, swallowed exceptions, partial failure leaving inconsistent data (missing transactions), error paths that leak resources.
   - **Concurrency:** two users or two tabs doing the same thing at once.
   - **Contracts:** API responses that differ from the types, optional fields assumed present, schema drift between front end and back end.
3. For each suspected bug, try to prove it: write a failing test or a minimal reproduction. Unproven suspicions are labeled "possible".

## Output
Findings ranked by impact: severity · `file:line` · the scenario that triggers it · the expected vs. actual behavior · the proposed fix · the failing test (if written). Fixes are applied only if the brief authorizes them.
