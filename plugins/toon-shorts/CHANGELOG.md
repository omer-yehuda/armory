# Changelog

## 1.0.1 (2026-11-19)

### Fixed
- Hebrew captions rendered backwards when Pillow is built with libraqm (the standard Linux wheels): `bidi.py` already puts the text in visual order, and raqm reversed it a second time. Caption fonts now load with Pillow's BASIC layout engine, so the result is the same on every platform.

## 1.0.0 (2026-11-19)

First release. A clean-room rewrite of the idea behind an unlicensed "viral shorts" skill, which was audited and not installed (CAUTION: silent pip installs, an unverified model download, written for claude.ai paths). None of its code or prompts are reused.

### Added
- Full flow from questions to MP4: 10 ideas, retention script, voice, storyboard, a preview Claude reviews itself, then the render.
- Toon characters: 12 moods, 11 poses, 6 skin tones, 8 hair styles, 12 hats, 7 outfits, 28 props.
- 20 parallax sets (11 outdoor, 9 indoor), 5 times of day, 6 landmarks, 4 foreground overlays, 9 camera moves with automatic framing.
- Karaoke captions with Hebrew right-to-left layout.
- Timing from exact AI-voice line spans, the user's own recording (cuts snap to pauses), or reading pace.
- Storyboard checker that suggests corrections and flags pacing problems.

### Security
- Explicit, consent-first `setup` into a private venv. Nothing installs implicitly, and ffmpeg is found but never installed.
- Pinned dependencies. Kokoro model files are verified against SHA-256 digests, and a mismatch deletes the file.
- No network access outside setup. No filesystem sweeps.

### Tests
- 162 pytest tests, 97% coverage, run in CI.
