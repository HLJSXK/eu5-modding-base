# EU5 GUI Renderer and Research Core

`renderer/` contains the reusable parser, type/template expander, data-binding
evaluator, layout engine, text renderer, and texture compositor. It reads the
installed game and a selected mod root; it does not contain any project's
scenarios, screenshots, or generated output. Install `Pillow` and `NumPy` from
`ai_gui_assessment/renderer/requirements.txt` in the selected Python environment.

The command-line tools accept `--workspace`, `--mod-root`, `--game-root`, and
`--output-root` so a fresh agent can use the same renderer from any workspace.
Use `guidef.py` to print a resolved type/template and `run.py` for a generic
mock-backed root/type/template render.

The [shared GUI guide](../docs/guides/EU5_GUI_Modding_Guide.md) records verified
EU5 GUI rules. Project-specific research notebooks, screenshot comparisons,
and scenario fixtures stay in the calling mod repository.
