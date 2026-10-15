"""Selected workspace, mod, installed-game, and render-output paths."""
from __future__ import annotations

import os
from pathlib import Path

DEFAULT_GAME = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis V\game")


def _path(name: str, default: Path, base: Path | None = None) -> Path:
    value = os.environ.get(name)
    path = Path(value).expanduser() if value else default
    if not path.is_absolute():
        path = (base or Path.cwd()) / path
    return path.resolve()


WORKSPACE = _path("EU5_RENDER_WORKSPACE", Path.cwd())
GAME = _path("EU5_RENDER_GAME_ROOT", DEFAULT_GAME, WORKSPACE)
if GAME.name.lower() != "game" and (GAME / "game").is_dir():
    GAME = GAME / "game"
default_mod = WORKSPACE / "src" / "stable"
if not default_mod.is_dir():
    default_mod = WORKSPACE / "src"
MOD = _path("EU5_RENDER_MOD_ROOT", default_mod, WORKSPACE)
OUTPUT = _path("EU5_RENDER_OUTPUT_ROOT", WORKSPACE / "ai_gui_assessment" / "images", WORKSPACE)
LANGUAGE = os.environ.get("EU5_RENDER_LANGUAGE", "simp_chinese")
