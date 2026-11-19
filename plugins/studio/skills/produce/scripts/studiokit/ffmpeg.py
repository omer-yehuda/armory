"""ffmpeg plumbing: raw RGB frames are piped to stdin, so no temp PNG files are written."""
import subprocess
import tempfile
from pathlib import Path

from .paths import FFMPEG_HELP, find_tool


class FfmpegError(RuntimeError):
    pass


def require() -> str:
    exe = find_tool("ffmpeg")
    if not exe:
        raise FfmpegError(FFMPEG_HELP)
    return exe


def probe_seconds(path: Path) -> float:
    exe = find_tool("ffprobe")
    if not exe:
        raise FfmpegError("ffprobe was not found (it ships with ffmpeg).\n" + FFMPEG_HELP)
    r = subprocess.run([exe, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError as e:
        raise FfmpegError(f"could not read the length of {path}: {r.stderr.strip()[:200]}") from e


class Encoder:
    """Context manager: write PIL images, get an H.264 MP4."""

    def __init__(self, out: Path, size: tuple[int, int], fps: int = 30, audio: Path | None = None):
        w, h = size
        cmd = [require(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{w}x{h}", "-r", str(fps), "-i", "-"]
        if audio:
            cmd += ["-i", str(audio)]
        cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                "-movflags", "+faststart"]
        cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest"] if audio else ["-an"]
        self.size, self.err = size, tempfile.TemporaryFile()
        self.proc = subprocess.Popen(cmd + [str(out)], stdin=subprocess.PIPE, stderr=self.err)

    def _fail(self) -> FfmpegError:
        self.err.seek(0)
        return FfmpegError("ffmpeg failed: " + self.err.read().decode(errors="replace")[-600:].strip())

    def write(self, img) -> None:
        if img.size != self.size or img.mode != "RGB":
            raise ValueError(f"frame must be RGB {self.size}, got {img.mode} {img.size}")
        try:
            self.proc.stdin.write(img.tobytes())
        except BrokenPipeError:
            self.proc.wait()
            raise self._fail() from None

    def close(self) -> None:
        try:
            self.proc.stdin.close()
        except BrokenPipeError:
            pass
        if self.proc.wait() != 0:
            raise self._fail()
        self.err.close()

    def abort(self) -> None:
        self.proc.kill()
        self.proc.wait()
        self.err.close()
