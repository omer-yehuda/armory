import pytest
from PIL import Image

from studiokit import motion, themes


@pytest.mark.parametrize("fn", [motion.ease_out_back, motion.ease_in_out_cubic, motion.ease_out_cubic])
def test_easing_endpoints_and_clamping(fn):
    assert fn(0) == pytest.approx(0) and fn(1) == pytest.approx(1)
    assert fn(-5) == pytest.approx(0) and fn(7) == pytest.approx(1)


def test_easing_bounds():
    xs = [i / 100 for i in range(101)]
    assert all(0 <= motion.ease_in_out_cubic(x) <= 1 for x in xs)
    assert all(0 <= motion.ease_out_cubic(x) <= 1 for x in xs)
    assert max(motion.ease_out_back(x) for x in xs) > 1.0          # overshoots (that is the pop)
    assert max(motion.ease_out_back(x) for x in xs) < 1.15         # but only a little
    assert all(b >= a for a, b in zip(map(motion.ease_in_out_cubic, xs), map(motion.ease_in_out_cubic, xs[1:])))
    assert motion.ease_in_out_cubic(0.5) == pytest.approx(0.5)


def test_pulse_loops():
    assert motion.pulse(0) == pytest.approx(0) and motion.pulse(0.6, 1.2) == pytest.approx(1)
    assert motion.pulse(1.2, 1.2) == pytest.approx(0)


def test_transition_length():
    assert motion.transition_length("cut", 3) == 0
    assert motion.transition_length("slide", 3) == motion.TRANSITION_SECONDS
    assert motion.transition_length("fade", 0.5) == pytest.approx(0.2)


@pytest.mark.parametrize("kind", motion.TRANSITIONS)
def test_transitions_keep_size_and_end_on_current(kind):
    prev, cur = Image.new("RGB", (60, 100), (255, 0, 0)), Image.new("RGB", (60, 100), (0, 0, 255))
    for p in (0.0, 0.3, 0.7):
        assert motion.apply_transition(kind, prev, cur, p).size == (60, 100)
    assert motion.apply_transition(kind, prev, cur, 1.0) is cur
    if kind != "cut":
        mid = motion.apply_transition(kind, prev, cur, 0.1)
        assert mid.tobytes() != cur.tobytes()


def test_slide_moves_both_scenes():
    prev, cur = Image.new("RGB", (100, 10), (255, 0, 0)), Image.new("RGB", (100, 10), (0, 0, 255))
    mid = motion.apply_transition("slide", prev, cur, 0.5)
    assert mid.getpixel((5, 5)) == (255, 0, 0) and mid.getpixel((95, 5)) == (0, 0, 255)


def test_unknown_transition():
    im = Image.new("RGB", (4, 4))
    with pytest.raises(ValueError):
        motion.apply_transition("wipe", im, im, 0.5)


def test_accents_and_contrast():
    assert themes.parse_accent("Coral") == themes.ACCENTS["coral"]
    assert themes.parse_accent("#0A0b0C") == (10, 11, 12)
    assert themes.parse_accent("#12345") is None and themes.parse_accent(5) is None
    assert themes.contrast((0, 0, 0), (255, 255, 255)) == pytest.approx(21)
    assert themes.contrast((9, 9, 9), (9, 9, 9)) == pytest.approx(1)


def test_palettes_are_readable():
    for pal in themes.PALETTES.values():
        assert themes.contrast(pal["fg"], pal["bg"]) > 12
        assert themes.contrast(pal["muted"], pal["bg"]) > 4.5


def test_lerp_and_on_accent():
    assert themes.lerp((0, 0, 0), (100, 200, 50), 0.5) == (50, 100, 25)
    assert themes.lerp((0, 0, 0), (10, 10, 10), 9) == (10, 10, 10)
    assert themes.on_accent((255, 255, 255)) == (20, 22, 26)
    assert themes.on_accent((10, 10, 10)) == (255, 255, 255)
