"""Scene types: quote, image (slow zoom), cta, plus the dispatcher."""
from functools import lru_cache

from PIL import Image, ImageDraw

from . import scenes as base
from . import text as tx
from .canvas import Ctx
from .motion import clamp, ease_out_back, ease_out_cubic, pulse
from .themes import lerp, on_accent


def quote(c: Ctx, sc, t: float) -> None:
    f = c.fit(sc.text, 0.5, 100, 700)
    au = c.fit(f"- {sc.author}", 0.1, 52, 500) if sc.author else None
    total = 180 * c.s + f.height + ((au.height + 50 * c.s) if au else 0)
    top = c.y0 + (c.bh - total) / 2
    qf = tx.font(round(400 * c.s), 900)
    pop = ease_out_back(clamp(t / 0.5))
    c.d.text((c.x0, top - 120 * c.s * pop), "“", font=qf, fill=lerp(c.bg, c.accent, clamp(t * 4)))
    tx.draw_block(c.d, f, c.cx, top + 180 * c.s, t - 0.2, c.fg, c.bg, stagger=0.1)
    if au:
        tx.draw_block(c.d, au, c.cx, top + 180 * c.s + f.height + 50 * c.s, t - 0.2 - tx.reveal_end(len(sc.text.split()), 0.1),
                      c.pal["muted"], c.bg)


@lru_cache(maxsize=8)
def _load(path: str) -> Image.Image:
    im = Image.open(path)
    im.draft("RGB", (2400, 2400))
    im = im.convert("RGB")
    im.thumbnail((2400, 2400))
    return im


@lru_cache(maxsize=8)
def _mask(size: tuple, radius: int) -> Image.Image:
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return m


def image(c: Ctx, sc, t: float) -> None:
    cap = c.fit(sc.text, 0.14, 64, 700) if sc.text else None
    cap_h = (cap.height + 40 * c.s) if cap else 0
    bw, bh = round(c.bw), round(c.bh - cap_h)
    top = c.y0 + (c.bh - cap_h - bh) / 2
    slide = (1 - ease_out_cubic(t / 0.6)) * 80 * c.s
    src = _load(str(sc.image))
    sw, sh = src.size
    cw = min(sw, sh * bw / bh)             # cover-fit crop with the box aspect ratio
    ch = cw * bh / bw
    z = 1 + 0.14 * clamp(t / sc.duration)  # slow zoom toward the upper right
    cw, ch = cw / z, ch / z
    fx = 0.5 + 0.5 * clamp(t / sc.duration)
    left, upper = (sw - cw) * fx, (sh - ch) * (1 - fx)
    crop = src.resize((bw, bh), Image.BICUBIC, box=(left, upper, left + cw, upper + ch))
    c.img.paste(crop, (round(c.x0), round(top + slide)), _mask((bw, bh), round(48 * c.s)))
    if cap:
        tx.draw_block(c.d, cap, c.cx, top + bh + 40 * c.s, t - 0.3, c.fg, c.bg)


def cta(c: Ctx, sc, t: float) -> None:
    f = c.fit(sc.text, 0.45, 130, 900)
    btn_h = 150 * c.s
    total = f.height + ((btn_h + 70 * c.s) if sc.sub else 0)
    top = c.y0 + (c.bh - total) / 2
    tx.draw_block(c.d, f, c.cx, top, t, c.fg, c.bg, c.accent, accent_last=True)
    if not sc.sub:
        return
    p = ease_out_back(clamp((t - tx.reveal_end(len(sc.text.split())) - 0.1) / 0.4))
    k = p * (1 + 0.04 * pulse(t))
    bf = tx.fit(sc.sub, c.bw - 120 * c.s, btn_h, round(64 * c.s * k) or 8, 8, 800)
    w = min(c.bw, bf.font.getlength(sc.sub) + 120 * c.s * k)
    cy = top + f.height + 70 * c.s + btn_h / 2
    half = btn_h / 2 * k
    c.d.rounded_rectangle((c.cx - w / 2, cy - half, c.cx + w / 2, cy + half), radius=half, fill=c.accent)
    if k > 0.3:
        c.d.text((c.cx, cy), sc.sub, font=bf.font, anchor="mm", fill=on_accent(c.accent))


DRAWERS = {"title": base.title, "bullets": base.bullets, "stat": base.stat, "compare": base.compare,
           "quote": quote, "image": image, "cta": cta}


def draw_scene(sc, t: float, size: tuple[int, int], decor: bool = True) -> Image.Image:
    """Render one scene at local time t (seconds) as an RGB image."""
    c = Ctx(sc, size)
    if decor:
        c.decor(t + sc.start)
    DRAWERS[sc.type](c, sc, max(0.0, t))
    return c.img
