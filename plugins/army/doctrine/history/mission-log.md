# Mission chronicler

Goal: a short, searchable record of every mission.

Write `<missionDir>/log.md` (at most 40 lines):

```
# Mission <missionId>
Mission: <one line>
Mode: <lean|full> · Turbo: <yes|no> · Date: <date>
Outcome: <GREEN/AMBER/RED> - <one line>

## Units engaged
<unit> (<model>) - <one-line result>

## Delivered
- <path or artifact>

## Open items
- <RED/AMBER items still open>

## Decisions made by HQ
- <decision> - <reason>
```

Also append one line to `.army/missions/index.md`:
`<missionId> · <outcome> · <one-line mission>`

Don't copy report contents. Link the paths instead.
