"""Path and name safety: sanitized ids, outputs that stay inside one folder, no symlink writes."""
import re
import subprocess
from pathlib import Path

from .model import SpecError

MAX_SLUG = 48


def slugify(text: str, default: str = "video") -> str:
    """Lowercase [a-z0-9-] only, at most MAX_SLUG characters, never empty, never starts with '-'."""
    s = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")[:MAX_SLUG].strip("-")
    return s or default


def inside(path: Path, folder: Path) -> bool:
    try:
        path.resolve().relative_to(folder.resolve())
        return True
    except ValueError:
        return False


def require_inside(path: Path, folder: Path, what: str) -> Path:
    """Resolve path (following symlinks) and insist it stays inside folder."""
    if not inside(path, folder):
        raise SpecError(f"{what} must stay inside {folder}: {path}")
    return path.resolve()


def safe_out_dir(out: Path, anchor: Path) -> Path:
    """An output folder must be the anchor folder (the storyboard's) or live inside it."""
    return require_inside(out, anchor, "output folder")


def safe_file(path: Path, folder: Path) -> Path:
    """An output file inside folder that is not a symlink (writes would follow it out of the folder)."""
    if path.is_symlink():
        raise SpecError(f"refusing to write through a symlink: {path}")
    require_inside(path.parent, folder, "output path")
    return path


def git_tracked(root: Path, rel: str) -> bool:
    """True when git tracks anything under rel (state that came from a repository, not from this user)."""
    try:
        r = subprocess.run(["git", "-C", str(root), "ls-files", "--", rel], capture_output=True, text=True)
    except OSError:
        return False
    return r.returncode == 0 and bool(r.stdout.strip())


def new_dir(parent: Path, name: str) -> Path:
    """Create parent/name, or name-2, name-3 ... (never reuse a folder that may be a planted symlink)."""
    for n in range(1, 1000):
        p = parent / (name if n == 1 else f"{name}-{n}")
        try:
            p.mkdir()
            return p
        except FileExistsError:
            continue
    raise SpecError(f"too many productions named {name}")
