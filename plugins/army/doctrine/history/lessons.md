# Lessons keeper

Goal: `.army/lessons.md` makes every future mission in this project faster and better. HQ reads it at the start of each mission, so every line costs tokens. Keep it sharp.

## Input
The mission directory (opord.md, unit reports, inspector-general verdict). Read the SITREPs and the verdict first. Open the full reports only to confirm a lesson.

## What counts as a lesson
- Project facts that took effort to discover: "Tests need `DATABASE_URL` from `.env.test`; run with `pnpm test:ci`".
- User preferences revealed in the briefing or the corrections: "User prefers Tailwind over CSS modules", "Copy for this product: informal tone, plural Hebrew forms".
- Mistakes and how to avoid them: "Playwright tests fail without `pnpm build` first".
- Decisions to remember: "Chose Postgres over Mongo (see ADR-002); don't relitigate".
- Recurring risks: "The auth middleware matcher excludes /api/admin/*. Check it on every auth change".

## Not lessons
Mission narration, one-off details, things obvious from the code or the recon file, secrets, personal data, long code blocks.

## Format (keep the whole file under ~100 lines)
```
# Army lessons: <project name>
_Last updated: <date> · missions: <n>_

## Project facts
- ...
## User preferences
- ...
## Pitfalls
- ...
## Decisions
- ...
```

## Maintenance on every update
- Add the new lessons, one line each, specific and actionable.
- Merge duplicates. Update lessons the new mission contradicted. Delete lessons that no longer apply.
- If the file exceeds ~100 lines, prune the least useful lines.
