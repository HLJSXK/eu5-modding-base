# Shared EU5 AI Tool Workflow

This is the cross-workspace workflow contract. Read it together with the base
`CLAUDE.md`, the workspace `CLAUDE.md`, both knowledge briefs, and the
task-scoped context output from `scripts/ai_context.py`. In a mounted project,
the base is `.eu5-base`; when working in the base checkout itself, the base is
the current directory.

## Task Context

Before a non-trivial edit, run the direct EU5 interpreter:

```powershell
$env:EU5_PYTHON = '<absolute path to the eu5 environment python.exe>'
& $env:EU5_PYTHON scripts\ai_context.py --changed
# or: scripts\ai_context.py --files <paths>
```

The context command merges the base and workspace anti-pattern registries,
route tables, required reads, risk cards, and generated-file ownership. Read
every required card and immediate alert it reports.

## EU5 Resolution Rule

EU5 uses Jomini; do not assume EU4 syntax. For uncertain syntax, consult these
sources in order:

1. `<base>/reference_official_defines/`
2. `<base>/reference_game_files/`
3. `<base>/reference_mods/`

Use `<base> = .eu5-base` in a mounted workspace and `<base> = .` in the base
checkout.

The mandatory-reference categories are `blockoverride`, `custom_tooltip`,
`situation_card_common` / `card_common`, `location_rank:*`, modifier names,
undeclared scripted triggers/effects, localization encoding, GUI expressions,
variable-map APIs, and GUI icon display. Preserve a feature while correcting
its syntax; do not remove it because a guessed expression failed.

## GUI and Generated Files

Read `<base>/docs/guides/EU5_GUI_Modding_Guide.md` before GUI work. Resolve
types with the shared renderer's `guidef.py` and render a representative state
with `run.py` when the change affects layout or bindings. Check
`font_icons.gui` before creating an icon widget; use inline `@icon_name!` text
icons when the engine already provides one. Check `data/generated_files.yaml`
before editing generated project outputs and edit their data source or
generator instead.

## Knowledge Maintenance

When a verified source or runtime error reveals a reusable rule, add it to the
shared anti-pattern registry with provenance, update the shared workflow guide
or GUI guide as appropriate, regenerate the shared brief, and run the base and
workspace knowledge tests. Rules that depend on a project's solver, wonder,
international organization, victory, or GUI implementation belong in that
workspace's local registry and risk cards.

Use the direct EU5 interpreter for validation. Do not use `conda run` in managed
sandboxes. Run the workspace validator and routing tests after workflow or
knowledge changes.
