# Army: a chief of staff and specialist units for Claude Code

Say **"raise the army"** and Claude becomes a Chief of Staff (HQ). It asks you its briefing questions once, then plans the mission and dispatches specialist units as subagents, each on the most cost-effective model for its job. It runs to completion on its own, and stops only at the safety gates.

## Install

```
/plugin install army --marketplace omer-yehuda/plugins
```

On Claude Code versions earlier than 2.1.275, run `/plugin marketplace add omer-yehuda/plugins` first, then `/plugin install army@omer-plugins`.

## Commands

| Say / run | What happens |
|---|---|
| `raise the army <mission>` · `/army:raise <mission>` | HQ engages only the units the mission needs |
| `raise the entire army <mission>` · `all units on board` · `/army:raise-all <mission>` | Turbo: every unit is engaged |
| `/army:mode lean` · `/army:mode full` | Switch model profile (lean = Pro-friendly, the default; full = Max) |
| `/army:gates on` · `/army:gates off` | Safety gates before irreversible actions (default: on) |
| `/army:status` | Mode, gates, active mission, memory size |

You can also call a single unit directly: "send the defense unit to audit the auth flow".

## Order of battle

| Unit | Specialists | full | lean |
|---|---|---|---|
| **HQ** (`raise`) | Chief of Staff: briefing, planning, dispatch, integration | main session model | main session model |
| `recon` | Codebase mapping (cached per commit) | haiku | haiku |
| `ops` | Mission planner, architect | opus | sonnet |
| `intel` | Competitor analyst, market analyst, audience listener, tech scout, strategist | sonnet | sonnet |
| `comms` | UX copy, marketing copy, localization (Hebrew/RTL), plain-language legal | sonnet | sonnet |
| `engineering` | Builder, test strategist (integration/E2E), unit tests, optimizer, clean code, dependencies | sonnet | sonnet |
| `ux` | UX review, accessibility (WCAG 2.2), design consistency | sonnet | sonnet |
| `defense` | AppSec, secrets, supply chain, threat model, red team (own project only) | opus | sonnet |
| `legal` | Licenses & copyright, privacy, terms & policies, accessibility law, trademarks, AI compliance | opus | sonnet |
| `logistics` | CI/CD, deployment, infra cost, observability | sonnet | haiku |
| `treasury` | Pricing & business model, cost forecast | sonnet | haiku |
| `growth` | SEO, ASO, launch, analytics | sonnet | haiku |
| `rescue` | Debugging, incident response | opus | sonnet |
| `inspector-general` | Independent final acceptance check (judges cold) | opus | sonnet |
| `history` | Lessons learned, mission log, documentation | haiku | haiku |

**Why this structure:** in Claude Code, only the main session can launch subagents. So each unit is one subagent, and its specialists are playbooks (`doctrine/`) that the unit reads only when its brief needs them. This keeps every unit's context small, which saves tokens.

**Token savings built in:**
- Units write full reports to disk and return a SITREP of at most 200 words to HQ.
- Recon is cached per git commit, and the lessons file stays under ~100 lines.
- Lean mode routes heavy units to Sonnet and light ones to Haiku.
- Specialist playbooks load on demand.

Tip: in full mode, run the main session on Opus (`/model opus`), because HQ uses the main session's model.

## Memory (local only)

Each project gets a `.army/` folder:

```
.army/
  state.json        active mission flag (used by the safety gate)
  recon.md          codebase map, cached per commit
  lessons.md        lessons learned, read by HQ at the start of every mission
  missions/<id>/    operation order, unit reports, mission log
```

`.army/` is added to `.git/info/exclude` automatically. It is never committed and `.gitignore` is not touched. Your settings (mode, gates) are stored per user in the plugin's data directory.

## Safety gates

With gates **on** (the default), HQ asks before irreversible actions. During an active mission, a `PreToolUse` hook also enforces this for shell commands. It asks for approval before:

- `git push`, history rewrites and discarding changes
- deleting files
- deployments (Vercel, Netlify, Firebase, Fly, Kubernetes, Terraform, and more)
- publishing packages
- dropping data and running schema migrations
- installing new dependencies

Outside an army mission the hook does nothing.

## Requirements

Claude Code with plugin support, and Node.js 18+ (used by the control script and the hook).
