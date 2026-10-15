"""Render a selected GUI root, type, or template using installed game assets.

Example: python run.py --workspace <repo> --mod-root src --name MyTemplate
--gui-file prototype.gui --output prototype.png
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))


def _target(db, expander, name: str, gui_file: Path | None):
    if name in db.templates:
        for node in db.templates[name]:
            if node.is_block() and expander.is_element_key(node.key):
                return expander.build(node.key, node.value, {}, node.src, node.line)
        raise ValueError(f"template has no root element: {name}")
    if name in db.types or expander.is_element_key(name):
        return expander.build(name, [], {}, "<type>", 0)
    roots = list(db.roots.items())
    if gui_file is not None:
        roots.sort(key=lambda item: item[0] != str(gui_file))
    for path, nodes in roots:
        for node in nodes:
            if not node.is_block():
                continue
            if node.key == name or any(child.key == "name" and child.value == name for child in node.value):
                return expander.build(node.key, node.value, {}, path, node.line)
    raise ValueError(f"GUI root, type, or template not found: {name}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="GUI root name, type, or template")
    parser.add_argument("--gui-file", type=Path, help="extra .gui file for a prototype")
    parser.add_argument("--mocks", type=Path, help="JSON list of [expression regex, value] pairs")
    parser.add_argument("--output", type=Path, help="PNG file, relative to output root")
    parser.add_argument("--width", type=int, default=800)
    parser.add_argument("--height", type=int, default=600)
    parser.add_argument("--scale", type=float, default=1.0)
    parser.add_argument("--language", default="simp_chinese")
    parser.add_argument("--workspace", type=Path)
    parser.add_argument("--mod-root", type=Path)
    parser.add_argument("--game-root", type=Path)
    parser.add_argument("--output-root", type=Path)
    args = parser.parse_args(argv)
    if args.width <= 0 or args.height <= 0 or args.scale <= 0:
        parser.error("width, height, and scale must be positive")
    for name, value in (("EU5_RENDER_WORKSPACE", args.workspace),
                        ("EU5_RENDER_MOD_ROOT", args.mod_root),
                        ("EU5_RENDER_GAME_ROOT", args.game_root),
                        ("EU5_RENDER_OUTPUT_ROOT", args.output_root)):
        if value is not None:
            os.environ[name] = str(value)
    os.environ["EU5_RENDER_LANGUAGE"] = args.language

    from PIL import Image
    from eu5_gui_renderer.data import Evaluator, Formats, Loc, TextIcons
    from eu5_gui_renderer.engine import Engine
    from eu5_gui_renderer.gui import Expander, GuiDB, collect_files, dump
    from eu5_gui_renderer.paths import OUTPUT, WORKSPACE
    from eu5_gui_renderer.textures import TEXTURES

    extra = args.gui_file
    if extra is not None and not extra.is_absolute():
        extra = WORKSPACE / extra
    if extra is not None:
        extra = extra.resolve()
        if not extra.is_file():
            parser.error(f"GUI file does not exist: {extra}")
    files = collect_files()
    if extra is not None:
        files.append(extra)
    db = GuiDB(files)
    log: list[str] = []
    expander = Expander(db, log)
    element = _target(db, expander, args.name, extra)
    mocks = []
    if args.mocks is not None:
        path = args.mocks if args.mocks.is_absolute() else WORKSPACE / args.mocks
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        mocks = payload.get("mocks", []) if isinstance(payload, dict) else payload
        if not isinstance(mocks, list):
            parser.error("mocks JSON must be a list of [regex, value] pairs")
    loc = Loc()
    evaluator = Evaluator(mocks, loc, log)
    engine = Engine(expander, evaluator, loc, Formats(), TextIcons(), args.scale)
    engine.place(element, 0, 0, args.width, args.height)
    image = Image.new("RGBA", (round(args.width * args.scale), round(args.height * args.scale)), (29, 35, 42, 255))
    engine.render(element, image)
    output = args.output or Path(f"{args.name}.png")
    if not output.is_absolute():
        output = OUTPUT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    tree = output.with_name(output.stem + "_tree.txt")
    tree.write_text("\n".join(dump(element)) + "\n", encoding="utf-8")
    print(f"Rendered {output}")
    print(f"Element tree {tree}")
    print(f"Unknown expressions: {len(set(log))}; missing textures: {len(TEXTURES.missing)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
