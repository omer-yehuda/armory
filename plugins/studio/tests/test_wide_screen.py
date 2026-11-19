"""Wide (16:9) format, the screen and link scenes, narration-based captions."""
from PIL import Image

from studiokit import captions, lint
from studiokit.canvas import Ctx, frame_size, progress_bar
from studiokit.imgcache import padded
from studiokit.preview import contact_sheet
from studiokit.scenes_media import draw_scene
from studiokit.scenes_screen import view_box
from studiokit.spec import validate

SCREEN = {"type": "screen", "image": "pic.png", "url": "example.com/page", "text": "Real result",
          "zoom": [0.2, 0.2, 0.6, 0.7], "cursor": [0.5, 0.5], "click": 1.0}


def board_in(tmp_path, photo, board, *scenes, **top):
    (tmp_path / "pic.png").write_bytes(photo.read_bytes())
    sb, errs, warns = validate(board(*scenes, **top), tmp_path)
    assert not errs, errs
    return sb, warns


def test_format_validation(board, tmp_path):
    _, errs, _ = validate(board({"type": "title", "text": "x"}, format="square"), tmp_path)
    assert any("'format' must be one of short, wide" in e for e in errs)
    sb, errs, _ = validate(board({"type": "title", "text": "x"}, format="wide"), tmp_path)
    assert sb.format == "wide" and sb.scenes[0].fmt == "wide"


def test_frame_size_wide():
    assert frame_size(1.0, "wide") == (1920, 1080) and frame_size(0.25, "wide") == (480, 270)


def test_screen_and_link_draw_in_both_formats(tmp_path, photo, board):
    for fmt in ("short", "wide"):
        sb, _ = board_in(tmp_path, photo, board, SCREEN, {"type": "link", "text": "github.com/a/b", "sub": "MIT"},
                         format=fmt)
        size = frame_size(0.25, fmt)
        for sc in sb.scenes:
            for t in (0.0, 0.4, 1.05, 2.0, sc.duration):
                im = draw_scene(sc, t, size)
                assert im.size == size and im.getbbox()
        progress_bar(im, 0.5, (255, 0, 0), "dark", fmt)


def test_screen_without_zoom_cursor_or_caption(tmp_path, photo, board):
    sb, _ = board_in(tmp_path, photo, board, {"type": "screen", "image": "pic.png"}, format="wide")
    assert draw_scene(sb.scenes[0], 1.0, frame_size(0.2, "wide")).getbbox()


def test_screen_field_errors(tmp_path, photo, board):
    (tmp_path / "pic.png").write_bytes(photo.read_bytes())
    bad = [({"zoom": [0.5, 0.5, 0.5, 0.9]}, "'zoom' must be"), ({"cursor": [2, 0]}, "'cursor' must be"),
           ({"click": -1, "cursor": [0.1, 0.1]}, "'click' must be"), ({"click": 1}, "needs a 'cursor'"),
           ({"url": "x" * 200}, "'url' must be"), ({"say": ""}, "'say' must be")]
    for extra, needle in bad:
        _, errs, _ = validate(board({**{"type": "screen", "image": "pic.png"}, **extra}), tmp_path)
        assert any(needle in e for e in errs), (extra, errs)
    _, errs, _ = validate(board({"type": "screen"}), tmp_path)
    assert any("'image' must be a file path" in e for e in errs)
    _, errs, _ = validate(board({"type": "link"}), tmp_path)
    assert any("'text' is required" in e for e in errs)


def test_view_box_keeps_aspect_and_stays_inside():
    full = view_box((1000, 500), (400, 200), None, 0)
    assert full == (0.0, 0.0, 1000.0, 500.0)
    end = view_box((1000, 500), (400, 200), (0.9, 0.9, 1.0, 1.0), 1)
    w, h = end[2] - end[0], end[3] - end[1]
    assert abs(w / h - 2) < 1e-6 and end[2] <= 1000 and end[3] <= 500
    mid = view_box((1000, 500), (400, 200), (0.9, 0.9, 1.0, 1.0), 0.5)
    assert full[0] <= mid[0] <= end[0]


def test_padded_fits_any_aspect(tmp_path):
    p = tmp_path / "tall.png"
    Image.new("RGB", (100, 300), (9, 9, 9)).save(p)
    assert padded(str(p), 2.0).size == (600, 300)
    assert padded(str(p), 1 / 3).size == (100, 300)
    w = tmp_path / "wide.png"
    Image.new("RGB", (400, 100), (9, 9, 9)).save(w)
    assert padded(str(w), 1.0).size == (400, 400)


def test_compare_side_by_side_in_wide(board, tmp_path):
    sb, _, _ = validate(board({"type": "compare", "left": {"title": "A", "items": ["x"]},
                               "right": {"title": "B", "items": ["y"]}}, format="wide"), tmp_path)
    c = Ctx(sb.scenes[0], frame_size(0.25, "wide"))
    assert c.wide and draw_scene(sb.scenes[0], 2.0, frame_size(0.25, "wide")).getbbox()


def test_captions_follow_narration(board, tmp_path):
    say = "First sentence here. Then a second, longer one that keeps going and going past nine words, ok? End"
    sb, _, _ = validate(board({"type": "title", "text": "Hi", "say": say, "duration": 6}), tmp_path)
    cues = captions.cues(sb)
    assert cues[0][2] == "First sentence here." and cues[-1][2] == "End"
    assert abs(cues[-1][1] - 6) < 1e-6 and len(cues) >= 3


def test_wide_metadata_has_no_shorts_tag_and_lint_lengths(board, tmp_path):
    sb, _, _ = validate(board({"type": "title", "text": "Hi"}, format="wide"), tmp_path)
    assert "#Shorts" not in captions.metadata_md(sb, 1920, 1080, 30)
    assert any("under 45s" in w for w in lint.lint(sb))
    long = board(*[{"type": "title", "text": "Hi", "duration": 14}], format="short")
    sb, _, _ = validate(long, tmp_path)
    assert any("long for a Short" in w for w in lint.lint(sb))


def test_wide_contact_sheet(tmp_path, photo, board):
    sb, _ = board_in(tmp_path, photo, board, SCREEN, {"type": "cta", "text": "Go"}, format="wide")
    out = contact_sheet(sb, tmp_path / "p.png")
    assert Image.open(out).width > Image.open(out).height
