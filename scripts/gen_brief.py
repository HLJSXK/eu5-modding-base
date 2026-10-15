#!/usr/bin/env python3
"""Generate the shared EU5 knowledge brief."""
from datetime import date
from pathlib import Path
import sys
import yaml
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE = ROOT / "docs" / "knowledge"
def main():
    rules = yaml.safe_load((KNOWLEDGE / "anti_patterns.yaml").read_text(encoding="utf-8")) or []
    enums = yaml.safe_load((KNOWLEDGE / "valid_enums.yaml").read_text(encoding="utf-8")) or {}
    lines = ["# EU5 Shared Knowledge Brief", "", "> Generated from this base checkout. Do not edit directly.", f"> Last updated: {date.today()}", "", "## Startup", "", "- Read this base's `CLAUDE.md` plus the project workspace's `CLAUDE.md`.", "- Read this brief and the workspace's own `docs/knowledge/BRIEF.md`.", "- Consult `.eu5-base/reference_official_defines/`, `.eu5-base/reference_game_files/`, and the workspace-appropriate community snapshot.", "- For GUI work, read `.eu5-base/docs/guides/EU5_GUI_Modding_Guide.md`; the renderer accepts explicit workspace and game paths.", "", "## Shared resources", "", "- `reference_game_files/`: one filtered 1.4 text mirror; source snapshots/logs are recorded in `migration/`.", "- `reference_official_defines/`: official type and script definitions.", "- `reference_mods/`: complete SOL-source snapshot.", "- `reference_mods_variants/eu5-towards-victory/`: complete TV-source snapshot, retained to preserve divergent same-path files.", "- `vanilla_error_filters.txt`: additive union of both vanilla log baselines; exact sources and rule origins are under `migration/`.", "", "## Shared enums", "", "| Enum | Values | Source |", "| --- | --- | --- |"]
    for key, item in enums.items():
        lines.append(f"| `{key}` | {', '.join(item.get('values', []))} | {item.get('source', '')} |")
    lines.extend(["", "## Shared anti-patterns", "", f"The shared registry contains **{len(rules)}** reusable rules. Load the workspace registry cumulatively; do not shadow a shared ID.", "", "| ID | Category | Scope |", "| --- | --- | --- |"])
    for item in rules:
        lines.append(f"| `{item.get('id', '')}` | {item.get('category', '')} | {item.get('scope', '')} |")
    (KNOWLEDGE / "BRIEF.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[OK] generated {KNOWLEDGE / 'BRIEF.md'} ({len(rules)} rules, {len(enums)} enums)")
if __name__ == "__main__": main()
