# EU5 Modding Base

`eu5-modding-base` is the shared EU5 modding knowledge and tooling project. It contains the filtered game/reference corpus, official definitions, community reference mods, reusable workflow rules, GUI guidance, gameplay evidence, risk cards, and knowledge loaders consumed by workspace projects.

Workspace projects mount this repository as `.eu5-base`. An AI agent must load both `.eu5-base/CLAUDE.md` (shared rules) and the workspace `CLAUDE.md` (project rules), then use the workspace context command so shared and local knowledge are combined. Project-specific implementation rules, generated indexes, source code, scenarios, and design notes remain in the workspace.

The base corpus is authoritative for shared engine syntax and reference paths. Check `migration/` manifests when a source conflict or provenance question arises. Regenerate shared knowledge with the direct EU5 interpreter after changing base knowledge files.
