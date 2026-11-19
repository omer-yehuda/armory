"""Where things live: skill assets (read-only) and the user's data dir (venv, models)."""
import os
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[2]
PLUGIN_DIR = SKILL_DIR.parents[1]
FONT = SKILL_DIR / "assets" / "fonts" / "Rubik.ttf"


def home() -> Path:
    """Data dir for the venv and models. Override with TOON_SHORTS_HOME."""
    env = os.environ.get("TOON_SHORTS_HOME")
    return Path(env) if env else Path.home() / ".cache" / "toon-shorts"


def venv_dir() -> Path:
    return home() / "venv"


def venv_python(venv: Path | None = None) -> Path:
    v = venv or venv_dir()
    return v / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def models_dir() -> Path:
    return home() / "models"


def in_venv(venv: Path | None = None) -> bool:
    v = (venv or venv_dir()).resolve()
    try:
        return Path(sys.prefix).resolve() == v
    except OSError:
        return False


def requirements(kind: str) -> Path:
    name = {"render": "requirements.txt", "voice": "requirements-voice.txt"}[kind]
    return PLUGIN_DIR / name
