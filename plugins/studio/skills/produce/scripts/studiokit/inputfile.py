"""Safe input files: `prep` makes a fresh private temp folder; only files inside such a folder are read or deleted."""
import os
import stat
import tempfile
from pathlib import Path

PREFIX = "studio-in-"
MAX_BYTES = 200_000


class InputFileError(ValueError):
    pass


def tmp_root() -> Path:
    return Path(tempfile.gettempdir()).resolve()


def prep(name: str = "input.txt") -> Path:
    """Create an unpredictable 0700 temp folder and return the path HQ must write to."""
    return Path(tempfile.mkdtemp(prefix=PREFIX, dir=tmp_root())) / name


def _check_dir(folder: Path) -> None:
    st = folder.lstat() if folder.exists() or folder.is_symlink() else None
    if st is None or stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode):
        raise InputFileError("the input file must be inside a folder made by the prep command")
    if folder.parent != tmp_root() or not folder.name.startswith(PREFIX):
        raise InputFileError("the input file must be inside a folder made by the prep command")
    if hasattr(os, "getuid") and st.st_uid != os.getuid():
        raise InputFileError("the prep folder is not owned by you")


def read_prep_file(file: str | os.PathLike) -> tuple[str, Path]:
    """Return (text, path). Refuses symlinks and anything outside a prep folder. Call discard(path) after a good parse."""
    path = Path(os.path.abspath(file))
    _check_dir(path.parent)
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    except OSError as e:
        raise InputFileError("cannot read the input file (symlinks are refused)") from e
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise InputFileError("the input file is not a regular file")
        data = os.read(fd, MAX_BYTES)
    finally:
        os.close(fd)
    return data.decode("utf-8", errors="replace"), path


def discard(path: Path) -> None:
    """Delete the input file and its prep folder (best effort, only ever called on a validated prep path)."""
    path.unlink(missing_ok=True)
    try:
        path.parent.rmdir()
    except OSError:
        pass
