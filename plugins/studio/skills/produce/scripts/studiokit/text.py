"""Fonts, word wrap, auto-fit, and kinetic word-by-word reveal."""
from dataclasses import dataclass
from functools import lru_cache

from PIL import ImageFont

from .motion import clamp, ease_out_back
from .paths import FONT
from .themes import lerp

MIN_SIZE = 28


@lru_cache(maxsize=128)
def font(size: int, weight: int = 700) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(str(FONT), max(8, int(size)))
    f.set_variation_by_axes([weight])
    return f


def wrap(text: str, f, max_w: float) -> list[str]:
    """Greedy word wrap. A single word wider than max_w gets its own line (fit() shrinks for it)."""
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if cur and f.getlength(trial) > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


@dataclass
class Fit:
    font: ImageFont.FreeTypeFont
    lines: list
    line_h: int

    @property
    def height(self) -> int:
        return self.line_h * len(self.lines)


def fit(text: str, box_w: float, box_h: float, max_size: int, min_size: int = MIN_SIZE,
        weight: int = 700, spacing: float = 1.15) -> Fit:
    """Largest font (stepping down by 4px) whose wrapped text fits the box."""
    size = int(max_size)
    while True:
        f = font(size, weight)
        lines = wrap(text, f, box_w)
        line_h = round(size * spacing)
        ok_w = all(f.getlength(ln) <= box_w for ln in lines)
        if (ok_w and line_h * len(lines) <= box_h) or size <= min_size:
            return Fit(f, lines, line_h)
        size = max(min_size, size - 4)


def layout(fit_: Fit, cx: float, top: float) -> list[tuple[str, float, float, int]]:
    """(word, x, y, line_index) for every word, each line centered on cx, block starting at top."""
    f, out = fit_.font, []
    space = f.getlength(" ")
    for li, line in enumerate(fit_.lines):
        x = cx - f.getlength(line) / 2
        for word in line.split():
            out.append((word, x, top + li * fit_.line_h, li))
            x += f.getlength(word) + space
    return out


def bounds(fit_: Fit, cx: float, top: float) -> tuple[float, float, float, float]:
    """Bounding box (x0, y0, x1, y1) of the laid out text, for margin checks."""
    pos = layout(fit_, cx, top)
    x0 = min(x for _, x, _, _ in pos)
    x1 = max(x + fit_.font.getlength(w) for w, x, _, _ in pos)
    return x0, top, x1, top + fit_.height


def draw_block(d, fit_: Fit, cx: float, top: float, t: float, fg, bg, accent=None,
               stagger: float = 0.12, pop: float = 0.35, accent_last: bool = False) -> None:
    """Draw text with each word popping in (rise + overshoot + fade) in order."""
    pos = layout(fit_, cx, top)
    n = len(pos)
    rise = fit_.font.size * 0.5
    for i, (word, x, y, _) in enumerate(pos):
        p = clamp((t - i * stagger) / pop)
        if p <= 0:
            continue
        color = accent if (accent_last and accent and i == n - 1) else fg
        d.text((x, y + (1 - ease_out_back(p)) * rise), word, font=fit_.font,
               fill=lerp(bg, color, p * 2.5))


def reveal_end(n_words: int, stagger: float = 0.12, pop: float = 0.35) -> float:
    """Seconds until the last word has fully landed."""
    return (n_words - 1) * stagger + pop
