"""Easing functions and scene transitions."""
import math

TRANSITIONS = ("cut", "slide", "fade", "zoom-punch")
TRANSITION_SECONDS = 0.4


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def ease_out_back(t: float, overshoot: float = 1.70158) -> float:
    """Pop with a small overshoot. 0 -> 0, 1 -> 1 (may exceed 1 in between)."""
    t = clamp(t)
    c3 = overshoot + 1
    return 1 + c3 * (t - 1) ** 3 + overshoot * (t - 1) ** 2


def ease_in_out_cubic(t: float) -> float:
    t = clamp(t)
    return 4 * t ** 3 if t < 0.5 else 1 - ((-2 * t + 2) ** 3) / 2


def ease_out_cubic(t: float) -> float:
    return 1 - (1 - clamp(t)) ** 3


def pulse(t: float, period: float = 1.2) -> float:
    """0..1 smooth loop, for CTA buttons."""
    return 0.5 - 0.5 * math.cos(2 * math.pi * t / period)


def transition_length(kind: str, scene_seconds: float) -> float:
    if kind == "cut":
        return 0.0
    return min(TRANSITION_SECONDS, scene_seconds * 0.4)


def apply_transition(kind: str, prev, cur, p: float):
    """Blend the last frame of the previous scene (prev) with the current frame (cur).
    p runs 0..1 over the transition window. Both are RGB images of the same size."""
    from PIL import Image
    if kind == "cut" or p >= 1:
        return cur
    w, h = cur.size
    if kind == "fade":
        return Image.blend(prev, cur, ease_in_out_cubic(p))
    if kind == "slide":
        e = ease_in_out_cubic(p)
        out = Image.new("RGB", (w, h))
        out.paste(prev, (round(-e * w), 0))
        out.paste(cur, (round((1 - e) * w), 0))
        return out
    if kind == "zoom-punch":
        e = ease_out_cubic(p)
        zoom = 1 + 0.25 * (1 - e)
        cw, ch = w / zoom, h / zoom
        box = ((w - cw) / 2, (h - ch) / 2, (w + cw) / 2, (h + ch) / 2)
        zoomed = cur.resize((w, h), Image.BILINEAR, box=box)
        return Image.blend(prev, zoomed, clamp(p * 4))
    raise ValueError(f"unknown transition {kind!r}")
