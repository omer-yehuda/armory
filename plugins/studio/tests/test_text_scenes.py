import pytest
from PIL import Image, ImageChops

from studiokit import spec, text as tx
from studiokit.canvas import Ctx, frame_size, progress_bar
from studiokit.scenes_media import draw_scene

SIZE = (270, 480)
LONG = "Kinetic typography keeps every single word readable even when a sentence runs far too long for one line"

SCENES = {
    "title": {"type": "title", "text": "Big punchy idea"},
    "bullets": {"type": "bullets", "text": "Heading", "items": ["First point", "Second point here", "Third", "Fourth one"]},
    "stat": {"type": "stat", "value": 1234567, "label": "things counted", "prefix": "$"},
    "stat_pct": {"type": "stat", "value": 72.5, "suffix": "%", "label": "done"},
    "compare": {"type": "compare", "left": {"title": "Old way", "items": ["Slow", "Manual"]},
                "right": {"title": "New way", "items": ["Fast"]}},
    "quote": {"type": "quote", "text": "Say it once", "author": "Someone"},
    "quote_plain": {"type": "quote", "text": "No author here"},
    "image": {"type": "image", "image": "pic.png", "text": "A caption"},
    "image_nocap": {"type": "image", "image": "pic.png"},
    "cta": {"type": "cta", "text": "Follow along", "sub": "Follow for more"},
    "cta_plain": {"type": "cta", "text": "Thanks for watching"},
    "bullets_nohead": {"type": "bullets", "items": ["One", "Two"]},
}


def scene(name, photo, **extra):
    data = dict(SCENES[name], **extra)
    if "image" in data:
        data["image"] = photo.name
    sb, errs, _ = spec.validate({"title": "t", "scenes": [data]}, photo.parent)
    assert not errs, errs
    return sb.scenes[0]


def test_wrap_and_fit_stay_inside_box():
    f = tx.font(60)
    for line in tx.wrap(LONG, f, 500):
        assert f.getlength(line) <= 500
    fit = tx.fit(LONG, 800, 500, 200)
    x0, y0, x1, y1 = tx.bounds(fit, 540, 100)
    assert 140 <= x0 and x1 <= 940 and y1 - y0 <= 500
    assert fit.font.size < 200


def test_fit_keeps_big_size_for_short_text_and_has_a_floor():
    assert tx.fit("Hi", 900, 600, 150).font.size == 150
    tiny = tx.fit(LONG, 100, 50, 150)
    assert tiny.font.size == tx.MIN_SIZE


def test_wrap_long_word_gets_own_line():
    assert tx.wrap("a Supercalifragilistic b", tx.font(40), 120) == ["a", "Supercalifragilistic", "b"]
    assert tx.wrap("", tx.font(40), 100) == []


def test_reveal_is_word_by_word():
    fit = tx.fit("one two three", 900, 500, 100)
    bg, fg = (255, 255, 255), (0, 0, 0)

    def frame(t):
        im = Image.new("RGB", (1080, 600), bg)
        from PIL import ImageDraw
        tx.draw_block(ImageDraw.Draw(im), fit, 540, 100, t, fg, bg)
        return im

    assert ImageChops.difference(frame(-1), Image.new("RGB", (1080, 600), bg)).getbbox() is None
    blank = Image.new("RGB", (1080, 600), bg)
    early = ImageChops.difference(frame(0.2), blank).getbbox()
    late = ImageChops.difference(frame(2), blank).getbbox()
    assert early and late and early != late
    assert tx.reveal_end(3) == pytest.approx(0.24 + 0.35)


@pytest.mark.parametrize("name", list(SCENES))
def test_every_scene_type_renders_the_right_size(name, photo):
    sc = scene(name, photo)
    for t in (0.0, 0.4, sc.duration / 2, sc.duration):
        im = draw_scene(sc, t, SIZE)
        assert im.size == SIZE and im.mode == "RGB"


@pytest.mark.parametrize("name", list(SCENES))
def test_scenes_animate(name, photo):
    sc = scene(name, photo)
    first = draw_scene(sc, 0.05, SIZE, decor=False)
    last = draw_scene(sc, sc.duration - 0.05, SIZE, decor=False)
    assert ImageChops.difference(first, last).getbbox() is not None


@pytest.mark.parametrize("name", list(SCENES))
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_content_stays_inside_safe_margins(name, theme, photo):
    """With decor off, every pixel outside the safe area is exactly the background."""
    sc = scene(name, photo, theme=theme)
    c = Ctx(sc, (540, 960))
    im = draw_scene(sc, sc.duration * 0.95, (540, 960), decor=False)
    clean = Image.new("RGB", im.size, c.bg)
    mask = Image.new("L", im.size, 255)
    mask.paste(0, (round(c.x0) - 1, round(c.y0) - 1, round(c.x1) + 1, round(c.y1) + 1))
    diff = ImageChops.difference(im, clean).convert("L")
    assert ImageChops.multiply(diff, mask).getbbox() is None


def test_long_text_still_fits(photo):
    sc = scene("title", photo, text=LONG)
    im = draw_scene(sc, 5, (540, 960), decor=False)
    c = Ctx(sc, (540, 960))
    box = ImageChops.difference(im, Image.new("RGB", im.size, c.bg)).getbbox()
    assert box[0] >= c.x0 - 1 and box[2] <= c.x1 + 1 and box[1] >= c.y0 - 1 and box[3] <= c.y1 + 1


def test_stat_counts_up(photo):
    sc = scene("stat", photo)
    a, b, c_ = (draw_scene(sc, t, SIZE, decor=False) for t in (0.1, 0.5, 2.0))
    assert a.tobytes() != b.tobytes() != c_.tobytes()


def test_frame_size_is_even_and_scales():
    assert frame_size(1.0) == (1080, 1920) and frame_size(0.25) == (270, 480)
    w, h = frame_size(0.333)
    assert w % 2 == 0 and h % 2 == 0


def test_progress_bar_grows():
    a, b = (Image.new("RGB", (270, 480), (255, 255, 255)) for _ in range(2))
    progress_bar(a, 0.1, (255, 0, 0), "light")
    progress_bar(b, 0.9, (255, 0, 0), "light")
    assert a.tobytes() != b.tobytes()
