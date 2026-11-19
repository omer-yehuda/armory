"""Cached picture loading and rounded masks, shared by the image and screen scenes."""
from functools import lru_cache

from PIL import Image, ImageDraw


@lru_cache(maxsize=8)
def load(path: str) -> Image.Image:
    im = Image.open(path)
    im.draft("RGB", (2400, 2400))
    im = im.convert("RGB")
    im.thumbnail((2400, 2400))
    return im


@lru_cache(maxsize=8)
def mask(size: tuple, radius: int) -> Image.Image:
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return m


@lru_cache(maxsize=8)
def padded(path: str, aspect: float) -> Image.Image:
    """The picture centered on a canvas of the given aspect ratio (w / h), filled with its corner color,
    so the whole screenshot fits the view before any zoom."""
    im = load(path)
    w, h = im.size
    cw, ch = (w, round(w / aspect)) if w / h > aspect else (round(h * aspect), h)
    if (cw, ch) == (w, h):
        return im
    out = Image.new("RGB", (max(cw, w), max(ch, h)), im.getpixel((2, h - 3)))
    out.paste(im, ((out.width - w) // 2, (out.height - h) // 2))
    return out
