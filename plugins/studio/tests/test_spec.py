import json

import pytest

from studiokit import spec
from studiokit.model import SpecError

TITLE = {"type": "title", "text": "Hello world"}


def errors(data, tmp_path=None):
    sb, errs, _ = spec.validate(data, tmp_path or ".")
    assert sb is None
    return errs


def test_example_is_valid(example):
    sb, errs, warns = spec.validate(example, "")
    assert not errs and not warns
    assert len(sb.scenes) == 8 and 25 <= sb.duration <= 35
    assert {s.theme for s in sb.scenes} == {"light", "dark"}


def test_defaults(board):
    sb, errs, _ = spec.validate(board(TITLE, TITLE, TITLE), ".")
    assert not errs
    assert [s.theme for s in sb.scenes] == ["light", "dark", "light"]
    assert [s.transition for s in sb.scenes] == ["cut", "slide", "slide"]
    assert [s.start for s in sb.scenes] == pytest.approx([0, sb.scenes[0].duration, 2 * sb.scenes[0].duration])


def test_top_level_errors(board):
    assert "storyboard must be a JSON object" in spec.validate([], ".")[1]
    assert any("Did you mean 'scenes'" in e for e in errors({"title": "x", "scene": []}))
    assert any("'scenes' must be a list" in e for e in errors(board()))
    assert any("'title' is required" in e for e in errors({"scenes": [TITLE]}))
    assert any("top-level 'accent'" in e for e in errors(board(TITLE, accent="nope")))
    assert any("'audio' must be an existing file" in e for e in errors(board(TITLE, audio="missing.wav")))


@pytest.mark.parametrize("scene,needle", [
    ({"type": "nope"}, "scene 0: 'type' must be one of"),
    ({"type": "tilte", "text": "x"}, "Did you mean 'title'"),
    ({}, "'type' is required"),
    ("text", "scene 0: must be an object"),
    ({"type": "title"}, "scene 0 (title): 'text' is required"),
    ({"type": "title", "text": "x" * 200}, "limit is 140"),
    ({"type": "title", "text": "x", "txt": 1}, "unknown field 'txt'"),
    ({"type": "title", "text": "x", "theme": "blue"}, "'theme' must be 'light' or 'dark'"),
    ({"type": "title", "text": "x", "accent": "#12"}, "'accent' must be a name"),
    ({"type": "title", "text": "x", "transition": "fadee"}, "Did you mean 'fade'"),
    ({"type": "title", "text": "x", "duration": 99}, "between 1 and 12"),
    ({"type": "title", "text": "x", "duration": True}, "between 1 and 12"),
    ({"type": "bullets", "items": []}, "'items' must be a list of 1-4"),
    ({"type": "bullets", "items": ["a"] * 5}, "'items' must be a list of 1-4"),
    ({"type": "stat", "value": "9", "label": "x"}, "'value' must be a number"),
    ({"type": "stat", "value": 9}, "'label' is required"),
    ({"type": "stat", "value": 9, "label": "x", "suffix": 3}, "must be strings"),
    ({"type": "compare", "left": "a", "right": {}}, "'left' must be an object"),
    ({"type": "compare", "left": {"title": "a", "items": ["x"], "foo": 1}, "right": {"title": "b", "items": ["y"]}},
     "'left.foo' is not allowed"),
    ({"type": "compare", "left": {"title": "a", "items": []}, "right": {"title": "b", "items": ["y"]}},
     "'left.items' must be a list of 1-3"),
    ({"type": "image"}, "'image' must be a file path"),
    ({"type": "image", "image": "pic.gif"}, "image must be one of"),
    ({"type": "image", "image": "gone.png"}, "image file not found"),
])
def test_scene_errors_name_the_scene(board, scene, needle, tmp_path):
    errs = errors(board(scene), tmp_path)
    assert any(needle in e for e in errs), errs


def test_error_index_points_at_the_bad_scene(board):
    errs = errors(board(TITLE, TITLE, {"type": "stat", "value": "x", "label": "y"}))
    assert errs == ["scene 2 (stat): 'value' must be a number (use 'prefix'/'suffix' for $ or %)"]


def test_all_scene_types(board, photo):
    sb, errs, _ = spec.validate(board(
        TITLE,
        {"type": "bullets", "text": "Head", "items": ["a", "b"]},
        {"type": "stat", "value": 4.5, "label": "stars", "prefix": "$", "accent": "#112233"},
        {"type": "compare", "left": {"title": "A", "items": ["x"]}, "right": {"title": "B", "items": ["y"]}},
        {"type": "quote", "text": "Q", "author": "Me"},
        {"type": "image", "image": photo.name, "text": "cap"},
        {"type": "cta", "text": "Go", "sub": "Follow"}), photo.parent)
    assert not errs and sb.scenes[2].accent == (17, 34, 51) and sb.scenes[5].image == photo
    assert sb.scenes[3].words() == 4 and sb.scenes[2].visible_text() == ["$4.5", "stars"]


def test_warnings(board):
    scenes = [{"type": "cta", "text": "one two three four five six seven eight nine", "duration": 1.0,
               "accent": "yellow", "theme": "light"},
              {"type": "title", "text": "End", "duration": 5}]
    sb, errs, warns = spec.validate(board(*scenes), ".")
    text = "\n".join(warns)
    for needle in ("under 15s", "open with", "end with a 'cta'", "9 words", "too short to read",
                   "accent contrast"):
        assert needle in text


def test_slow_hook_warning(board):
    _, _, warns = spec.validate(board({"type": "title", "text": "Hi", "duration": 6}, TITLE), ".")
    assert any("hook scene runs 6s" in w for w in warns)


def test_length_warnings(board):
    long = [{"type": "title", "text": "Hi", "duration": 4}] * 16
    _, _, warns = spec.validate(board(*long), ".")
    assert any("over 60s" in w for w in warns) and any("16 scenes" in w for w in warns)


def test_meta_validation(board):
    assert any("meta" in e for e in errors(board(TITLE, meta={"titles": "x"})))
    sb, errs, _ = spec.validate(board(TITLE, meta={"titles": ["a"], "hashtags": ["x"]}), ".")
    assert not errs and sb.meta["titles"] == ["a"]


def test_audio_resolves_relative(board, tmp_path):
    (tmp_path / "v.wav").write_bytes(b"x")
    sb, errs, _ = spec.validate(board(TITLE, audio="v.wav"), tmp_path)
    assert not errs and sb.audio == (tmp_path / "v.wav").resolve()


def test_load_errors(tmp_path):
    p = tmp_path / "s.json"
    with pytest.raises(SpecError, match="cannot read"):
        spec.load(p)
    p.write_text("{nope", encoding="utf-8")
    with pytest.raises(SpecError, match="not valid JSON"):
        spec.load(p)
    p.write_text(json.dumps({"title": "x", "scenes": [{"type": "title"}]}), encoding="utf-8")
    with pytest.raises(SpecError, match="scene 0 .title.: 'text' is required"):
        spec.load(p)


def test_load_ok(tmp_path, example):
    p = tmp_path / "s.json"
    p.write_text(json.dumps(example), encoding="utf-8")
    sb, warns = spec.load(p)
    assert sb.title == "What is a Claude skill?" and warns == []
