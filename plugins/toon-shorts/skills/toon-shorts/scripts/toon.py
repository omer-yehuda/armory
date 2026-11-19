#!/usr/bin/env python3
"""toon-shorts entry point.

Runs inside the private venv created by `python toon.py setup` (~/.cache/toon-shorts/venv,
override with TOON_SHORTS_HOME). If called with another interpreter it hands over to the
venv. It never installs anything unless you run `setup`.
"""
import os
import subprocess
import sys

if sys.version_info < (3, 11):
    sys.exit("toon-shorts needs Python 3.11 or newer (found %d.%d)." % sys.version_info[:2])

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from toonshorts.paths import in_venv, venv_python  # noqa: E402


def main() -> int:
    for stream in (sys.stdout, sys.stderr):   # Hebrew titles on a Windows console
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    args = sys.argv[1:]
    if args and args[0] == "setup":
        from toonshorts.cli import main as cli_main
        return cli_main(args)
    py = venv_python()
    if not in_venv() and py.exists() and os.environ.get("TOON_SHORTS_NO_VENV") != "1":
        return subprocess.call([str(py), os.path.abspath(__file__), *args])
    if args and args[0] not in ("check", "-h", "--help"):
        try:
            import numpy  # noqa: F401
            import PIL  # noqa: F401
        except ImportError:
            print("toon-shorts is not set up yet. Ask the user, then run:\n"
                  f"  python {os.path.abspath(__file__)} setup          (render engine)\n"
                  f"  python {os.path.abspath(__file__)} setup --voice  (adds the free AI voice)", file=sys.stderr)
            return 3
    from toonshorts.cli import main as cli_main
    return cli_main(args)


if __name__ == "__main__":
    sys.exit(main())
