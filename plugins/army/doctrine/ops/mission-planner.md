# Mission planner

Goal: an operation order that HQ can dispatch without further thinking.

## Steps
1. Restate the objective and the definition of done as 3-8 testable acceptance criteria.
2. List the assumptions and open risks. For each risk, state its mitigation, or "accept".
3. Break the work into work packages of 0.5-1 day of agent work each. A package has one owner unit, clear inputs, a clear output, and a way to verify it.
4. Order the packages by dependency. Mark which can run in parallel. Parallel engineering packages must touch disjoint files or modules.
5. Assign units and models (lean or full, as given in the brief). Note the units you deliberately left out.
6. Draft a brief for each package in the HQ brief format (`doctrine/shared/brief.md`).
7. Define the checkpoints: after which phase defense, legal or ux reviews happen.

## Output (report file)
- Objective, definition of done, assumptions, risks
- Phase table: phase · packages · unit · depends on · parallel? · verify by
- Draft briefs
- Out of scope (explicit)

## Anti-patterns
- Phases without a verifiable output
- "Research everything first" with no question to answer
- Over-planning a small mission. For fewer than 3 packages, a short list is enough.
