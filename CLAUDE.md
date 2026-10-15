# EU5 Modding Base — Shared Agent Instructions

This file is the shared workflow contract for EU5 workspaces mounted through `.eu5-base`.

When this repository itself is the current workspace, read the paths in this
file relative to the repository root: `.eu5-base/` means `.`. When a mod
workspace mounts this repository, use its `.eu5-base/` junction as written.

## Startup

1. Read this file.
2. Read the workspace root `CLAUDE.md` and any workspace `AGENTS.md`.
3. Read `.eu5-base/docs/knowledge/BRIEF.md`, then the workspace `docs/knowledge/BRIEF.md`.
4. For GUI work, read `.eu5-base/docs/guides/EU5_GUI_Modding_Guide.md` and the workspace GUI supplement, if present.
5. For gameplay design, read `.eu5-base/docs/knowledge/EU5_Gameplay_Reference.md`; keep workspace-specific application notes separate.
6. Before a non-trivial edit, run the workspace context builder. It must merge base routes/cards/rules with local routes/cards/rules.
   The shared workflow contract is `docs/guides/AI_Tool_Workflow_Prompt.md`.

If `.eu5-base` is missing, stop and run the workspace `scripts/bootstrap_base.py` (or follow its printed repair command), then restart the startup sequence. Never silently continue with only local knowledge.

## EU5 reference policy

EU5 uses Jomini; do not assume EU4 syntax. For uncertain syntax, consult `.eu5-base/reference_official_defines/`, then `.eu5-base/reference_game_files/`, then `.eu5-base/reference_mods/`. The checked-in source corpus is evidence, not a license to guess. Mandatory-reference categories include block overrides, custom tooltips, GUI templates and expressions, location ranks, modifiers, undeclared scripted triggers/effects, variable maps, localization encoding, and GUI icons.

The current location-rank enum is `rural_settlement`, `town`, `city`, `megalopolis`; verify the corpus when the game version changes. Localization YAML requires UTF-8 BOM and straight ASCII double quotes. Preserve features while fixing syntax; do not remove behavior merely because an expression failed.

## Knowledge ownership

Base files describe reusable engine behavior, reference evidence, and tooling contracts. Workspace files describe that project's source, generated outputs, design decisions, and implementation-specific rules. When a shared rule is discovered, update the base rule and its provenance; when it only depends on a project's solver, wonder, IO, victory, or GUI implementation, keep it local. Do not copy one project's strategy into another project's startup context.

After changing shared knowledge or workflow files, regenerate `.eu5-base/docs/knowledge/BRIEF.md` and run the base and workspace knowledge tests. Keep `docs/knowledge/MIGRATION_COVERAGE.yaml` complete when moving entries.
