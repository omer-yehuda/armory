"""studio.py commands: init, doctor, setup, check, preview, render."""
import argparse
import sys
from datetime import date
from pathlib import Path

from .ffmpeg import FfmpegError
from .inputfile import InputFileError, discard, prep, read_prep_file
from .setup_env import SetupError
from .safety import git_tracked, new_dir, safe_file, safe_out_dir, slugify
from .spec import SpecError, load

EXIT_INVALID, EXIT_ERROR, EXIT_NOT_SETUP, EXIT_NO_FFMPEG = 1, 2, 3, 4


def check_state(root: Path) -> Path:
    studio = root / ".studio"
    if git_tracked(root, ".studio"):
        raise SpecError(".studio/ is tracked in git, so it came from the repository. Remove it from git first.")
    if studio.is_symlink() or (studio / "productions").is_symlink():
        raise SpecError(".studio is a symlink: refusing to use it")
    return studio


def cmd_init(a) -> int:
    """Create a production folder. The name comes from a text file (never from the command line)."""
    root = Path(a.root).resolve()
    text = a.slug or ""
    src = None
    if a.title_file:
        text, src = read_prep_file(a.title_file)
        text = text[:2000]
    studio = check_state(root)
    (studio / "productions").mkdir(parents=True, exist_ok=True)
    safe_file(studio / ".gitignore", studio).write_text("*\n", encoding="utf-8")   # keep productions out of git
    prod = new_dir(studio / "productions", f"{date.today().isoformat()}-{slugify(text)}")
    if a.title_file:
        (prod / "topic.txt").write_text(text, encoding="utf-8")
        discard(src)
    print(prod)
    return 0


def cmd_prep(a) -> int:
    """Print a fresh private path for free-text input (HQ writes there, then passes it to init)."""
    check_state(Path(a.root).resolve())
    print(prep("topic.txt"))
    return 0


def cmd_doctor(a) -> int:
    from .setup_env import ffmpeg_status
    try:
        import PIL
        pil = f"Pillow {PIL.__version__}"
    except ImportError:
        pil = None
    ok, msg = ffmpeg_status()
    print(f"python {sys.version.split()[0]}\n{pil or 'Pillow: MISSING (run setup)'}\n{msg}")
    return 0 if (pil and ok) else (EXIT_NOT_SETUP if not pil else EXIT_NO_FFMPEG)


def cmd_setup(a) -> int:
    from .setup_env import setup
    return setup(a.yes)


def cmd_check(a) -> int:
    try:
        sb, warns = load(a.storyboard)
    except SpecError as e:
        print("INVALID storyboard:\n" + "\n".join(f"  - {m}" for m in str(e).splitlines()))
        return EXIT_INVALID
    print(f"OK: {len(sb.scenes)} scenes, {sb.duration:.1f}s")
    for w in warns:
        print(f"  warning: {w}")
    return EXIT_INVALID if (warns and a.strict) else 0


def cmd_preview(a) -> int:
    from .preview import contact_sheet
    sb, warns = load(a.storyboard)
    anchor = Path(a.storyboard).resolve().parent
    out = safe_file(Path(a.out) if a.out else anchor / "preview.png", anchor)
    print(f"contact sheet -> {contact_sheet(sb, out, guides=not a.no_guides)}")
    for w in warns:
        print(f"  warning: {w}")
    return 0


def cmd_render(a) -> int:
    from .render import render
    sb, warns = load(a.storyboard)
    anchor = Path(a.storyboard).resolve().parent
    out = safe_out_dir(Path(a.out) if a.out else anchor, anchor)
    audio_arg = a.audio
    if a.audio_path_file:
        audio_arg = Path(a.audio_path_file).read_text(encoding="utf-8").strip().splitlines()[0]
    audio = Path(audio_arg).resolve() if audio_arg else None
    if audio and not audio.is_file():
        raise SpecError(f"audio file not found: {audio}")
    for w in warns:
        print(f"  warning: {w}")
    res = render(sb, out, a.scale, a.fps, audio, a.fit_audio, log=print)
    for k, v in res.items():
        print(f"{k}: {v}")
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="studio.py", description="Studio: kinetic-typography explainer renderer")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("init", help="create .studio/productions/<date>-<slug>/ (git-ignored)")
    s.add_argument("slug", nargs="?", help="legacy: sanitized; prefer --title-file")
    s.add_argument("--title-file", help="file from `prep` holding the topic; the folder name is derived from it, then it is deleted")
    s.add_argument("--root", default=".")
    s = sub.add_parser("prep", help="make a fresh private temp folder and print the input file path to write to")
    s.add_argument("--root", default=".")
    sub.add_parser("doctor", help="report Python, Pillow and ffmpeg status")
    s = sub.add_parser("setup", help="create the private venv and install pinned Pillow (asks first)")
    s.add_argument("--yes", action="store_true", help="the user already agreed")
    s = sub.add_parser("check", help="validate a storyboard (exit 1 if invalid)")
    s.add_argument("storyboard")
    s.add_argument("--strict", action="store_true", help="treat warnings as failures")
    s = sub.add_parser("preview", help="contact sheet PNG of one key frame per scene")
    s.add_argument("storyboard")
    s.add_argument("--out")
    s.add_argument("--no-guides", action="store_true", help="hide the safe-area outline")
    s = sub.add_parser("render", help="1080x1920 H.264 MP4 + captions.srt + metadata.md")
    s.add_argument("storyboard")
    s.add_argument("--out", help="output folder, inside the storyboard folder (default: the storyboard folder)")
    s.add_argument("--scale", type=float, default=1.0, help="0.1-1.0 of full size (tests use 0.25)")
    s.add_argument("--fps", type=int, default=30)
    s.add_argument("--audio", help="optional voice or music file to mux in")
    s.add_argument("--audio-path-file", help="text file whose first line is the audio path (keeps the path off the command line)")
    s.add_argument("--fit-audio", action="store_true", help="stretch scene timings to the audio length")
    return p


COMMANDS = {"prep": cmd_prep, "init": cmd_init, "doctor": cmd_doctor, "setup": cmd_setup, "check": cmd_check,
            "preview": cmd_preview, "render": cmd_render}


def main(argv: list[str] | None = None) -> int:
    a = parser().parse_args(argv)
    if a.cmd == "render" and not 0.1 <= a.scale <= 1.0:
        print("ERROR: --scale must be between 0.1 and 1.0", file=sys.stderr)
        return EXIT_ERROR
    try:
        return COMMANDS[a.cmd](a)
    except SpecError as e:
        print("ERROR:\n" + str(e), file=sys.stderr)
        return EXIT_INVALID
    except (FfmpegError, SetupError, InputFileError, OSError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return EXIT_NO_FFMPEG if "ffmpeg was not found" in str(e) else EXIT_ERROR
