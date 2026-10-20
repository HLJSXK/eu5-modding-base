"""Shared resource loading, rendering and diagnostics for caller-owned scenarios."""
from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path

from PIL import Image

from .data import Evaluator, Formats, Loc, TextIcons
from .engine import Engine
from .gui import GuiDB, collect_files, dump
from .paths import GAME, OUTPUT
from .textures import TEXTURES

DIAGNOSTIC_KEYS = ("unknown_expressions", "unresolved_contexts", "missing_textures",
                   "unsupported_textcontexts", "missing_text", "missing_localizations")


@dataclass
class RenderResources:
    db: GuiDB
    loc: Loc
    formats: Formats
    icons: TextIcons


def load_resources(*, extra_files: list[Path] | None = None) -> RenderResources:
    if not (GAME / "loading_screen/fonts").is_dir():
        raise ValueError(f"Installed game fonts missing (use --game-root): {GAME}")
    files = collect_files()
    for path in extra_files or []:
        path = path.resolve()
        if not path.is_file():
            raise ValueError(f"GUI file does not exist: {path}")
        if path not in files:
            files.append(path)
    return RenderResources(GuiDB(files), Loc(), Formats(), TextIcons())


def has_diagnostics(report: dict) -> bool:
    return any(report[key] for key in DIAGNOSTIC_KEYS)


def write_report(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_tree(element, expander, resources: RenderResources, mocks: list, *,
                width: int, height: int, scale: float = 1, output: Path,
                metadata: dict | None = None, top_detail_height: int | None = None) -> dict:
    """Render a fresh expanded tree; metadata belongs to the calling scenario."""
    if width <= 0 or height <= 0 or not math.isfinite(scale) or scale <= 0:
        raise ValueError("width, height and scale must be positive and finite")
    size = round(width * scale), round(height * scale)
    if min(size) < 1:
        raise ValueError("scaled width and height must be at least one pixel")
    evaluator = Evaluator(mocks, resources.loc, expander.log)
    engine = Engine(expander, evaluator, resources.loc, resources.formats, resources.icons, scale)
    # Cached failures must still appear in every scene's own report.
    TEXTURES.load.cache_clear()
    TEXTURES.missing.clear()
    engine.place(element, 0, 0, width, height)
    image = Image.new("RGBA", size, (29, 35, 42, 255))
    engine.render(element, image)
    output = output if output.is_absolute() else OUTPUT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    tree = output.with_name(output.stem + "_tree.txt")
    tree.write_text("\n".join(dump(element)) + "\n", encoding="utf-8")
    report = {
        **(metadata or {}), "game_root": str(GAME), "size": [width, height], "scale": scale,
        "unknown_expressions": sorted(set(expander.log)),
        "unresolved_contexts": sorted(engine.unresolved_contexts),
        "unsupported_textcontexts": sorted(engine.unsupported_textcontexts),
        "missing_textures": sorted(TEXTURES.missing),
        "missing_text": sorted(set(engine.missing_text)),
        "missing_localizations": sorted(engine.missing_localizations | evaluator.missing_localizations),
        "output": str(output), "tree": str(tree),
    }
    write_report(output.with_name(output.stem + "_report.json"), report)
    if top_detail_height is not None:
        image.crop((0, 0, image.width, min(image.height, round(top_detail_height * scale)))).save(
            output.with_name(output.stem + "_top_detail.png"))
    return report
