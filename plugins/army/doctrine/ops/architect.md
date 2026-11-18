# Architect

Goal: the simplest architecture that meets the requirements and survives the next 12 months of growth.

## Steps
1. Write down the requirements that drive the architecture: users and scale, latency, offline needs, real-time needs, data sensitivity, budget, team skills, platform (web, mobile, desktop).
2. Start from the existing stack in `.army/recon.md`. For a new project, default to boring, popular choices:
   - Web front end: React + TypeScript (Vite or Next.js, depending on SEO/SSR needs)
   - Back end: Node.js (TypeScript) or Python (FastAPI), matching the team's code
   - Database: PostgreSQL by default; SQLite for local or single-user apps
   - Auth: a managed provider or a proven library. Never hand-rolled crypto.
3. Define the components and their boundaries, the data model (main entities and relations), the API surface (main endpoints or events) and where state lives.
4. For each significant decision, write an ADR: context, options (2-3), decision, consequences. Use `doctrine/history/documentation.md` for the format.
5. Identify the trust boundaries and sensitive data flows, and pass them to defense (HANDBACK note).
6. Draw the system in a Mermaid diagram in the report.

## Checks before handing off
- Can a single developer run it locally with one command?
- What breaks at 10x usage, and is that acceptable for now?
- Is every external dependency (API, SaaS) replaceable, or knowingly locked in?
- Does the cost at the expected scale fit the budget? If not, hand it to treasury.
