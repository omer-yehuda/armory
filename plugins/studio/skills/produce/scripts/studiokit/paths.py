"""Where things live: skill assets (read-only), the private venv, and ffmpeg."""
import os
import shutil
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[2]
PLUGIN_DIR = SKILL_DIR.parents[1]
FONT = SKILL_DIR / "assets" / "fonts" / "Rubik.ttf"
REQUIREMENTS = PLUGIN_DIR / "requirements.txt"
REQUIREMENTS_VOICE = PLUGIN_DIR / "requirements-voice.txt"


def home() -> Path:
    """Data dir for the venv. Override with STUDIO_HOME."""
    env = os.environ.get("STUDIO_HOME")
    return Path(env) if env else Path.home() / ".cache" / "studio-plugin"


def venv_dir() -> Path:
    return home() / "venv"


def venv_python(venv: Path | None = None) -> Path:
    v = venv or venv_dir()
    return v / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def in_venv(venv: Path | None = None) -> bool:
    v = (venv or venv_dir()).resolve()
    try:
        return Path(sys.prefix).resolve() == v
    except OSError:
        return False


def find_tool(name: str) -> str | None:
    """Locate ffmpeg/ffprobe on PATH. Never installs anything."""
    return shutil.which(name)


FFMPEG_HELP = (
    "ffmpeg was not found on PATH. Studio never installs system packages. Install it yourself:\n"
    "  macOS:   brew install ffmpeg\n"
    "  Ubuntu:  sudo apt install ffmpeg\n"
    "  Windows: winget install Gyan.FFmpeg\n"
    "then open a new terminal and retry."
)
