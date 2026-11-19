"""Consent-first setup: a private venv with pinned Pillow. ffmpeg is checked, never installed."""
import subprocess
import sys
from pathlib import Path

from .paths import FFMPEG_HELP, REQUIREMENTS, find_tool, venv_dir, venv_python


class SetupError(RuntimeError):
    pass


def ffmpeg_status() -> tuple[bool, str]:
    """(ok, message). Checks ffmpeg, ffprobe and the libx264 encoder."""
    exe = find_tool("ffmpeg")
    if not exe or not find_tool("ffprobe"):
        return False, FFMPEG_HELP
    r = subprocess.run([exe, "-hide_banner", "-encoders"], capture_output=True, text=True)
    if "libx264" not in r.stdout:
        return False, "ffmpeg is installed but has no libx264 encoder. Install a full build of ffmpeg."
    return True, f"ffmpeg ok ({exe})"


def confirmed(yes: bool, stdin=sys.stdin, ask=input) -> bool:
    """--yes (Claude passes it after asking the user) or an interactive y/N on a terminal."""
    if yes:
        return True
    if not stdin.isatty():
        return False
    return ask("Proceed? [y/N] ").strip().lower() in ("y", "yes")


def plan() -> str:
    pins = ", ".join(t for t in REQUIREMENTS.read_text().split() if "==" in t)
    return (f"Studio setup will:\n  1. create a private Python venv at {venv_dir()}\n"
            f"  2. pip install pinned, hash-checked wheels (no source builds) from PyPI into that venv only: {pins}\n"
            "It will not touch your global Python, install system packages, or contact anything else.")


def setup(yes: bool, log=print, stdin=sys.stdin, ask=input) -> int:
    log(plan())
    if not confirmed(yes, stdin, ask):
        raise SetupError("not confirmed, nothing was installed (pass --yes after the user agrees)")
    py = venv_python()
    if not py.exists():
        log(f"creating venv at {venv_dir()}")
        venv_dir().parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir())], check=True)
    r = subprocess.run([str(py), "-m", "pip", "install", "--disable-pip-version-check", "-q",
                        "--require-hashes", "--only-binary=:all:", "--no-input", "-r", str(Path(REQUIREMENTS))], capture_output=True, text=True)
    if r.returncode != 0:
        raise SetupError(f"pip failed (usually no network access to pypi.org):\n{r.stderr[-1500:]}")
    ok, msg = ffmpeg_status()
    log(msg)
    log(f"python packages ready in {venv_dir()}")
    return 0 if ok else 4
