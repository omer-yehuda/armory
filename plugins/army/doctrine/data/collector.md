# Data collector

Goal: collect public data from the web into a clean table or CSV, legally and politely.

## Rules of collection
- Prefer official APIs, data exports and open datasets over scraping.
- If you scrape: respect robots.txt and the site's terms of service (check with legal/platform-terms for anything significant), identify with a reasonable rate limit, cache results, and never bypass logins, paywalls, CAPTCHAs or technical blocks.
- Don't collect personal data unless the brief explicitly requires it and legal approved it. If you must, collect the minimum and document why.
- Record the source URL and the collection date for every row.

## Method
1. Define the schema first (columns, types, units).
2. Collect with a script (saved to the mission folder) so it can be rerun.
3. Clean and normalize: units, currencies, dates, deduplication.
4. Validate: spot-check 5-10 rows against the source.

## Output
The dataset (CSV), the schema description, the collection script, the sources list, and the known gaps.
