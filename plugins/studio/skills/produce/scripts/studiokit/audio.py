"""Clean audio: faded edges, mastering (declick, 12 kHz low-pass, two-pass loudness to -14 LUFS) and a check
that pauses are quiet and there are no clicks. numpy is imported inside the functions that need it."""
import json
import math
import re
import subprocess
import wave
from pathlib import Path

from .ffmpeg import FfmpegError, require

TARGET_LUFS, TRUE_PEAK = -14.0, -1.5
PAUSE_DBFS = -35.0             # pauses between lines must stay below this
MAX_CLICKS_PER_MIN = 3.0


def edges(x, sr: int, ms: float = 6.0):
    """Fade both ends so a sound never starts or stops on a non-zero sample (that step is a click)."""
    import numpy as np
    x = np.asarray(x, np.float32).copy()
    k = min(len(x) // 2, int(sr * ms / 1000))
    if k > 0:
        ramp = np.sin(np.linspace(0, math.pi / 2, k, dtype=np.float32)) ** 2
        x[:k] *= ramp
        x[-k:] *= ramp[::-1]
    return x


def write_wav(path: Path, x, sr: int) -> Path:
    import numpy as np
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    return Path(path)


def _ff(args: list[str]) -> str:
    r = subprocess.run([require(), "-hide_banner", "-nostats", *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise FfmpegError("ffmpeg failed: " + r.stderr[-600:].strip())
    return r.stderr


def master(src: Path, out: Path) -> Path:
    """Two-pass loudnorm in linear mode (a plain gain, so silent pauses stay silent) after a declick and a
    12 kHz low-pass. Writes 48 kHz mono 16-bit WAV."""
    pre = "adeclick=w=55:o=75:t=2,lowpass=f=12000"
    probe = _ff(["-i", str(src), "-af", f"{pre},loudnorm=I={TARGET_LUFS}:TP={TRUE_PEAK}:LRA=11:print_format=json",
                 "-f", "null", "-"])
    m = json.loads(re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", probe)[-1])
    ln = (f"loudnorm=I={TARGET_LUFS}:TP={TRUE_PEAK}:LRA=11:linear=true:measured_I={m['input_i']}:"
          f"measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
          f"offset={m['target_offset']}")
    _ff(["-y", "-i", str(src), "-af", f"{pre},{ln}", "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(out)])
    return out


def decode(path: Path, sr: int = 48000):
    import numpy as np
    r = subprocess.run([require(), "-v", "error", "-i", str(path), "-vn", "-f", "f32le", "-ac", "1", "-ar", str(sr), "-"],
                       capture_output=True)
    if r.returncode != 0:
        raise FfmpegError(f"could not decode the audio of {path}: {r.stderr.decode(errors='replace')[-300:]}")
    return np.frombuffer(r.stdout, np.float32).copy()


def dbfs(x) -> float:
    import numpy as np
    rms = float(np.sqrt(np.mean(np.square(x)))) if len(x) else 0.0
    return 20 * math.log10(rms) if rms > 1e-9 else -120.0


def clicks(x, sr: int) -> int:
    """Broadband clicks: 5 ms windows whose energy above 12 kHz spikes far above both the local median and
    the windows 15 ms before and after (speech that starts or a hissy consonant lasts longer and is ignored)."""
    import numpy as np
    n = int(sr * 0.005)
    if len(x) < n * 4:
        return 0
    frames = x[: len(x) // n * n].reshape(-1, n) * np.hanning(n)
    spec = np.abs(np.fft.rfft(frames, axis=1)) ** 2
    hf = spec[:, int(12000 / (sr / 2) * spec.shape[1]):].sum(axis=1) + 1e-12
    db = 10 * np.log10(hf)
    pad = np.pad(db, 25, mode="edge")
    med = np.array([np.median(pad[i:i + 51]) for i in range(len(db))])
    side = np.maximum(pad[22:22 + len(db)], pad[28:28 + len(db)])    # 15 ms before and after
    hits = (db > med + 18) & (db > side + 12) & (db > -60)       # a short spike, not a sound starting
    return int(np.count_nonzero(hits[1:] & ~hits[:-1]) + (1 if len(hits) and hits[0] else 0))


def check(media: Path, lines: Path | None = None) -> dict:
    """{'ok', 'seconds', 'pause_dbfs' (loudest pause), 'clicks_per_min', 'problems'}."""
    sr = 48000
    x = decode(media, sr)
    seconds = len(x) / sr
    gaps = []
    if lines and Path(lines).is_file():
        spans = json.loads(Path(lines).read_text(encoding="utf-8"))
        for a, b in zip(spans, spans[1:]):
            if b["start"] - a["end"] > 0.2:
                gaps.append((a["end"] + 0.06, b["start"] - 0.06))
    pause = max((dbfs(x[int(a * sr):int(b * sr)]) for a, b in gaps), default=-120.0)
    cpm = clicks(x, sr) / max(seconds / 60, 1e-9)
    problems = []
    if pause > PAUSE_DBFS:
        problems.append(f"pauses are too loud: {pause:.1f} dBFS (want below {PAUSE_DBFS:g})")
    if cpm > MAX_CLICKS_PER_MIN:
        problems.append(f"{cpm:.1f} clicks per minute (want {MAX_CLICKS_PER_MIN:g} or fewer)")
    return {"ok": not problems, "seconds": round(seconds, 2), "pause_dbfs": round(pause, 1),
            "clicks_per_min": round(cpm, 1), "problems": problems}
