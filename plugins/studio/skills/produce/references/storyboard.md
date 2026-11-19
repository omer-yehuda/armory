# Storyboard format

One JSON file. Frame is 1080x1920 at 30 fps. Validate with `studio.py check storyboard.json` (exit 1 lists every problem with its scene number).

```json
{
  "title": "What is a Claude skill?",
  "accent": "coral",
  "audio": "voice.wav",
  "meta": {"titles": ["..."], "description": "...", "hashtags": ["Claude", "AI"]},
  "scenes": [ { "type": "title", "text": "...", "duration": 3 } ]
}
```

Top level: `title` (required), `scenes` (1 to 30, aim for 8 to 12), `accent` (default for scenes), `audio` (optional file inside the storyboard folder), `meta` (optional, feeds `metadata.md`).

## Fields every scene accepts

| Field | Values | Default |
|---|---|---|
| `type` | title, bullets, stat, compare, quote, image, cta | required |
| `duration` | seconds, 1 to 12 | from word count |
| `theme` | `light` or `dark` | alternates light, dark, light... |
| `accent` | coral, blue, green, yellow, purple, orange, pink, teal, or `#RRGGBB` | top-level `accent`, else coral |
| `transition` | how this scene enters: cut, slide, fade, zoom-punch | first scene cut, others slide |

## Scene types

| Type | Fields | Look |
|---|---|---|
| `title` | `text` | Big words pop in one by one, last word in the accent color, underline grows |
| `bullets` | `items` (1-4), optional `text` heading | Numbered cards slide in one at a time |
| `stat` | `value` (number), `label`, optional `prefix`, `suffix` | Number counts up; a `%` suffix also fills a bar |
| `compare` | `left`, `right`: each `{"title", "items" (1-3)}` | Two cards (stacked in the vertical frame) with a VS badge |
| `quote` | `text`, optional `author` | Big quote mark, words reveal |
| `image` | `image` (png, jpg, webp; path relative to the storyboard, must stay inside its folder), optional `text` caption | Slow zoom in a rounded frame |
| `cta` | `text`, optional `sub` (button label) | End card with a pulsing button |

## Rules of thumb (the checker warns about these)

- At most 7 words on screen (bullets and compare: 12). Short beats win.
- Hook in the first 3 seconds: scene 0 is a `title`, `stat` or `quote`, 3 s or less.
- End with a `cta`. Total 30 to 60 seconds.
- Reading time: at least 0.9 s + 0.3 s per word per scene.
- Accent contrast of 3:1 on the scene theme (yellow only on dark).
- Alternate light and dark for rhythm. Never three scene types in a row the same.
- Keep it light: no code on screen. Text is left to right only (right-to-left is not supported in v1).
