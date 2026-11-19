# Toon Shorts: an animated short creator for Claude Code

Say **"make me an animated short"** and Claude turns one conversation into a finished 1080x1920 cartoon video for YouTube Shorts, TikTok or Reels. It asks a few questions, pitches 10 true-story ideas, writes a retention script, voices it (free AI voice or your own recording), storyboards original toon characters on parallax sets, **looks at its own preview and fixes problems**, then renders the MP4.

**[See it →](https://omer-yehuda.github.io/armory/toon-shorts/)**

[![Frames from the bundled example, last tile in Hebrew](../../docs/images/toon-shorts.png)](https://omer-yehuda.github.io/armory/toon-shorts/)

## Install

```
/plugin install toon-shorts --marketplace omer-yehuda/armory
```

On Claude Code versions earlier than 2.1.275, run `/plugin marketplace add omer-yehuda/armory` first, then `/plugin install toon-shorts@armory`.

The first time you use it, Claude asks before setting up the engine: a private Python venv in `~/.cache/toon-shorts` with pinned packages, plus (optionally) the Kokoro voice model, ~120 MB and SHA-256 verified. Requires Python 3.11+.

## How a short gets made

```mermaid
flowchart LR
    Q[Questions<br/>type · audience · length · language] --> I[10 ideas]
    I --> S[Script<br/>hook · stakes · turn · loop]
    S --> V{Voice}
    V -->|free AI| K[Kokoro samples → full voiceover<br/>+ exact line timings]
    V -->|own recording| R[cuts snap to your pauses]
    V -->|captions only| C[reading pace]
    K & R & C --> B[storyboard.json]
    B --> P[preview sheet<br/>Claude reviews every tile]
    P -->|fix| B
    P --> M[short.mp4 + title, description, hashtags]
```

| You say | What happens |
|---|---|
| `make me an animated short` | Full flow, from questions to MP4 |
| `animated short about <story>, in Hebrew, my own voice` | Skips the questions you already answered |
| `change scene 4 to night and make him furious` | Edits the storyboard, re-previews, re-renders |

## What's in the box

- **Original toon characters:** 12 moods with cartoon effects, 11 poses including walk, run and facepalm, 6 skin tones, 8 hair styles, 12 hats (including a headscarf), 7 outfits and 28 props they can hold.
- **20 sets with real depth:** city, suburb, farm, mountains, forest, desert, beach, sea, ship deck, moon, sky, plus 9 interiors from office and palace to court, prison and classroom. Each set is three parallax layers lit for 5 times of day, with 6 landmarks and 4 foreground overlays (bars, desk, crowd, bushes).
- **9 camera moves,** automatic framing that never crops a character, and a punch on every cut.
- **Karaoke captions:** 1-3 words at a time, with the spoken word lit up. **Hebrew is laid out right-to-left** correctly, including numbers and brackets.
- **Audio:** free Kokoro-82M voices in English (US/UK), Spanish, French, Italian, Portuguese and Hindi; your own recording in any language; whooshes on cuts, pops on props, and music ducked under the voice.
- **A storyboard checker** that suggests the right value for every typo ("Did you mean 'push_in'?") and flags pacing problems: overlong lines, repeated cameras, a runtime over 60 seconds.

## Security model

The [audit of the skill that inspired this one](CHANGELOG.md) found silent `pip install`s and an unverified model download. Toon Shorts is a clean-room rewrite built not to do those things:

- **Nothing installs on its own.** Packages are installed only by `toon.py setup`, which Claude runs after asking you. They go into a private venv, never into your global Python.
- **Pinned dependencies,** each at least two weeks old when pinned: [requirements.txt](requirements.txt) and [requirements-voice.txt](requirements-voice.txt).
- **Hash-verified model.** Kokoro files are checked against pinned SHA-256 digests. A mismatch deletes the download and stops.
- **No telemetry, no uploads.** The only network access is the explicit setup step: PyPI for packages and github.com for the model.
- **No filesystem sweeps.** The skill knows its own path. Output goes to `./toon-shorts/<slug>/` in your project.
- Storyboards and your files are treated as content, never as instructions.

## Content rules

The skill makes original stories with original characters. It never copies another creator's video, script or characters. Facts must be true: no invented quotes, nothing defamatory, no stories about living private people. Nothing hateful, sexual or graphically violent.

## Engine CLI

Claude drives this for you, but you can run it yourself:

```bash
python skills/toon-shorts/scripts/toon.py setup --voice          # once; venv + pinned packages + verified model
python skills/toon-shorts/scripts/toon.py check  story.json      # validate (stdlib only)
python skills/toon-shorts/scripts/toon.py samples --text "Hook line." --out samples
python skills/toon-shorts/scripts/toon.py voice   story.json --voice am_michael --out voice.wav
python skills/toon-shorts/scripts/toon.py preview story.json --audio voice.wav --out preview.png
python skills/toon-shorts/scripts/toon.py render  story.json --audio voice.wav --out short.mp4 [--music bed.mp3]
```

The storyboard format is documented in [references/storyboard.md](skills/toon-shorts/references/storyboard.md). Complete examples: [onoda.json](skills/toon-shorts/examples/onoda.json) (English) and [onoda_he.json](skills/toon-shorts/examples/onoda_he.json) (Hebrew).

## Development

```bash
python -m venv .venv && .venv/bin/pip install -r plugins/toon-shorts/requirements-dev.txt
cd plugins/toon-shorts && ../../.venv/bin/python -m pytest      # 150+ tests, coverage gate 85%
```

Every module stays under 200 lines. The engine uses only numpy, Pillow and ffmpeg (through the pinned `imageio-ffmpeg`), and the voice adds `kokoro-onnx`.

## Requirements

Claude Code 2.1.275+ · Python 3.11-3.13 · about 1.5 GB of RAM while rendering. A 50-second short renders in about 2 minutes on a 4-core laptop.

## Credits

[Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) (Apache-2.0) via [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx) (MIT). [Rubik](https://github.com/googlefonts/rubik) font (SIL OFL 1.1, bundled with its license). Videos you make are yours to monetize.
