# Brief format (HQ to unit)

Units start with no memory of the conversation. Everything they need is in the brief, or in a file the brief points to.

```
MISSION ID: <missionId>
UNIT: <unit>   SPECIALISTS: <playbooks to load, e.g. appsec, secrets>
OBJECTIVE: <1-2 sentences: the outcome, not the activity>
CONTEXT:
  - <facts from the briefing that matter to this unit>
  - Recon: .army/recon.md            (code missions)
  - Related reports: <paths>          (never paste their content)
SCOPE:
  In:  <areas / files / questions>
  Out: <what not to touch or research>
CONSTRAINTS: <stack, audience, markets, language, deadline, budget, conventions>
AUTHORITY: may modify files: yes|no. Irreversible actions are never authorized: hand them back.
DELIVERABLE: <what exists when the unit is done>
REPORT: write the full report to <missionDir>/<unit>.md and return a SITREP only.
```

Good brief checklist:
- The objective is testable ("all endpoints validate input and return 4xx on bad data"), not vague ("improve security").
- The scope is explicit, so parallel units don't collide on the same files.
- It names the specialists to load, so the unit doesn't read playbooks it doesn't need.
- Turbo briefs to marginal units are short: "Scan for anything in your domain relevant to X. If none, reply NO FINDINGS."
