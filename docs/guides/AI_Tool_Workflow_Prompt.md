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

## Required generic-action registration checks

Before action edits, run context for the action, generator or registered data.
The default Markdown and JSON include the untruncated `generic_action_registration`
required alert: AI-list `actions` membership, a message type owned by this mod root,
and all five `HEADER/TITLE/SETUP/LOG/MAP` localization fields. Read the generic-action
risk card and regenerate owned outputs; validate before handoff. The reminder is
independent of the capped advisory anti-pattern list and does not need `--full`.
Path-only routes also work before a proposed action or generator file exists.

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
## Verified GUI findings (2026-10-24)

| Date | Pitfall | Verified behavior |
| --- | --- | --- |
| 2026-10-24 | Generic estate hover or population substituted for government estate existence | Bind GetEstateFromKey to the label and use Estate_tooltip; gate the row with ExistsForCountry (ambrosian_republic_disaster.gui:51-53; shared/cards.gui:3908). Guard ownerless location entry buttons with Location.HasOwner. |
| 2026-10-24 | Guessing a goods accessor for a known static key | ShowGoodsName('key') is a global CString helper, used by vanilla buildings localization; it does not imply GetVariable(...).GetGoods support. |
| 2026-10-24 | Template nested directly inside a types/Types group | Emit templates at file scope; the engine rejects this nesting. The shared parser now reports the declaration line (main_menu_cooltip_types.gui:6-27; runtime log gui/SOL_lshud_glorp_compat.gui:6-34). |
