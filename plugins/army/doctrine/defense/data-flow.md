# Personal-data mapper

Goal: a precise, technical map of what personal data the system collects, where it flows, and who can see it. Legal uses this map for compliance.

## Method
1. Find the collection points in code: forms, sign-up, OAuth scopes, analytics events, cookies/localStorage, device APIs (location, contacts, camera), uploads, logs, error trackers.
2. Trace each data type: client → API → database tables/columns → backups → third parties (SDKs, AI APIs, email providers, payment processors) → exports.
3. For each store: encryption at rest, access control (which roles and services can read it), retention and deletion behavior.
4. Find leaks: personal data in URLs or query strings, logs, analytics properties, error reports, AI prompts, or client-side bundles.
5. Check that deletion is real: when a user deletes their account, what remains, and where?

## Output
A data inventory table (data type · sensitivity · collected where · stored where · shared with · retention · access), a Mermaid flow diagram, and the leaks found with fixes. Hand it to legal/privacy.
