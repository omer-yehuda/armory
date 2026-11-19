"""Contact sheet: one key frame per scene, with safe-area guides, for a quick visual review."""
from pathlib import Path

from PIL import Image, ImageDraw

from . import text as tx
from .canvas import SAFE_BOTTOM, SAFE_LEFT, SAFE_RIGHT, SAFE_TOP, frame_size
from .scenes_media import draw_scene

TILE_SCALE = 0.3
PAD, LABEL_H = 14, 40
SHEET_BG = (28, 28, 32)


def _guides(img) -> None:
    w, h = img.size
    ImageDraw.Draw(img).rectangle((SAFE_LEFT * w / 1080, SAFE_TOP * h / 1920,
                                   w - SAFE_RIGHT * w / 1080, h - SAFE_BOTTOM * h / 1920),
                                  outline=(255, 70, 70), width=1)


def key_frames(sb):
    """(label, time) pairs: a mid-animation look at the hook, then the settled state of every scene."""
    first = sb.scenes[0]
    out = [(f"hook @0.6s: {first.type}", first, min(0.6, first.duration))]
    for s in sb.scenes:
        out.append((f"#{s.index} {s.type} {s.duration:g}s {s.theme}", s, max(0.0, min(s.duration * 0.92, s.duration - 0.05))))
    return out


def contact_sheet(sb, out: Path, cols: int = 4, guides: bool = True) -> Path:
    tiles = key_frames(sb)
    tw, th = frame_size(TILE_SCALE)
    cols = max(1, min(cols, len(tiles)))
    rows = -(-len(tiles) // cols)
    sheet = Image.new("RGB", (PAD + cols * (tw + PAD), PAD + rows * (th + LABEL_H + PAD)), SHEET_BG)
    d, lf = ImageDraw.Draw(sheet), tx.font(18, 600)
    for i, (label, sc, t) in enumerate(tiles):
        x, y = PAD + (i % cols) * (tw + PAD), PAD + (i // cols) * (th + LABEL_H + PAD)
        tile = draw_scene(sc, t, (tw, th))
        if guides:
            _guides(tile)
        sheet.paste(tile, (x, y))
        d.text((x, y + th + 8), label, font=lf, fill=(235, 235, 240))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return out
