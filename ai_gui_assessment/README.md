# EU5 GUI Renderer and Research Core

`renderer/` contains the reusable parser, type/template expander, data-binding
evaluator, layout engine, text renderer, and texture compositor. It reads the
installed game and a selected mod root; it includes a generic vanilla HUD scenario, but no project-specific
scenarios, screenshots, or generated output. Install `Pillow` and `NumPy` from
`ai_gui_assessment/renderer/requirements.txt` in the selected Python environment.

The command-line tools accept `--workspace`, `--mod-root`, `--game-root`, and
`--output-root` so a fresh agent can use the same renderer from any workspace.
Use `guidef.py` to print a resolved type/template and `run.py` for a generic
mock-backed root/type/template render.

The [shared GUI guide](../docs/guides/EU5_GUI_Modding_Guide.md) records verified
EU5 GUI rules. Project-specific research notebooks, screenshot comparisons,
and scenario fixtures stay in the calling mod repository.

Use run.py --scenario hud for the full in-game HUD with sample data.
Run parser regressions: python -m unittest discover -s ai_gui_assessment/renderer/tests

With `--gui-file`, a matching concrete root in that file takes precedence over
a registered type with the same name. This retains panel-specific overrides.
`using` accepts inherited types as well as templates. Concept images and font
icons are loaded from the selected mod, with matching files overriding vanilla.

For a widget with `textcontext` and `ontextcontextchanged`, a scenario can mock
the expression with a typed context dictionary, using the same `__type__` and
accessor keys as ordinary datacontext mocks. For example, a `StringPairList`
contains `GetRows` (a list of `StringViewPair` contexts), `GetFooter`, and title
accessors. This context is scoped to that table and its descendants. The renderer
does not parse arbitrary native effect-description strings; unconverted contexts
are listed in `unsupported_textcontexts` in the JSON report. Scenario-authored
effect text and table values must be identified as sample data.

## Scenario integration and ownership

The shared package owns configuration (`config.configure_paths`), resource loading
and PNG/tree/report output (`preview.load_resources`, `preview.render_tree`),
strict diagnostic checks (`preview.has_diagnostics`), root selection
(`gui.build_target`), and native mock/table serialization (`fixtures`). The generic
`run.py --strict` uses that same pipeline. Batch callers load one `RenderResources`
instance and pass a fresh expanded tree for each render. Texture misses are
recorded independently for every image, including cached failures.

Localization diagnostics track missing literal text keys, `$key$` substitutions,
`Localize`, `SelectLocalization`, and selected game-concept keys without relying
on a project's naming prefix. Conditional `modify_texture.visible` layers are
resolved before composing or loading their textures.

Mod repositories own their GUI selection, tabs, lifecycle presets, variable names,
fictional values, action availability rules, fixture schemas and sample effect
descriptions. Pass those as mocks/metadata to the shared API; do not import a mod
or add a mod's scenario registry to this package. Test generic behavior here with
synthetic GUI fixtures; test a mod's visible branches in that mod's repository.
