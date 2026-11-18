# Tech scout

Goal: find the technology that gives us an edge, and avoid technology that slows us down.

## Steps
1. Infer what competitors are built on: job posts, public tech stacks, network requests visible on their site, open-source repos, engineering blogs.
2. For each key capability the product needs, list 2-3 candidate libraries, APIs or services. Check for each:
   - maintenance (last release date, open issues trend, maintainers)
   - adoption (weekly downloads, stars), license (pass doubts to legal)
   - fit with the stack (React/TS, Node, Python), bundle size or performance
   - pricing and lock-in for SaaS/APIs
3. Flag deprecated or risky options.
4. Spot opportunities: new APIs, models or platform features competitors haven't adopted yet.

## Output
- Capability → recommended option → alternatives → reason (table)
- Risks (abandoned packages, license issues, vendor lock-in)
- Every version and price verified via web search and dated
