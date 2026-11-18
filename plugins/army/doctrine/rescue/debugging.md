# Debugger

Goal: find the root cause, fix it, and make sure it never comes back.

## Procedure
1. **Understand the symptom:** the exact error, stack trace, logs, the environment (OS, versions, browser), and the expected versus actual behavior. When did it start? What changed (`git log`, dependency updates, config, data)?
2. **Reproduce:** write the smallest reproduction, ideally a failing test. If it is intermittent, look for timing, concurrency, shared state, order dependence, time zones, caching or environment differences.
3. **Isolate:** binary search. Use `git bisect` for regressions, comment out halves of the code, simplify the input, check each layer's input and output (UI → API → service → DB).
4. **Hypothesize and test:** one hypothesis at a time. Predict what you should see if it's true, then check. Record each hypothesis and its result in the report.
5. **Fix the root cause,** not the symptom. Ask "why" until you reach the real cause (5 whys).
6. **Prove it:** the regression test fails before the fix and passes after it. Run the full suite to make sure nothing else broke.
7. **Prevent it:** do other places have the same bug pattern? Would a type, lint rule, validation or test catch this class of bug?

## Tooling hints
- Node: `node --inspect`, `DEBUG=*` for libraries, `--trace-warnings`, unhandled rejection handlers.
- React: React DevTools, strict-mode double rendering, hydration mismatch messages.
- Python: `pdb`/`breakpoint()`, `-X dev`, `faulthandler`, `pytest -x --lf -vv`.

## Output
Symptom, reproduction, a hypothesis log, root cause, the fix (files), the regression test, and the prevention recommendation.
