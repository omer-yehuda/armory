"""Scene types: title, bullets, stat, compare. Each draw function paints one frame at time t."""
from . import text as tx
from .canvas import Ctx
from .motion import clamp, ease_out_back, ease_out_cubic
from .themes import lerp, on_accent


def title(c: Ctx, sc, t: float) -> None:
    f = c.fit(sc.text, 0.7, 170, 900)
    top = c.y0 + (c.bh - f.height) / 2
    tx.draw_block(c.d, f, c.cx, top, t, c.fg, c.bg, c.accent, accent_last=True)
    p = ease_out_cubic((t - tx.reveal_end(len(sc.text.split())) * 0.6) / 0.5)
    bar_w, bar_h = min(c.bw * 0.5, 300 * c.s) * p, 16 * c.s
    y = top + f.height + 36 * c.s
    c.d.rounded_rectangle((c.cx - bar_w / 2, y, c.cx + bar_w / 2, y + bar_h), radius=bar_h / 2, fill=c.accent)


def bullets(c: Ctx, sc, t: float) -> None:
    n, gap = len(sc.items), 28 * c.s
    head = c.fit(sc.text, 0.12, 64, 800) if sc.text else None
    head_h = (head.height + 50 * c.s) if head else 0
    row_h = min(280 * c.s, (c.bh - head_h - gap * (n - 1)) / n)
    top = c.y0 + (c.bh - head_h - n * row_h - (n - 1) * gap) / 2
    if head:
        tx.draw_block(c.d, head, c.cx, top, t, c.accent, c.bg)
    badge = 84 * c.s
    for i, item in enumerate(sc.items):
        p = clamp((t - 0.25 - i * 0.45) / 0.5)
        if p <= 0:
            continue
        dx = (1 - ease_out_back(p)) * c.w * 0.7
        y = top + head_h + i * (row_h + gap)
        c.card((c.x0 + dx, y, c.x1 + dx, y + row_h), radius=44)
        by = y + (row_h - badge) / 2
        c.d.ellipse((c.x0 + 36 * c.s + dx, by, c.x0 + 36 * c.s + badge + dx, by + badge), fill=c.accent)
        nf = tx.font(round(50 * c.s), 900)
        c.d.text((c.x0 + 36 * c.s + badge / 2 + dx, by + badge / 2), str(i + 1), font=nf, anchor="mm",
                 fill=on_accent(c.accent))
        left = c.x0 + 36 * c.s + badge + 32 * c.s
        f = tx.fit(item, c.x1 - 30 * c.s - left, row_h - 40 * c.s, round(74 * c.s), round(tx.MIN_SIZE * c.s), 700)
        cx = left + (c.x1 - 30 * c.s - left) / 2 + dx
        for word, x, yy, _ in tx.layout(f, cx, y + (row_h - f.height) / 2):
            c.d.text((x, yy), word, font=f.font, fill=lerp(c.bg, c.fg, p * 2.5))


def _fmt(value: float, shown: float) -> str:
    decimals = 0 if float(value).is_integer() else min(2, len(str(value).split(".")[1]))
    return f"{shown:,.{decimals}f}"


def stat(c: Ctx, sc, t: float) -> None:
    final = f"{sc.prefix}{_fmt(sc.value, sc.value)}{sc.suffix}"
    nf = c.fit(final, 0.4, 420, 900)
    nf.lines = [final]
    lab = c.fit(sc.label, 0.25, 76, 600)
    bar = sc.suffix == "%"
    total = nf.height + 50 * c.s + lab.height + (90 * c.s if bar else 0)
    top = c.y0 + (c.bh - total) / 2
    e = ease_out_cubic(t / 1.3)
    shown = f"{sc.prefix}{_fmt(sc.value, sc.value * e)}{sc.suffix}"
    x = c.cx - nf.font.getlength(final) / 2
    c.d.text((x, top), shown, font=nf.font, fill=c.accent)
    y = top + nf.height + 50 * c.s
    tx.draw_block(c.d, lab, c.cx, y, t - 0.5, c.fg, c.bg)
    if bar:
        by, bh = y + lab.height + 40 * c.s, 34 * c.s
        c.d.rounded_rectangle((c.x0, by, c.x1, by + bh), radius=bh / 2, fill=c.pal["line"])
        c.d.rounded_rectangle((c.x0, by, c.x0 + max(bh, c.bw * clamp(sc.value / 100) * e), by + bh),
                              radius=bh / 2, fill=c.accent)


def compare(c: Ctx, sc, t: float) -> None:
    gap = 120 * c.s
    card_h = (c.bh - gap) / 2
    for k, (side, start, sign) in enumerate(((sc.left, 0.1, -1), (sc.right, 0.5, 1))):
        p = clamp((t - start) / 0.5)
        if p <= 0:
            continue
        dx = sign * (1 - ease_out_back(p)) * c.w
        y = c.y0 + k * (card_h + gap)
        c.card((c.x0 + dx, y, c.x1 + dx, y + card_h), radius=44)
        strip = c.accent if k == 0 else c.pal["muted"]
        c.d.rounded_rectangle((c.x0 + dx + 28 * c.s, y + 36 * c.s, c.x0 + dx + 44 * c.s, y + card_h - 36 * c.s),
                              radius=8 * c.s, fill=strip)
        inner_w = c.bw - 120 * c.s
        cx = c.x0 + 80 * c.s + inner_w / 2 + dx
        head = tx.fit(side["title"], inner_w, card_h * 0.25, round(96 * c.s), round(tx.MIN_SIZE * c.s), 800)
        n = len(side["items"])
        item_h = (card_h - head.height - 90 * c.s) / n
        fits = [tx.fit(i, inner_w, item_h, round(68 * c.s), round(tx.MIN_SIZE * c.s), 600) for i in side["items"]]
        top = y + (card_h - head.height - sum(f.height for f in fits) - 20 * c.s * n) / 2
        col = c.accent if k == 0 else c.fg
        for word, x, yy, _ in tx.layout(head, cx, top):
            c.d.text((x, yy), word, font=head.font, fill=lerp(c.bg, col, p * 2.5))
        top += head.height + 20 * c.s
        for f in fits:
            for word, x, yy, _ in tx.layout(f, cx, top):
                c.d.text((x, yy), word, font=f.font, fill=lerp(c.bg, c.pal["muted"] if k else c.fg, p * 2.5))
            top += f.height + 20 * c.s
    vs = clamp((t - 0.9) / 0.4)
    if vs > 0:
        r, cy = 56 * c.s * ease_out_back(vs), c.y0 + card_h + gap / 2
        c.d.ellipse((c.cx - r, cy - r, c.cx + r, cy + r), fill=c.accent)
        c.d.text((c.cx, cy), "VS", font=tx.font(round(44 * c.s * clamp(ease_out_back(vs))), 900), anchor="mm",
                 fill=(255, 255, 255) if sum(c.accent) < 400 else (20, 22, 26))
