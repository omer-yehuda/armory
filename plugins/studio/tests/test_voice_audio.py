"""Narration (with a fake TTS engine), mastering, the audio check and the voice model download."""
import io
import json
import math

import numpy as np
import pytest

from conftest import needs_ffmpeg
from studiokit import audio, cli, models, setup_env, voice


class FakeTTS:
    """Stands in for Kokoro: a soft tone whose length follows the text."""
    def create(self, text, voice, speed, lang):
        n = int(voice_len(text) * 24000)
        t = np.arange(n) / 24000
        return (0.3 * np.sin(2 * math.pi * 180 * t)).astype(np.float32), 24000


def voice_len(text):
    return 0.25 + 0.06 * len(text.split())


def test_edges_fade_both_ends():
    x = audio.edges(np.ones(1000, np.float32), 24000)
    assert x[0] == 0 and x[-1] == 0 and x[500] == 1


def test_synth_rejects_unknown_voice():
    with pytest.raises(ValueError, match="unknown voice"):
        voice.synth("hi", "nobody", 1.0, FakeTTS())


def test_engine_needs_models(monkeypatch):
    voice._ENGINE.clear()
    with pytest.raises(models.ModelError, match="setup --voice"):
        voice.engine()


@needs_ffmpeg
def test_narrate_fits_durations_and_masters(tmp_path):
    board = {"title": "T", "format": "wide", "scenes": [
        {"type": "title", "text": "Hello there", "say": "Hello there, this is a test line."},
        {"type": "title", "text": "Quiet", "duration": 2},
        {"type": "cta", "text": "Bye", "say": "Bye now."}]}
    p = tmp_path / "storyboard.json"
    p.write_text(json.dumps(board))
    res = voice.narrate(p, "am_michael", 1.1, tts=FakeTTS(), log=lambda *a: None)
    data = json.loads(p.read_text())
    assert data["audio"] == "voice.wav" and data["scenes"][1]["duration"] == 2
    assert data["scenes"][0]["duration"] >= voice_len(board["scenes"][0]["say"])
    lines = json.loads(res["lines"].read_text())
    assert [ln["scene"] for ln in lines] == [0, 2]
    assert not (tmp_path / "voice.raw.wav").exists() and list((tmp_path / ".voice-cache").glob("*.npy"))
    voice.narrate(p, "am_michael", 1.1, tts=None, log=lambda *a: None)      # all lines cached: no engine needed
    check = audio.check(res["audio"], res["lines"])
    assert check["ok"], check
    assert abs(check["seconds"] - res["seconds"]) < 0.2


def test_narrate_needs_a_line_and_a_valid_board(tmp_path):
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"title": "T", "scenes": [{"type": "title", "text": "x"}]}))
    with pytest.raises(ValueError, match="no scene has a 'say'"):
        voice.narrate(p, tts=FakeTTS(), log=lambda *a: None)
    p.write_text(json.dumps({"title": "T", "scenes": [{"type": "nope"}]}))
    with pytest.raises(ValueError, match="fix the storyboard"):
        voice.narrate(p, tts=FakeTTS())


@needs_ffmpeg
def test_check_flags_loud_pauses_and_clicks(tmp_path):
    sr = 48000
    x = np.zeros(sr * 4, np.float32)
    x[: sr] = 0.2 * np.sin(np.arange(sr) * 2 * math.pi * 220 / sr)
    x[sr:2 * sr] = 0.1 * np.sin(np.arange(sr) * 2 * math.pi * 220 / sr)    # a "pause" that is not quiet
    for k in range(2 * sr + 100, 4 * sr, sr // 8):
        x[k:k + 3] += 0.9                                                  # clicks
    wav = audio.write_wav(tmp_path / "bad.wav", x, sr)
    lines = tmp_path / "l.json"
    lines.write_text(json.dumps([{"start": 0, "end": 0.9}, {"start": 2.1, "end": 3.9}]))
    res = audio.check(wav, lines)
    assert not res["ok"] and len(res["problems"]) == 2
    assert cli.main(["audiocheck", str(wav), "--lines", str(lines)]) == 1


def test_dbfs_and_tiny_clicks_input():
    assert audio.dbfs(np.zeros(10, np.float32)) == -120.0
    assert audio.clicks(np.zeros(10, np.float32), 48000) == 0


class Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


def test_model_fetch_verifies_hash(tmp_path, monkeypatch):
    data = b"model-bytes"
    import hashlib
    monkeypatch.setitem(models.MODELS, "m.bin", (hashlib.sha256(data).hexdigest(), len(data)))
    path = models.fetch("m.bin", tmp_path, log=lambda *a: None, opener=lambda req, timeout: Resp(data))
    assert path.read_bytes() == data and models.model_ok("m.bin", tmp_path)
    assert models.fetch("m.bin", tmp_path, opener=None) == path                     # already there
    monkeypatch.setitem(models.MODELS, "bad.bin", ("0" * 64, len(data)))
    with pytest.raises(models.ModelError, match="sha256 mismatch"):
        models.fetch("bad.bin", tmp_path, log=lambda *a: None, opener=lambda req, timeout: Resp(data))
    monkeypatch.setitem(models.MODELS, "big.bin", ("0" * 64, 3))
    with pytest.raises(models.ModelError, match="download failed"):
        models.fetch("big.bin", tmp_path, log=lambda *a: None, opener=lambda req, timeout: Resp(data))
    assert not list(tmp_path.glob("*.part"))


def test_setup_plan_mentions_voice_and_cli_guards(capsys):
    assert "Kokoro voice model" in setup_env.plan(voice=True)
    assert "Kokoro" not in setup_env.plan()
    assert cli.main(["voice", "x.json", "--speed", "3"]) == 2
    assert cli.main(["doctor"]) in (0, 3, 4)
    assert "voice:" in capsys.readouterr().out


@needs_ffmpeg
def test_cli_voice_command(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(voice, "engine", lambda: FakeTTS())
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"title": "T", "scenes": [{"type": "title", "text": "Hi", "say": "Hello, world."}]}))
    assert cli.main(["voice", str(p)]) == 0
    assert "voice.wav" in capsys.readouterr().out and (tmp_path / "voice.wav").is_file()
