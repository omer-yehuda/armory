"""Soft rules (warnings, not errors): retention, readability, pacing."""
from .themes import PALETTES, contrast

WORD_LIMIT = {"bullets": 12, "compare": 12}
DEFAULT_WORD_LIMIT = 7


def lint(sb) -> list[str]:
    out = []
    n = len(sb.scenes)
    total = sb.duration
    if total > 60:
        out.append(f"total length {total:.0f}s is over 60s: cut scenes or shorten durations")
    if total < 15:
        out.append(f"total length {total:.0f}s is under 15s: probably too thin for an explainer")
    if n > 14:
        out.append(f"{n} scenes is a lot: aim for 8-12 so each idea has room")
    first, last = sb.scenes[0], sb.scenes[-1]
    if first.duration > 3.5:
        out.append(f"scene 0: the hook scene runs {first.duration:g}s. Land the hook in the first 2-3 seconds")
    if first.type in ("cta", "image"):
        out.append(f"scene 0 ({first.type}): open with a 'title', 'stat' or 'quote' hook")
    if last.type != "cta" and n > 1:
        out.append(f"scene {n - 1}: end with a 'cta' scene so viewers know what to do next")
    for s in sb.scenes:
        w, limit = s.words(), WORD_LIMIT.get(s.type, DEFAULT_WORD_LIMIT)
        where = f"scene {s.index} ({s.type})"
        if w > limit:
            out.append(f"{where}: {w} words on screen, keep it to {limit} or fewer")
        need = 0.9 + 0.3 * w
        if s.duration < need:
            out.append(f"{where}: {s.duration:g}s is too short to read {w} words, use at least {need:.1f}s")
        c = contrast(s.accent, PALETTES[s.theme]["bg"])
        if c < 3.0:
            out.append(f"{where}: accent contrast {c:.1f}:1 on the {s.theme} theme is low (want 3:1), "
                       "pick another accent for this scene")
    return out
