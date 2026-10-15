"""Load shared base knowledge together with one workspace's local additions."""
from __future__ import annotations

from pathlib import Path
from typing import Any
import os
import yaml


def base_root(workspace: Path) -> Path:
    root = Path(workspace).resolve()
    configured = os.environ.get("EU5_MODDING_BASE")
    if configured:
        candidate = Path(configured).expanduser().resolve()
        if (candidate / "docs/knowledge/anti_patterns.yaml").is_file():
            return candidate
    if (root / "reference_game_files" / "game").is_dir() and (root / "docs/knowledge/anti_patterns.yaml").is_file():
        return root
    link = root / ".eu5-base"
    required = link / "docs/knowledge/anti_patterns.yaml"
    if not required.is_file():
        module_root = Path(__file__).resolve().parents[1]
        if (module_root / "docs/knowledge/anti_patterns.yaml").is_file():
            return module_root
        sibling = root.parent / "eu5-modding-base"
        if (sibling / "docs/knowledge/anti_patterns.yaml").is_file():
            return sibling.resolve()
        raise FileNotFoundError(f"Missing shared EU5 knowledge at {required}; run scripts/bootstrap_base.py or set EU5_MODDING_BASE")
    return link.resolve()


def read_yaml(path: Path) -> Any:
    if not path.is_file():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def knowledge_files(workspace: Path, filename: str) -> tuple[Path, Path]:
    root = Path(workspace).resolve()
    shared_root = base_root(root)
    if shared_root == root:
        return shared_root / "docs/knowledge" / filename, root / "docs/knowledge" / "__no_local__"
    return shared_root / "docs/knowledge" / filename, root / "docs/knowledge" / filename


def load_anti_patterns(workspace: Path) -> list[dict[str, Any]]:
    shared, local = knowledge_files(workspace, "anti_patterns.yaml")
    merged: list[dict[str, Any]] = []
    seen: dict[str, tuple[dict[str, Any], Path]] = {}
    for source in (shared, local):
        for entry in read_yaml(source) or []:
            if not isinstance(entry, dict) or not entry.get("id"):
                raise ValueError(f"Anti-pattern without id in {source}")
            ident = str(entry["id"])
            if ident in seen:
                previous, previous_file = seen[ident]
                if previous != entry:
                    raise ValueError(f"Conflicting anti-pattern {ident} in {previous_file} and {source}")
                continue
            seen[ident] = (entry, source)
            merged.append(entry)
    return merged


def load_valid_enums(workspace: Path) -> dict[str, Any]:
    shared, local = knowledge_files(workspace, "valid_enums.yaml")
    merged: dict[str, Any] = {}
    for source in (shared, local):
        for key, value in (read_yaml(source) or {}).items():
            if key in merged and merged[key] != value:
                raise ValueError(f"Conflicting enum {key} in {source}")
            merged[key] = value
    return merged


def load_context_routes(workspace: Path) -> dict[str, Any]:
    root = Path(workspace).resolve()
    shared_root = base_root(root)
    shared_path = shared_root / "docs/knowledge/context_routes.yaml"
    local_path = root / "docs/knowledge/context_routes.yaml" if shared_root != root else Path("__no_local__")
    shared = read_yaml(shared_path) or {}
    local = read_yaml(local_path) or {}
    result: dict[str, Any] = {"mod_roots": local.get("mod_roots") or shared.get("mod_roots") or ["src"]}
    for key in ("core_reads", "domain_routes", "filename_routes", "content_routes", "object_alerts", "maintenance_routes"):
        rows: list[dict[str, Any]] = []
        seen: set[tuple[str, str]] = set()
        for origin, config in (("base", shared), ("local", local)):
            for row in config.get(key, []) or []:
                row = dict(row)
                ident = str(row.get("id") or row.get("path") or "")
                if not ident:
                    raise ValueError(f"Route without id/path in {key}")
                row["_origin"] = origin
                comparable = dict(row)
                comparable.pop("_origin", None)
                signature = (ident, repr(sorted(comparable.items())))
                if signature in seen:
                    continue
                seen.add(signature)
                rows.append(row)
        result[key] = rows
    return result


def risk_card_path(workspace: Path, filename: str, origin: str = "base") -> str:
    root = Path(workspace).resolve()
    base = base_root(root) / "docs/knowledge/risk_cards" / filename
    local = root / "docs/knowledge/risk_cards" / filename
    if origin == "base" and base.is_file() and base_root(root) == root:
        return f"docs/knowledge/risk_cards/{filename}"
    if origin == "base" and base.is_file():
        return f".eu5-base/docs/knowledge/risk_cards/{filename}"
    if origin == "local" and local.is_file():
        return f"docs/knowledge/risk_cards/{filename}"
    raise FileNotFoundError(filename)


def validate_migration_coverage(workspace: Path) -> dict[str, int]:
    root = Path(workspace).resolve()
    manifest = read_yaml(base_root(root) / "docs/knowledge/MIGRATION_COVERAGE.yaml") or {}
    shared_rows = read_yaml(base_root(root) / "docs/knowledge/anti_patterns.yaml") or []
    local_rows = read_yaml(root / "docs/knowledge/anti_patterns.yaml") or [] if base_root(root) != root else []
    shared_ids = {x.get("id") for x in shared_rows}
    local_ids = {x.get("id") for x in local_rows}
    if len(shared_ids) != len(shared_rows):
        raise ValueError("Duplicate IDs in shared anti-pattern registry")
    if len(local_ids) != len(local_rows):
        raise ValueError(f"Duplicate IDs in workspace anti-pattern registry: {root.name}")
    overlap = shared_ids & local_ids
    if overlap:
        raise ValueError(f"Workspace shadows shared anti-pattern IDs: {sorted(overlap)[:8]}")
    entries = [x for x in manifest.get("entries", []) if x.get("source_project") == root.name]
    missing = [x["id"] for x in entries if x["id"] not in (shared_ids if x.get("destination") == "base" else local_ids)]
    if missing:
        raise ValueError(f"Missing migrated anti-patterns for {root.name}: {missing[:8]}")
    invalid_destinations = [x["id"] for x in entries if x.get("destination") not in {"base", "local"}]
    if invalid_destinations:
        raise ValueError(f"Invalid migration destinations for {root.name}: {invalid_destinations[:8]}")
    return {"source_entries": len(entries), "base_entries": len(shared_ids), "local_entries": len(local_ids), "merged_entries": len(shared_ids | local_ids)}
