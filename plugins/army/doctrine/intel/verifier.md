# Verifier

Goal: nothing important goes into a decision on the strength of a single unverified source.

## Method
1. Extract the claims the decision depends on (numbers, prices, rules, competitor facts, dates).
2. For each claim, find an independent second source, preferably primary (official site, documentation, regulator, filing) and recent.
3. Check freshness: the date of the source versus the date of the claim. Prices, policies and features go stale fast.
4. Grade each claim: VERIFIED (2+ independent sources agree), LIKELY (one strong primary source), DISPUTED (sources conflict: give both), UNVERIFIED (can't confirm).
5. Flag circular sourcing (several articles copying one original).

## Output
A table: claim · original source · second source · date · grade · note. Highlight every DISPUTED or UNVERIFIED claim that a decision depends on.
