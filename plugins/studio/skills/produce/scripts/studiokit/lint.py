"""Soft rules (warnings, not errors): retention, readability, pacing."""
from .themes import PALETTES, contrast

WORD_LIMIT = {"bullets": 12, "compare": 12, "link": 10}
DEFAULT_WORD_LIMIT = 7
LENGTH = {"short": (15, 60, 14), "wide": (45, 480, 40)}     # min s, max s, max scenes


def lint(sb) -> list[str]:
    out = []
    n = len(sb.scenes)
    total = sb.duration
    lo, hi, most = LENGTH[sb.format]
    if total > hi:
        out.append(f"total length {total:.0f}s is over {hi}s for a {sb.format} video: cut scenes or shorten durations")
    if total < lo:
        out.append(f"total length {total:.0f}s is under {lo}s: probably too thin for a {sb.format} video")
    if n > most:
        out.append(f"{n} scenes is a lot: aim for fewer so each idea has room")
    first, last = sb.scenes[0], sb.scenes[-1]
    if first.duration > 3.5:
        out.append(f"scene 0: the hook scene runs {first.duration:g}s. Land the hook in the first 2-3 seconds")
    if first.type in ("cta", "image", "link"):
        out.append(f"scene 0 ({first.type}): open with a 'title', 'stat' or 'quote' hook")
    if last.type != "cta" and n > 1:
        out.append(f"scene {n - 1}: end with a 'cta' scene so viewers know what to do next")
    for s in sb.scenes:
        w, limit = s.words(), WORD_LIMIT.get(s.type, DEFAULT_WORD_LIMIT)
        where = f"scene {s.index} ({s.type})"
        if w > limit:
            out.append(f"{where}: {w} words on screen, keep it to {limit} or fewer")
        need = 0.9 + 0.3 * w
        if s.duration > 12 and sb.format == "short":
            out.append(f"{where}: {s.duration:g}s is long for a Short, split it into two scenes")
        if s.duration < need:
            out.append(f"{where}: {s.duration:g}s is too short to read {w} words, use at least {need:.1f}s")
        c = contrast(s.accent, PALETTES[s.theme]["bg"])
        if c < 3.0:
            out.append(f"{where}: accent contrast {c:.1f}:1 on the {s.theme} theme is low (want 3:1), "
                       "pick another accent for this scene")
    return out
