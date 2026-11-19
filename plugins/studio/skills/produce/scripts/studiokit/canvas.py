"""Per-frame drawing context: image, palette, safe area, shared helpers."""
import math

from PIL import Image, ImageDraw

from . import text as tx
from .themes import PALETTES, lerp

BASE_W, BASE_H = 1080, 1920
# Safe area in 1080x1920 units: keeps text clear of the Shorts UI (title/buttons at the bottom,
# search/camera icons at the top, action buttons at the right edge).
SAFE_LEFT, SAFE_RIGHT, SAFE_TOP, SAFE_BOTTOM = 90, 90, 230, 420


def frame_size(scale: float) -> tuple[int, int]:
    """Even dimensions (H.264 needs them) for a given scale of 1080x1920."""
    return 2 * round(BASE_W * scale / 2), 2 * round(BASE_H * scale / 2)


class Ctx:
    def __init__(self, scene, size: tuple[int, int]):
        self.w, self.h = size
        self.s = self.w / BASE_W
        self.sy = self.h / BASE_H
        self.pal = PALETTES[scene.theme]
        self.accent = scene.accent
        self.bg, self.fg = self.pal["bg"], self.pal["fg"]
        self.img = Image.new("RGB", size, self.bg)
        self.d = ImageDraw.Draw(self.img)
        self.x0, self.x1 = SAFE_LEFT * self.s, self.w - SAFE_RIGHT * self.s
        self.y0, self.y1 = SAFE_TOP * self.sy, self.h - SAFE_BOTTOM * self.sy
        self.cx = self.w / 2

    @property
    def bw(self) -> float:
        return self.x1 - self.x0

    @property
    def bh(self) -> float:
        return self.y1 - self.y0

    def fit(self, text: str, height_frac: float, max_size: int, weight: int = 700, width: float | None = None):
        return tx.fit(text, width or self.bw, self.bh * height_frac, round(max_size * self.s),
                      round(tx.MIN_SIZE * self.s), weight)

    def decor(self, t: float) -> None:
        """Soft drifting shapes behind the content."""
        mix = 0.10 if self.pal is PALETTES["light"] else 0.16
        tone = lerp(self.bg, self.accent, mix)
        r = self.w * 0.34
        cx = self.w * 0.88 + 24 * self.s * math.sin(t * 0.8)
        cy = self.h * 0.80 + 24 * self.s * math.cos(t * 0.6)
        self.d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=tone)
        r2 = self.w * 0.14
        cx2, cy2 = self.w * 0.08, self.h * 0.14 + 16 * self.s * math.sin(t)
        self.d.ellipse((cx2 - r2, cy2 - r2, cx2 + r2, cy2 + r2), outline=tone, width=max(2, round(14 * self.s)))

    def card(self, box, radius: float = 40, fill=None, outline=None) -> None:
        self.d.rounded_rectangle(box, radius=radius * self.s, fill=fill or self.pal["card"],
                                 outline=outline or self.pal["line"], width=max(1, round(3 * self.s)))


def progress_bar(img, progress: float, accent, theme: str) -> None:
    """Thin video progress bar at the top, inside the horizontal safe area."""
    d, w = ImageDraw.Draw(img), img.size[0]
    s = w / BASE_W
    x0, x1, y, hh = SAFE_LEFT * s, w - SAFE_RIGHT * s, 120 * img.size[1] / BASE_H, max(3, 10 * s)
    d.rounded_rectangle((x0, y, x1, y + hh), radius=hh / 2, fill=PALETTES[theme]["line"])
    fill_to = x0 + (x1 - x0) * max(0.02, min(1.0, progress))
    d.rounded_rectangle((x0, y, fill_to, y + hh), radius=hh / 2, fill=accent)
