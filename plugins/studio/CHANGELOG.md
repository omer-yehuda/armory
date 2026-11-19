# Changelog

## 1.0.0 (2026-11-19)

First release.

- `/studio:produce <topic>`: a crew of agents (writer, director, screener) plus a local renderer turns a topic into a 1080x1920, 30 fps H.264 explainer video with `captions.srt` and `metadata.md`.
- Seven scene types: title, bullets, stat, compare, quote, image (slow zoom), cta. Light and dark themes, eight accent colors, four transitions (cut, slide, fade, zoom-punch).
- Storyboard checker with scene-numbered errors and retention warnings (hook, words per screen, reading time, contrast, length).
- Contact-sheet preview with a safe-area outline for Shorts UI, reviewed by the screener before the final render.
- Optional user audio (`--audio`, `--fit-audio`). Captions-only by default.
- `/studio:crew`: one-screen description of the crew.
- Consent-first `setup`: private venv with pinned Pillow 12.3.0; ffmpeg is checked, never installed.
- Bundled Rubik font (OFL).
- 130+ pytest tests, about 98% coverage, including a real end-to-end render.
- Security: topic and audio path reach the scripts through files, safe folder names, outputs and image/audio paths confined to the production folder, no writes through symlinks, hash-locked pip install.
