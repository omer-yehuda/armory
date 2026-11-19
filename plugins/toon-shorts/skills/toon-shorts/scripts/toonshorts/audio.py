"""ffmpeg discovery (never installs anything), decoding and the final mix (voice + sfx + ducked music)."""
import math
import shutil
import subprocess
import wave

import numpy as np

from . import SR


class FfmpegMissing(RuntimeError):
    pass


def find_ffmpeg(explicit: str | None = None) -> str:
    if explicit:
        return explicit
    on_path = shutil.which("ffmpeg")
    if on_path:
        return on_path
    try:
        import imageio_ffmpeg   # pinned in requirements.txt, installed by `toon.py setup`
        return imageio_ffmpeg.get_ffmpeg_exe()
    except (ImportError, RuntimeError) as e:
        raise FfmpegMissing("ffmpeg not found. Run `python toon.py setup` (installs the pinned imageio-ffmpeg "
                            "into the toon-shorts venv) or install ffmpeg yourself.") from e


def decode(ffmpeg: str, path: str) -> np.ndarray:
    """any audio file -> mono float32 at SR"""
    raw = subprocess.run([ffmpeg, "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def whoosh(seconds: float = 0.4, seed: int = 1) -> np.ndarray:
    n = int(SR * seconds)
    noise = np.random.default_rng(seed).standard_normal(n).astype(np.float32)
    noise = np.convolve(noise, np.ones(20) / 20, mode="same")
    return (noise * np.sin(np.linspace(0, math.pi, n)) ** 2 * 0.5).astype(np.float32)


def pop(seconds: float = 0.12) -> np.ndarray:
    t = np.linspace(0, seconds, int(SR * seconds), dtype=np.float32)
    return (np.sin(2 * math.pi * (900 - 4000 * t) * t) * np.exp(-t * 40) * 0.6).astype(np.float32)


def mix(voice: np.ndarray | None, cuts: list[float], pops: list[float], total: float,
        music: np.ndarray | None = None, sfx: bool = True) -> np.ndarray:
    n = int(total * SR) + SR
    out = np.zeros(n, np.float32)
    if voice is not None:
        out[: min(n, len(voice))] += voice[:n]
    if sfx:
        for i, t in enumerate(cuts):
            w = whoosh(seed=i + 1)
            a = max(0, int((t - 0.2) * SR))
            out[a:a + len(w)] += w[: max(0, n - a)] * 0.14
        for t in pops:
            pp = pop()
            a = max(0, int(t * SR))
            out[a:a + len(pp)] += pp[: max(0, n - a)] * 0.18
    if music is not None and len(music):
        m = np.tile(music, n // len(music) + 1)[:n]
        duck = np.ones(n, np.float32)
        if voice is not None:
            v = np.abs(np.pad(voice, (0, max(0, n - len(voice))))[:n])
            env = np.convolve(v, np.ones(4410) / 4410, "same")
            duck = 1 - 0.7 * np.clip(env / (env.max() * 0.25 + 1e-9), 0, 1)
        fade = np.ones(n, np.float32)
        fl = int(1.5 * SR)
        fade[-fl:] = np.linspace(1, 0, fl)
        out += m * 0.16 * duck * fade
    peak = float(np.abs(out).max()) if len(out) else 0.0
    if peak > 0.98:
        out *= 0.98 / peak
    return out


def write_wav(path: str, x: np.ndarray, sr: int = SR) -> None:
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
