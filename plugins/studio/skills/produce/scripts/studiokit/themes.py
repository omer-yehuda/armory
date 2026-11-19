"""Light and dark palettes plus accent colors. No Pillow needed."""
import re

PALETTES = {
    "light": {"bg": (247, 244, 236), "fg": (20, 22, 26), "muted": (96, 100, 110), "card": (255, 255, 255),
              "line": (222, 217, 205)},
    "dark": {"bg": (15, 17, 23), "fg": (245, 245, 247), "muted": (160, 166, 180), "card": (30, 34, 44),
             "line": (52, 58, 72)},
}

ACCENTS = {
    "coral": (228, 60, 44), "blue": (37, 99, 235), "green": (18, 148, 66), "yellow": (250, 204, 21),
    "purple": (139, 92, 246), "orange": (222, 84, 6), "pink": (236, 72, 153), "teal": (13, 148, 136),
}
DEFAULT_ACCENT = "coral"
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


def parse_accent(value) -> tuple[int, int, int] | None:
    """Named color or #RRGGBB -> RGB tuple, None if invalid."""
    if isinstance(value, str):
        if value.lower() in ACCENTS:
            return ACCENTS[value.lower()]
        if HEX.match(value):
            return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))
    return None


def _lin(c: int) -> float:
    c /= 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb) -> float:
    r, g, b = (_lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b) -> float:
    """WCAG contrast ratio, 1..21."""
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def lerp(a, b, t: float):
    t = max(0.0, min(1.0, t))
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def on_accent(accent) -> tuple[int, int, int]:
    """Readable text color to put on top of an accent fill."""
    dark, light = (20, 22, 26), (255, 255, 255)
    return dark if contrast(accent, dark) >= contrast(accent, light) else light
