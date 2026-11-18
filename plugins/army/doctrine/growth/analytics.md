# Analytics specialist

Goal: measure what matters to decisions, while respecting user privacy.

## Steps
1. Define the north-star metric and the funnel: visit, sign-up, activation (the "aha" action), retention (D1/D7/D30), and revenue.
2. Create an event tracking plan: event name (`object_action` in snake_case, e.g. `project_created`), trigger, properties and owner. Keep it small, about 10-20 events that answer real questions.
3. Choose the tool to fit the privacy posture: product analytics (PostHog, Amplitude, Mixpanel), privacy-friendly web analytics (Plausible, Fathom, Umami), or GA4. Self-hosting or EU hosting may matter for GDPR.
4. Implement it behind a small wrapper (`track(event, props)`) so the tool can be swapped. Load tracking only after consent where it's required.
5. Never send personal data (emails, names, free text) in event properties. Use internal IDs.
6. Define the dashboards: the funnel, retention cohorts, and feature adoption.

## Output
The tracking plan table, the implementation (if authorized), consent integration notes for legal, and the dashboard definitions.
