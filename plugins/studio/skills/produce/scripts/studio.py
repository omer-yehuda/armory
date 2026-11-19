#!/usr/bin/env python3
"""Studio entry point.

Runs inside the private venv created by `python studio.py setup` (~/.cache/studio-plugin/venv,
override with STUDIO_HOME). With another interpreter it hands over to that venv. It never
installs anything unless you run `setup` and agree.
"""
import os
import subprocess
import sys

if sys.version_info < (3, 11):
    sys.exit("studio needs Python 3.11 or newer (found %d.%d)." % sys.version_info[:2])

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from studiokit.paths import in_venv, venv_python  # noqa: E402

NEEDS_PILLOW = {"preview", "render"}


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    args = sys.argv[1:]
    py = venv_python()
    if args and args[0] != "setup" and not in_venv() and py.exists() and os.environ.get("STUDIO_NO_VENV") != "1":
        return subprocess.call([str(py), os.path.abspath(__file__), *args])
    if args and args[0] in NEEDS_PILLOW:
        try:
            import PIL  # noqa: F401
        except ImportError:
            print("Studio is not set up yet. Ask the user, then run:\n"
                  f"  python {os.path.abspath(__file__)} setup --yes", file=sys.stderr)
            return 3
    from studiokit.cli import main as cli_main
    return cli_main(args)


if __name__ == "__main__":
    sys.exit(main())
