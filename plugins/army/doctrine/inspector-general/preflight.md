# Preflight checker

Goal: right before release, upload or publication, catch what would embarrass us or get the release rejected.

## Software release
- The build passes from a clean checkout. Tests, typecheck and lint pass. The version number and changelog are updated.
- Environment variables documented and set for the target environment. No debug flags, test keys or `console.log` noise in production.
- Database migrations reviewed and reversible. A rollback plan exists.
- Error tracking and monitoring active.
- The key user flows were checked on production-like data.

## Web and content
- Every link works. Meta tags, Open Graph images and the favicon are present. 404 page exists.
- Images optimized with alt text. Fonts licensed. Spelling and grammar checked.
- Legal pages linked (privacy, terms, accessibility statement where required). Cookie consent works.

## App store submission
- Screenshots in the required sizes, the listing text, the privacy label / data safety form matches reality, a demo account for reviewers if login is required, the age rating, and in-app account deletion.

## Print or files
Correct dimensions, resolution, color mode, embedded fonts, bleed and margins where relevant.

## Output
A checklist with PASS / FAIL / N/A for each item and evidence. Any FAIL on a blocking item makes the status RED.
