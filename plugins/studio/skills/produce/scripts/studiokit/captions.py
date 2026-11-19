"""SRT captions and upload metadata, derived from the storyboard. No Pillow needed."""


def sentences(text: str) -> list[str]:
    """Split narration into caption-sized pieces: sentences, long ones cut near 9 words."""
    out, cur = [], []
    for w in text.split():
        cur.append(w)
        if w.endswith((".", "?", "!", ":")) or (len(cur) >= 9 and w.endswith(",")) or len(cur) >= 12:
            out.append(" ".join(cur))
            cur = []
    if cur:
        out.append(" ".join(cur))
    return out


def _units(sc) -> list[str]:
    """Caption cues for one scene, in reading order: the narration when there is one, else the screen text."""
    if sc.say:
        return sentences(sc.say)
    if sc.type == "stat":
        return [f"{sc.prefix}{sc.value:,g}{sc.suffix} {sc.label}"]
    if sc.type == "bullets":
        return [s for s in [sc.text, *sc.items] if s]
    if sc.type == "compare":
        return [f"{sc.left['title']}: " + ", ".join(sc.left["items"]),
                f"{sc.right['title']}: " + ", ".join(sc.right["items"])]
    if sc.type == "quote":
        return [sc.text, f"- {sc.author}"] if sc.author else [sc.text]
    return [s for s in [sc.text] if s]


def cues(sb) -> list[tuple[float, float, str]]:
    """(start, end, text): each scene's duration is split between its cues by word count."""
    out = []
    for sc in sb.scenes:
        units = _units(sc)
        words = [max(1, len(u.split())) for u in units]
        t = sc.start
        for u, n in zip(units, words):
            d = sc.duration * n / sum(words)
            out.append((t, t + d, u))
            t += d
    return out


def stamp(sec: float) -> str:
    ms = round(sec * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def to_srt(sb) -> str:
    blocks = [f"{i}\n{stamp(a)} --> {stamp(b)}\n{txt}\n" for i, (a, b, txt) in enumerate(cues(sb), 1)]
    return "\n".join(blocks)


def metadata_md(sb, width: int, height: int, fps: int) -> str:
    m = sb.meta
    titles = [t[:100] for t in m.get("titles", [])] or [sb.title[:100]]
    texts = [s.text for s in sb.scenes if s.text]
    desc = m.get("description") or " ".join(texts[:1] + texts[-1:]).strip()
    tags = [t if t.startswith("#") else f"#{t}" for t in m.get("hashtags", [])]
    if sb.format == "short" and not any(t.lower() == "#shorts" for t in tags):
        tags.insert(0, "#Shorts")
    lines = ["# Upload metadata", "", "## Title options", *[f"{i}. {t}" for i, t in enumerate(titles, 1)], "",
             "## Description", desc, "", "## Hashtags", " ".join(tags), "",
             "## Technical", f"- {width}x{height}, {fps} fps, H.264, {sb.duration:.1f} s",
             "- captions.srt can be uploaded as a caption track", ""]
    return "\n".join(lines)
