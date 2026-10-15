"""Print GUI type/template definitions from the selected game and mod roots."""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

# runpy shims do not add the script directory to sys.path.
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

DEF_RE = re.compile(r"^\s*(template|type)\s+([A-Za-z0-9_]+)\b")


def extract(lines: list[str], start: int) -> list[str]:
    depth, out, opened = 0, [], False
    for line in lines[start:]:
        code = line.split("#", 1)[0]
        out.append(line)
        depth += code.count("{") - code.count("}")
        if "{" in code:
            opened = True
        if opened and depth <= 0:
            break
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("names", nargs="+", metavar="TYPE_OR_TEMPLATE")
    parser.add_argument("--workspace", type=Path)
    parser.add_argument("--mod-root", type=Path)
    parser.add_argument("--game-root", type=Path)
    parser.add_argument("--output-root", type=Path)
    args = parser.parse_args(argv)
    for name, value in (("EU5_RENDER_WORKSPACE", args.workspace),
                        ("EU5_RENDER_MOD_ROOT", args.mod_root),
                        ("EU5_RENDER_GAME_ROOT", args.game_root),
                        ("EU5_RENDER_OUTPUT_ROOT", args.output_root)):
        if value is not None:
            os.environ[name] = str(value)

    from eu5_gui_renderer.gui import collect_files

    found: set[str] = set()
    wanted = set(args.names)
    for path in collect_files():
        lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
        for index, line in enumerate(lines):
            match = DEF_RE.match(line)
            if match and match.group(2) in wanted:
                found.add(match.group(2))
                print(f"===== {match.group(2)} ({path}:{index + 1})")
                print("\n".join(extract(lines, index)))
    missing = wanted - found
    if missing:
        print("Not found: " + ", ".join(sorted(missing)), file=sys.stderr)
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
