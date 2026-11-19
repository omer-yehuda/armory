# Consistency checker

Goal: names, numbers, dates, terms and facts match across every file and version of the deliverable.

## Method
1. List the deliverables and related files (code, docs, copy, configuration, store listings, legal documents).
2. Extract the key facts: product name and spelling, prices and plans, feature names, limits and quotas, dates, version numbers, contact details, URLs, supported platforms and languages.
3. Compare each fact across all locations (Grep helps). Check that the copy matches the actual behavior in code (for example the "free plan includes 3 projects" text vs. the enforced limit in code).
4. Check that the legal documents match reality (the privacy policy vs. actual data collection, the terms vs. actual pricing).
5. Check the terminology against the glossary, if there is one.

## Output
An inconsistency table (fact · location A says · location B says · which is correct, if known · fix).
