"""Frame loop: scenes + transitions + progress bar -> Encoder."""
import dataclasses
from pathlib import Path

from . import captions
from .canvas import frame_size, progress_bar
from .ffmpeg import Encoder, FfmpegError, probe_seconds
from .motion import apply_transition, transition_length
from .safety import safe_file
from .scenes_media import draw_scene


def fit_to_audio(sb, seconds: float):
    """Scale every scene duration so the video matches the audio length."""
    k = seconds / sb.duration
    if not 0.6 <= k <= 1.8:
        raise FfmpegError(f"audio is {seconds:.1f}s but the storyboard is {sb.duration:.1f}s: too far apart to "
                          "stretch. Rewrite the scene durations to match the audio.")
    t, scenes = 0.0, []
    for s in sb.scenes:
        d = s.duration * k
        scenes.append(dataclasses.replace(s, duration=d, start=t))
        t += d
    return dataclasses.replace(sb, scenes=scenes)


def frames(sb, size, fps: int = 30):
    """Yield every frame of the video as an RGB image."""
    total = sb.duration
    prev_last = None
    for sc in sb.scenes:
        n0, n1 = round(sc.start * fps), round((sc.start + sc.duration) * fps)
        tl = transition_length(sc.transition, sc.duration) if prev_last is not None else 0.0
        for n in range(n0, n1):
            t = n / fps - sc.start
            img = draw_scene(sc, t, size)
            if t < tl:
                img = apply_transition(sc.transition, prev_last, img, t / tl)
            progress_bar(img, (n + 1) / (total * fps), sc.accent, sc.theme, sc.fmt)
            yield img
        prev_last = draw_scene(sc, sc.duration, size)


def render(sb, out_dir: Path, scale: float = 1.0, fps: int = 30, audio: Path | None = None,
           fit_audio: bool = False, log=print) -> dict:
    """Write video.mp4, captions.srt and metadata.md into out_dir. Returns their paths."""
    audio = audio or sb.audio
    if audio and fit_audio:
        sb = fit_to_audio(sb, probe_seconds(audio))
    size = frame_size(scale, sb.format)
    out_dir.mkdir(parents=True, exist_ok=True)
    video = safe_file(out_dir / "video.mp4", out_dir)
    srt, meta = safe_file(out_dir / "captions.srt", out_dir), safe_file(out_dir / "metadata.md", out_dir)
    enc = Encoder(video, size, fps, audio)
    n_total = round(sb.duration * fps)
    try:
        for i, img in enumerate(frames(sb, size, fps), 1):
            enc.write(img)
            if i % (fps * 5) == 0:
                log(f"  {i / n_total:4.0%} ({i}/{n_total} frames)")
        enc.close()
    except BaseException:
        enc.abort()
        raise
    srt.write_text(captions.to_srt(sb), encoding="utf-8")
    meta.write_text(captions.metadata_md(sb, *size, fps), encoding="utf-8")
    return {"video": video, "captions": srt, "metadata": meta}
