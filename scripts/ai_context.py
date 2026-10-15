#!/usr/bin/env python3
"""Build task-scoped context from shared and workspace-local EU5 knowledge."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml
except ImportError:
    raise SystemExit("[ERROR] PyYAML is required")

BASE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_ROOT / "scripts"))
from knowledge_loader import base_root, load_anti_patterns, load_context_routes  # noqa: E402

REPO_ROOT = Path(os.environ.get("EU5_WORKSPACE_ROOT", Path.cwd())).expanduser().resolve()


def configure_workspace(path: Path | None) -> None:
    global REPO_ROOT
    if path is not None:
        REPO_ROOT = path.expanduser().resolve()


def _norm(path: str) -> str:
    return str(path).replace("\\", "/").strip()


def _load_yaml(path: Path) -> Any:
    if not path.is_file():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def changed_files() -> list[str]:
    names: set[str] = set()
    for args in (("diff", "--name-only", "HEAD"), ("diff", "--name-only", "--cached"), ("ls-files", "--others", "--exclude-standard")):
        result = subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if result.returncode == 0:
            names.update(line.strip() for line in result.stdout.splitlines() if line.strip())
    return sorted(names)


def _generated_map() -> dict[str, dict[str, Any]]:
    registry = _load_yaml(REPO_ROOT / "data" / "generated_files.yaml") or {}
    return {_norm(item["output"]): item for item in registry.get("generated", []) if item.get("output")}


def _generated_sources(entry: dict[str, Any] | None) -> list[str]:
    if not entry:
        return []
    paths = [_norm(entry["script"])] if entry.get("script") else []
    if entry.get("data"):
        paths.extend(_norm(part) for part in str(entry["data"]).split("+") if part.strip() and "*" not in part)
    return paths


def _path_matches(path: str, route: dict[str, Any], routes: dict[str, Any]) -> bool:
    normalized = _norm(path)
    prefixes = [_norm(p) for p in route.get("path_prefixes", []) or []]
    if route.get("expand_mod_roots"):
        prefixes.extend(f"{root.rstrip('/')}/{prefix.lstrip('/')}" for root in routes.get("mod_roots", []) for prefix in route.get("path_prefixes", []) or [])
    prefix_ok = not prefixes or any(normalized.startswith(prefix) for prefix in prefixes)
    name = Path(normalized).name.lower()
    substrings = route.get("substrings", route.get("filename_substrings", [])) or []
    name_ok = not substrings or any(str(value).lower() in name for value in substrings)
    suffix_ok = not route.get("file_suffixes") or any(normalized.lower().endswith(str(value).lower()) for value in route["file_suffixes"])
    return prefix_ok and name_ok and suffix_ok


def _content_excluded(path: str, route: dict[str, Any]) -> bool:
    normalized = _norm(path)
    return normalized in {_norm(p) for p in route.get("excluded_paths", []) or []} or any(normalized.startswith(_norm(p)) for p in route.get("excluded_prefixes", []) or [])


def _contains(path: str, markers: list[str]) -> bool:
    target = REPO_ROOT / path
    if not target.is_file():
        return False
    try:
        content = target.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return any(marker in content for marker in markers)


def _card_path(route: dict[str, Any]) -> str:
    filename = str(route.get("card", ""))
    if not filename:
        return ""
    common = BASE_ROOT / "docs/knowledge/risk_cards" / filename
    local = REPO_ROOT / "docs/knowledge/risk_cards" / filename
    if route.get("_origin") == "base" and common.is_file():
        return f"docs/knowledge/risk_cards/{filename}" if REPO_ROOT == BASE_ROOT else f".eu5-base/docs/knowledge/risk_cards/{filename}"
    if local.is_file():
        return f"docs/knowledge/risk_cards/{filename}"
    if common.is_file():
        return f"docs/knowledge/risk_cards/{filename}" if REPO_ROOT == BASE_ROOT else f".eu5-base/docs/knowledge/risk_cards/{filename}"
    return ""


def _add_card(cards: dict[str, dict[str, str]], route: dict[str, Any], domain: str) -> None:
    path = _card_path(route)
    if path:
        cards[path] = {"path": path, "domain": domain, "reason": str(route.get("reason", "")), "summary": str(route.get("summary", ""))}


def build_context(files: list[str]) -> dict[str, Any]:
    shared_root = base_root(REPO_ROOT)
    routes = load_context_routes(REPO_ROOT)
    files = sorted({_norm(path) for path in files if path})
    generated = _generated_map()
    routed = {path: sorted({path, *_generated_sources(generated.get(path))}) for path in files}
    domains: dict[str, dict[str, str]] = {}
    cards: dict[str, dict[str, str]] = {}
    reads: dict[str, str] = {}
    alerts: dict[str, dict[str, str]] = {}
    for route in routes.get("core_reads", []):
        read_path = str(route.get("path", ""))
        if shared_root == REPO_ROOT and read_path.startswith(".eu5-base/"):
            read_path = read_path[len(".eu5-base/"):]
        if read_path:
            reads[read_path] = str(route.get("reason", ""))
    for original, candidates in routed.items():
        for path in candidates:
            for route in routes.get("domain_routes", []) + routes.get("filename_routes", []):
                if _path_matches(path, route, routes):
                    domain = str(route.get("id", ""))
                    domains[domain] = {"id": domain, "reason": str(route.get("reason", ""))}
                    _add_card(cards, route, domain)
            for route in routes.get("content_routes", []):
                if _content_excluded(path, route) or not _contains(path, [str(m) for m in route.get("markers", []) or []]):
                    continue
                domain = str(route.get("id", ""))
                domains[domain] = {"id": domain, "reason": str(route.get("reason", ""))}
                for read in route.get("reads", []) or []:
                    reads[str(read.get("path", ""))] = str(read.get("reason", ""))
                _add_card(cards, route, domain)
            for route in routes.get("object_alerts", []):
                if _content_excluded(path, route) or not _path_matches(path, route, routes) or not _contains(path, [str(m) for m in route.get("markers", []) or []]):
                    continue
                domain = str(route.get("id", ""))
                card = _card_path(route)
                alerts[domain] = {"id": domain, "severity": str(route.get("severity", "high")), "path": original, "source": path, "message": str(route.get("message", "")), "card": card}
                domains[domain] = {"id": domain, "reason": str(route.get("reason", route.get("message", "")))}
                _add_card(cards, route, domain)
            for route in routes.get("maintenance_routes", []):
                if _path_matches(path, route, routes):
                    domain = str(route.get("id", ""))
                    domains[domain] = {"id": domain, "reason": str(route.get("reason", ""))}
                    for read in route.get("reads", []) or []:
                        reads[str(read.get("path", ""))] = str(read.get("reason", ""))

    patterns = load_anti_patterns(REPO_ROOT)
    matched = []
    for item in patterns:
        only_in = [str(part).lower() for part in item.get("only_in_paths", []) or []]
        path_match = bool(only_in) and any(any(part in path.lower() for part in only_in) for path in files)
        domain_match = item.get("category") in domains or item.get("scope") in domains
        if path_match or domain_match:
            row = {"id": item.get("id", ""), "detectability": item.get("detectability") or ("lint" if item.get("pattern") else "advisory"), "bad": item.get("bad", ""), "correction": item.get("correction", "")}
            matched.append((0 if path_match else 1, row))
    matched.sort(key=lambda value: (value[0], value[1]["id"]))
    if shared_root == REPO_ROOT:
        reads = {path[len(".eu5-base/"):] if path.startswith(".eu5-base/") else path: reason for path, reason in reads.items()}
    common_rules = _load_yaml(shared_root / "docs/knowledge/anti_patterns.yaml") or []
    local_rules = _load_yaml(REPO_ROOT / "docs/knowledge/anti_patterns.yaml") or [] if REPO_ROOT != shared_root else []
    return {"workspace": str(REPO_ROOT), "base": str(shared_root), "files": files, "generated": {path: generated[path] for path in files if path in generated}, "routed_paths": routed, "domains": sorted(domains.values(), key=lambda row: row["id"]), "cards": sorted(cards.values(), key=lambda row: row["path"]), "reads": [{"path": path, "reason": reason} for path, reason in reads.items()], "alerts": sorted(alerts.values(), key=lambda row: row["id"]), "anti_patterns": [row for _, row in matched[:20]], "relevant_anti_patterns_total": len(matched), "counts": {"shared_anti_patterns": len(common_rules), "workspace_anti_patterns": len(local_rules), "merged_anti_patterns": len(patterns)}}


def _short(value: Any, limit: int = 220) -> str:
    text = " ".join(str(value or "").split())
    return text if len(text) <= limit else text[:limit - 3].rstrip() + "..."


def print_markdown(context: dict[str, Any], full: bool = False) -> None:
    print("# AI Task Context\n")
    print(f"Workspace: `{context['workspace']}`\nBase: `{context['base']}`\n")
    print("## Core Bootstrap\n- Read base and workspace `CLAUDE.md` / `AGENTS.md` files and both knowledge briefs.")
    print("- Shared and local anti-patterns, routes, and risk cards are loaded cumulatively.\n")
    print("## Files\n" + ("\n".join(f"- `{path}`" for path in context["files"]) or "- none") + "\n")
    print("## Knowledge Counts\n- Shared: {shared_anti_patterns}\n- Workspace: {workspace_anti_patterns}\n- Merged: {merged_anti_patterns}\n".format(**context["counts"]))
    for heading, key in (("Immediate Risk Alerts", "alerts"), ("Domains", "domains"), ("Context Routes", "cards"), ("Required Reads", "reads"), ("Relevant Anti-Patterns", "anti_patterns")):
        print(f"## {heading}")
        rows = context[key]
        if not rows:
            print("- none")
        for row in rows:
            if key == "alerts": print(f"- `{row['id']}` [{row['severity']}] {row['message']} Read `{row['card']}`.")
            elif key == "domains": print(f"- `{row['id']}` - {row['reason']}")
            elif key == "cards": print(f"- `{row['path']}` ({row['domain']}) - {row['summary'] or row['reason']}")
            elif key == "reads": print(f"- `{row['path']}` - {row['reason']}")
            else: print(f"- `{row['id']}` [{row['detectability']}] {_short(row['bad'])} -> {_short(row['correction'])}")
        if key == "anti_patterns" and context["relevant_anti_patterns_total"] > len(rows):
            print(f"- {context['relevant_anti_patterns_total'] - len(rows)} additional matches are in the loaded shared/local registries.")
        print()
    if full:
        for card in context["cards"]:
            path = REPO_ROOT / card["path"]
            if not path.is_file() and card["path"].startswith(".eu5-base/"):
                path = BASE_ROOT / card["path"].removeprefix(".eu5-base/")
            if path.is_file():
                print(f"## Risk Card: {card['path']}\n\n{path.read_text(encoding='utf-8').strip()}\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, help="workspace root; defaults to the current directory")
    parser.add_argument("--changed", action="store_true")
    parser.add_argument("--files", nargs="*", default=[])
    parser.add_argument("--full", action="store_true", help="inline full routed risk-card text")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    configure_workspace(args.workspace)
    files = changed_files() if args.changed else args.files
    context = build_context(files)
    if args.json:
        print(json.dumps(context, ensure_ascii=False, indent=2))
    else:
        print_markdown(context, args.full)


if __name__ == "__main__":
    main()
