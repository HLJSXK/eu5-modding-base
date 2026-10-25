# EU5 Modding Base

`eu5-modding-base` is the shared EU5 modding knowledge and tooling project. It contains the filtered game/reference corpus, official definitions, community reference mods, reusable workflow rules, GUI guidance, gameplay evidence, risk cards, and knowledge loaders consumed by workspace projects.

Workspace projects mount this repository as `.eu5-base`. An AI agent must load both `.eu5-base/CLAUDE.md` (shared rules) and the workspace `CLAUDE.md` (project rules), then use the workspace context command so shared and local knowledge are combined. Project-specific implementation rules, generated indexes, source code, scenarios, and design notes remain in the workspace.

The base corpus is authoritative for shared engine syntax and reference paths. Check `migration/` manifests when a source conflict or provenance question arises. Regenerate shared knowledge with the direct EU5 interpreter after changing base knowledge files.

## Shared tools

- [`scripts/update_workshop_tags.py`](scripts/update_workshop_tags.py) updates only the category tags of an existing EU5 Workshop item. Pass both `--item-id` and `--metadata`; the default is an offline preview, `--check` reads Steam, and `--apply` submits and verifies the tags. It uses the installed Windows Steam DLL without extra packages or API keys. See [Workshop tag instructions](docs/guides/Workshop_Tags.md).
- Run its offline regressions with `& $env:EU5_PYTHON scripts/test_update_workshop_tags.py` from this checkout. Workspaces may retain thin launchers with their own metadata defaults; implementation and shared tests belong here.
