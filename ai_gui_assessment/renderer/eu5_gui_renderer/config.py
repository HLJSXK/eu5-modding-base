"""Configure render paths before importing asset-dependent renderer modules."""
from __future__ import annotations

import os
from pathlib import Path


def configure_paths(*, workspace: Path | None = None, mod_root: Path | None = None,
                    game_root: Path | None = None, output_root: Path | None = None,
                    language: str = "simp_chinese") -> None:
    root = Path(workspace or os.environ.get("EU5_RENDER_WORKSPACE", Path.cwd())).resolve()
    os.environ["EU5_RENDER_WORKSPACE"] = str(root)
    for name, value in (("EU5_RENDER_MOD_ROOT", mod_root), ("EU5_RENDER_GAME_ROOT", game_root),
                        ("EU5_RENDER_OUTPUT_ROOT", output_root)):
        if value is not None:
            os.environ[name] = str((root / value).resolve())
    os.environ["EU5_RENDER_LANGUAGE"] = language
