"""Render a GUI root/type/template or vanilla HUD using the shared preview pipeline."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--name", help="GUI root name, type, or template")
    target.add_argument("--scenario", choices=["hud"], help="Built-in sample-data screen")
    parser.add_argument("--gui-file", type=Path, help="extra .gui file for a prototype")
    parser.add_argument("--mocks", type=Path, help="JSON list of [expression regex, value] pairs")
    parser.add_argument("--output", type=Path, help="PNG file, relative to output root")
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--scale", type=float, default=1)
    parser.add_argument("--language", default="simp_chinese")
    parser.add_argument("--workspace", type=Path)
    parser.add_argument("--mod-root", type=Path)
    parser.add_argument("--game-root", type=Path)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--strict", action="store_true", help="exit nonzero on unresolved bindings or assets")
    args = parser.parse_args(argv)
    width = args.width if args.width is not None else 1920 if args.scenario == "hud" else 800
    height = args.height if args.height is not None else 1080 if args.scenario == "hud" else 600
    try:
        from eu5_gui_renderer.config import configure_paths
        configure_paths(workspace=args.workspace, mod_root=args.mod_root, game_root=args.game_root,
                        output_root=args.output_root, language=args.language)
        from eu5_gui_renderer.fixtures import load_mocks
        from eu5_gui_renderer.gui import Expander, build_target
        from eu5_gui_renderer.paths import WORKSPACE
        from eu5_gui_renderer.preview import has_diagnostics, load_resources, render_tree

        extra = (WORKSPACE / args.gui_file).resolve() if args.gui_file else None
        resources = load_resources(extra_files=[extra] if extra else None)
        expander = Expander(resources.db)
        unsupported = []
        if args.scenario == "hud":
            from eu5_gui_renderer import hud
            element = hud.build(resources.db, expander, width, height)
            mocks = hud.mocks()
            unsupported = list(hud.UNSUPPORTED)
        else:
            element = build_target(resources.db, expander, args.name, extra)
            mocks = []
        if args.mocks:
            mocks = load_mocks(WORKSPACE / args.mocks) + mocks
        report = render_tree(element, expander, resources, mocks, width=width, height=height,
            scale=args.scale, output=args.output or Path(f"{args.scenario or args.name}.png"),
            metadata={"scenario": args.scenario, "sample_data": bool(args.scenario), "unsupported": unsupported},
            top_detail_height=300 if args.scenario == "hud" else None)
        print(f"Rendered {report['output']}")
        print(f"Element tree {report['tree']}")
        print(f"Unknown expressions: {len(report['unknown_expressions'])}; "
              f"missing textures: {len(report['missing_textures'])}; "
              f"missing localizations: {len(report['missing_localizations'])}")
        return int(args.strict and has_diagnostics(report))
    except (ValueError, OSError, re.error) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
