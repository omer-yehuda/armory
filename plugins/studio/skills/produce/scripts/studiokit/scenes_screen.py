"""Scene types for real footage: screen (a screenshot in a browser frame, with zoom and pointer) and link."""
from PIL import Image

from . import text as tx
from .canvas import Ctx
from .motion import clamp, ease_in_out_cubic, ease_out_back, ease_out_cubic
from .imgcache import mask as _mask, padded
from .themes import lerp

BAR = 56          # browser top bar height, in base units
CHIP = 92         # caption chip height


def view_box(src_size: tuple, view: tuple, focus: tuple | None, k: float) -> tuple:
    """Crop box in source pixels for zoom progress k (0 = whole image fitted to the view's aspect, 1 = focus).
    The box always has the view's aspect ratio and stays inside the image."""
    sw, sh = src_size
    vw, vh = view
    aspect = vw / vh
    full_w = min(sw, sh * aspect)
    full = ((sw - full_w) / 2, 0.0, (sw + full_w) / 2, full_w / aspect)
    if not focus:
        return full
    fx0, fy0, fx1, fy1 = focus[0] * sw, focus[1] * sh, focus[2] * sw, focus[3] * sh
    w = max(fx1 - fx0, (fy1 - fy0) * aspect)
    w = min(w, full_w)
    h = w / aspect
    cx, cy = (fx0 + fx1) / 2, (fy0 + fy1) / 2
    x0 = min(max(0.0, cx - w / 2), sw - w)
    y0 = min(max(0.0, cy - h / 2), sh - h)
    target = (x0, y0, x0 + w, y0 + h)
    return tuple(a + (b - a) * k for a, b in zip(full, target))


def _image_point(sc, padded_size: tuple, frac: tuple) -> tuple:
    """A point given as fractions of the original picture, in the padded canvas's pixels."""
    from .imgcache import load
    w, h = load(str(sc.image)).size
    pw, ph = padded_size
    return (pw - w) / 2 + frac[0] * w, (ph - h) / 2 + frac[1] * h


def _pointer(c: Ctx, x: float, y: float, press: float) -> None:
    """Arrow pointer with its tip at (x, y). press (0..1) shrinks it slightly, like a click."""
    k = 34 * c.s * (1 - 0.12 * press)
    pts = [(0, 0), (0, 1.0), (0.27, 0.76), (0.45, 1.12), (0.6, 1.05), (0.42, 0.7), (0.75, 0.7)]
    poly = [(x + px * k, y + py * k) for px, py in pts]
    c.d.polygon(poly, fill=(255, 255, 255), outline=(20, 22, 26), width=max(1, round(3 * c.s)))


def _ripple(c: Ctx, x: float, y: float, age: float) -> None:
    if not 0 <= age <= 0.6:
        return
    r = (14 + 70 * ease_out_cubic(age / 0.6)) * c.s
    c.d.ellipse((x - r, y - r, x + r, y + r), outline=lerp(c.accent, c.bg, age / 0.6),
                width=max(2, round(6 * c.s)))


def _chrome(c: Ctx, box: tuple, url: str) -> None:
    """Window frame: rounded card, top bar with three dots and an address pill."""
    x0, y0, x1, _ = box
    bar = BAR * c.s
    c.card(box, radius=26, fill=c.pal["card"])
    for i, col in enumerate(((255, 95, 87), (254, 188, 46), (40, 200, 64))):
        cx, r = x0 + (34 + 30 * i) * c.s, 9 * c.s
        c.d.ellipse((cx - r, y0 + bar / 2 - r, cx + r, y0 + bar / 2 + r), fill=col)
    if url:
        px0, px1 = x0 + 140 * c.s, x1 - 40 * c.s
        c.d.rounded_rectangle((px0, y0 + 12 * c.s, px1, y0 + bar - 12 * c.s), radius=16 * c.s, fill=c.pal["line"])
        f = tx.fit(url, px1 - px0 - 40 * c.s, bar - 30 * c.s, round(26 * c.s), 8, 500)
        c.d.text((px0 + 20 * c.s, y0 + bar / 2), f.lines[0] if f.lines else url, font=f.font, anchor="lm",
                 fill=c.pal["muted"])


def screen(c: Ctx, sc, t: float) -> None:
    chip = (CHIP + 24) * c.s if sc.text else 0
    rise = (1 - ease_out_cubic(t / 0.5)) * 60 * c.s
    top = c.y0 + (chip if c.wide else 0) + rise
    bottom = c.y1 - (0 if c.wide else chip) + rise
    box = (c.x0, top, c.x1, bottom)
    _chrome(c, box, sc.url)
    vx0, vy0 = round(c.x0 + 6 * c.s), round(top + BAR * c.s)
    vw, vh = round(c.bw - 12 * c.s), round(bottom - top - BAR * c.s - 6 * c.s)
    src = padded(str(sc.image), round(vw / vh, 3))
    k = ease_in_out_cubic((t - 0.5) / max(0.5, sc.duration * 0.75 - 0.5)) if sc.zoom else 0.0
    zoom = None
    if sc.zoom:
        a, b = _image_point(sc, src.size, sc.zoom[:2]), _image_point(sc, src.size, sc.zoom[2:])
        zoom = (a[0] / src.size[0], a[1] / src.size[1], b[0] / src.size[0], b[1] / src.size[1])
    crop_box = view_box(src.size, (vw, vh), zoom, k)
    view = src.resize((vw, vh), Image.BICUBIC, box=crop_box)
    c.img.paste(view, (vx0, vy0), _mask((vw, vh), round(20 * c.s)))
    if sc.cursor:
        bx0, by0, bx1, by1 = crop_box
        ix, iy = _image_point(sc, src.size, sc.cursor)
        px = vx0 + (ix - bx0) / (bx1 - bx0) * vw
        py = vy0 + (iy - by0) / (by1 - by0) * vh
        arrive = ease_out_cubic(t / 0.8)
        px, py = px + (1 - arrive) * 220 * c.s, py + (1 - arrive) * 140 * c.s
        age = t - sc.click if sc.click is not None else -1
        _ripple(c, px, py, age)
        _pointer(c, px, py, 1.0 if 0 <= age <= 0.15 else 0.0)
    if sc.text:
        _chip(c, sc.text, c.y0 if c.wide else c.y1 - CHIP * c.s, t)


def _chip(c: Ctx, text: str, y: float, t: float) -> None:
    """Caption pill with an accent dot; pops in after the window lands."""
    p = ease_out_back(clamp((t - 0.3) / 0.4))
    if p <= 0:
        return
    h = CHIP * c.s
    f = tx.fit(text, c.bw - 160 * c.s, h * 0.62, round(52 * c.s * max(0.3, p)), 8, 800)
    w = min(c.bw, f.font.getlength(f.lines[0] if len(f.lines) == 1 else text) + 130 * c.s)
    c.d.rounded_rectangle((c.x0, y, c.x0 + w, y + h), radius=h / 2, fill=c.fg)
    r = 14 * c.s
    c.d.ellipse((c.x0 + 40 * c.s - r, y + h / 2 - r, c.x0 + 40 * c.s + r, y + h / 2 + r), fill=c.accent)
    c.d.text((c.x0 + 74 * c.s, y + h / 2), " ".join(f.lines), font=f.font, anchor="lm", fill=c.bg)


def link(c: Ctx, sc, t: float) -> None:
    """Link card: a chain icon, the address typing itself out, and a short label."""
    p = ease_out_back(clamp(t / 0.5))
    card_h = min(c.bh, (360 if c.wide else 520) * c.s)
    top = c.y0 + (c.bh - card_h) / 2 + (1 - p) * 120 * c.s
    c.card((c.x0, top, c.x1, top + card_h), radius=40)
    ic, icx, icy = 46 * c.s, c.x0 + 110 * c.s, top + card_h / 2
    for dx in (-0.45, 0.45):
        c.d.rounded_rectangle((icx + dx * ic - ic * 0.7, icy - ic * 0.38, icx + dx * ic + ic * 0.7, icy + ic * 0.38),
                              radius=ic * 0.38, outline=c.accent, width=max(2, round(10 * c.s)))
    left = c.x0 + 200 * c.s
    shown = sc.text[:max(0, round(len(sc.text) * clamp((t - 0.35) / 0.9)))]
    f = tx.fit(sc.text, c.x1 - 50 * c.s - left, card_h * 0.4, round(84 * c.s), 8, 800)
    ty = icy - (f.line_h * len(f.lines)) / 2 - (30 * c.s if sc.sub else 0)
    c.d.text((left, ty), shown, font=f.font, fill=c.fg)
    if sc.sub and t > 1.2:
        sf = tx.fit(sc.sub, c.x1 - 50 * c.s - left, card_h * 0.2, round(46 * c.s), 8, 500)
        c.d.text((left, ty + f.height + 24 * c.s), sc.sub, font=sf.font, fill=lerp(c.bg, c.pal["muted"], clamp((t - 1.2) * 3)))
