import dataclasses
import subprocess

import pytest

from conftest import needs_ffmpeg
from studiokit import captions, ffmpeg, spec
from studiokit.model import SpecError
from studiokit.render import fit_to_audio, frames, render

TWO_SEC = {"title": "Tiny", "scenes": [
    {"type": "title", "text": "Hi there", "duration": 1.0},
    {"type": "cta", "text": "Bye", "sub": "Follow", "duration": 1.0, "transition": "fade"}]}


def load(data, base="."):
    sb, errs, _ = spec.validate(data, base)
    assert not errs, errs
    return sb


def test_srt_timing(example):
    sb = load(example)
    cs = captions.cues(sb)
    assert cs[0][0] == 0 and cs[-1][1] == pytest.approx(sb.duration)
    assert all(a < b for a, b, _ in cs)
    assert all(x[1] == pytest.approx(y[0]) for x, y in zip(cs, cs[1:]))   # no gaps, no overlap
    srt = captions.to_srt(sb)
    assert srt.startswith("1\n00:00:00,000 --> 00:00:03,000\nWhat is a Claude skill?")
    assert srt.count(" --> ") == len(cs)


def test_stamp_format():
    assert captions.stamp(0) == "00:00:00,000"
    assert captions.stamp(61.5) == "00:01:01,500"
    assert captions.stamp(3723.004) == "01:02:03,004"


def test_cue_text_for_every_type(photo):
    sb = load({"title": "t", "scenes": [
        {"type": "bullets", "text": "H", "items": ["a", "b"]},
        {"type": "stat", "value": 1200, "label": "views", "suffix": "+"},
        {"type": "compare", "left": {"title": "A", "items": ["x"]}, "right": {"title": "B", "items": ["y", "z"]}},
        {"type": "quote", "text": "Q", "author": "Me"},
        {"type": "image", "image": photo.name},
        {"type": "cta", "text": "Go"}]}, photo.parent)
    texts = [t for _, _, t in captions.cues(sb)]
    assert texts == ["H", "a", "b", "1,200+ views", "A: x", "B: y, z", "Q", "- Me", "Go"]


def test_metadata_fallbacks_and_hashtags():
    sb = load(TWO_SEC)
    md = captions.metadata_md(sb, 1080, 1920, 30)
    assert "1. Tiny" in md and "#Shorts" in md and "Hi there Bye" in md and "1080x1920" in md
    sb = load(dict(TWO_SEC, meta={"titles": ["A" * 150], "hashtags": ["#shorts", "ai"]}))
    md = captions.metadata_md(sb, 1080, 1920, 30)
    assert md.count("#Shorts") + md.count("#shorts") == 1 and "#ai" in md and "A" * 101 not in md


def test_fit_to_audio():
    sb = load(TWO_SEC)
    out = fit_to_audio(sb, 3.0)
    assert out.duration == pytest.approx(3.0) and out.scenes[1].start == pytest.approx(1.5)
    with pytest.raises(ffmpeg.FfmpegError, match="too far apart"):
        fit_to_audio(sb, 10)


def test_frame_count_and_transition_frames():
    sb = load(TWO_SEC)
    imgs = list(frames(sb, (54, 96), 10))
    assert len(imgs) == 20 and all(i.size == (54, 96) for i in imgs)


def test_encoder_rejects_wrong_frame_and_missing_ffmpeg(monkeypatch, tmp_path):
    from PIL import Image
    if ffmpeg.find_tool("ffmpeg"):
        enc = ffmpeg.Encoder(tmp_path / "a.mp4", (16, 16))
        with pytest.raises(ValueError):
            enc.write(Image.new("RGB", (8, 8)))
        enc.abort()
    monkeypatch.setattr(ffmpeg, "find_tool", lambda n: None)
    with pytest.raises(ffmpeg.FfmpegError, match="never installs"):
        ffmpeg.require()
    with pytest.raises(ffmpeg.FfmpegError):
        ffmpeg.probe_seconds(tmp_path / "x")


@needs_ffmpeg
def test_end_to_end_tiny_render(tmp_path):
    sb = load(TWO_SEC)
    logs = []
    res = render(sb, tmp_path / "out", scale=0.25, fps=15, log=logs.append)
    assert res["video"].stat().st_size > 1000
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                            "stream=codec_name,width,height,pix_fmt,r_frame_rate:format=duration", "-of", "default=nw=1",
                            str(res["video"])], capture_output=True, text=True).stdout
    for line in ("codec_name=h264", "width=270", "height=480", "pix_fmt=yuv420p", "r_frame_rate=15/1"):
        assert line in probe
    assert float(probe.split("duration=")[1]) == pytest.approx(2.0, abs=0.15)
    assert "1\n00:00:00,000" in res["captions"].read_text() and "# Upload metadata" in res["metadata"].read_text()


@needs_ffmpeg
def test_render_with_audio_fit(tmp_path):
    wav = tmp_path / "tone.wav"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "lavfi", "-i", "sine=frequency=440:duration=2.5",
                    str(wav)], check=True)
    sb = dataclasses.replace(load(TWO_SEC), audio=None)
    res = render(sb, tmp_path / "o", scale=0.25, fps=10, audio=wav, fit_audio=True, log=lambda m: None)
    assert ffmpeg.probe_seconds(res["video"]) == pytest.approx(2.5, abs=0.2)
    streams = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type", "-of", "csv=p=0",
                              str(res["video"])], capture_output=True, text=True).stdout.split()
    assert sorted(streams) == ["audio", "video"]


@needs_ffmpeg
def test_encoder_failure_is_reported(tmp_path):
    with pytest.raises(ffmpeg.FfmpegError, match="ffmpeg failed"):
        enc = ffmpeg.Encoder(tmp_path / "no-such-dir" / "x.mp4", (16, 16))
        from PIL import Image
        for _ in range(3):
            enc.write(Image.new("RGB", (16, 16)))
        enc.close()


def test_spec_error_type():
    assert issubclass(SpecError, ValueError)
