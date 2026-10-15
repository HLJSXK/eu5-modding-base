"""Move implementation-specific migrated rules back to workspace registries.

This is an idempotent migration maintenance command. It preserves each full
entry and updates MIGRATION_COVERAGE.yaml so the source and destination remain
auditable.
"""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
MOVED = {
    "eu5-modding-project": {
        "resolution_message_database_uses_fixed_path",
        "gui_standalone_target_missing_shared_types",
        "country_pulse_manual_on_action_merge_unnecessary",
        "situation_custom_mapmode_visibility_states",
        "goods_upper_group_includes_workers_1_3_11",
        "local_effect_min_is_not_value_floor",
    },
    "eu5-towards-victory": {
        "event_option_effect_block_unknown_effect",
        "generic_action_effect_reads_newly_set_variable",
        "variable_map_rebuild_on_read_path",
        "country_trigger_reused_inside_io_monthly_change",
        "card_common_list_missing_fixed_vertical_size_overlaps_in_vbox",
        "card_common_shrinking_height_chain_broken_by_one_fixed_height_wrapper",
        "card_common_text_wrapped_in_expanding_widget_blows_out_fixed_card",
        "card_common_untitled_card_missing_common_header_blockoverride",
        "gui_generator_rewrite_silently_dropped_generic_wonder_confirm_buttons",
        "cmm_mod_id_too_long_breaks_menu_visibility",
    },
}
PROMOTE_TO_BASE = {
    "managed_sandbox_conda_run_hang",
    "same_id_database_override_missing_replace_prefix",
    "replace_prefix_requires_guaranteed_base_entry",
    "artist_selector_should_use_artist_column",
    "mod_io_geticon_without_matching_texture",
    "engineering_building_loc_used_as_game_concept",
    "noncapital_building_country_effects_via_capital_country_modifier",
    "generated_static_modifier_key_flood_hash_collision_risk",
    "monthly_country_pulse_callback_missing_participation_gate",
    "io_non_unique_scope_link",
    "io_link_invalid_same_tick_creation",
    "io_has_leader_invalid_gui_function",
    "io_limit_leader_country_non_optional",
    "io_trigger_iterator_limit_invalid",
    "io_any_member_of_not_effect_iterator",
    "io_typed_variable_update_in_on_action",
    "io_monthly_change_signed_contribution_inside_named_add",
    "io_scoped_effect_called_inside_create_io_block",
    "io_policy_execution_scope_recipient_unset",
    "io_policy_activation_direct_leader_country",
    "io_policy_ai_math_scope_recipient_requires_exists",
    "io_policy_member_modifier_utility_unfiltered",
    "io_policy_leader_country_modifier_unguarded_recipient_tooltip",
    "io_single_member_parliament_without_leader_special_status",
    "io_parliament_issue_without_special_status_agenda",
    "io_law_vote_without_special_status_power",
    "io_law_vote_without_parliament_location",
    "io_special_status_auto_bestow_without_lifecycle_sync",
    "io_special_status_missing_parliament_modifier_types",
    "io_header_controls_in_country_header_extra",
    "io_character_card_sort_highlight_without_filtered_list",
    "io_custom_tab_scrollarea_autosize_wrapper_misaligns",
    "io_idle_parliament_issue_nonpositive_wants_bias",
    "io_law_category_missing_uppercase_loc",
}


def load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8")) or []


def dump(path: Path, header: str, value) -> None:
    path.write_text(header + yaml.safe_dump(value, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")


def main() -> None:
    base_path = ROOT / "docs/knowledge/anti_patterns.yaml"
    base = load(base_path)
    by_id = {row["id"]: row for row in base}
    manifest_path = ROOT / "docs/knowledge/MIGRATION_COVERAGE.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    local = {project: load(ROOT.parent / project / "docs/knowledge/anti_patterns.yaml") for project in MOVED}
    local["eu5-towards-victory"] = load(ROOT.parent / "eu5-towards-victory" / "docs/knowledge/anti_patterns.yaml")
    moved = set().union(*MOVED.values())
    source_rows = {(row.get("source_project"), row.get("id")): row.get("entry") for row in manifest.get("entries", [])}
    local_ids = {project: {row["id"] for row in rows} for project, rows in local.items()}
    missing = sorted(ident for project, ids in MOVED.items() for ident in ids if ident not in by_id and ident not in local_ids[project] and not source_rows.get((project, ident)))
    if missing:
        raise SystemExit(f"Entries are absent from both registries and migration source: {missing}")
    for project, ids in MOVED.items():
        for ident in sorted(ids):
            if ident in local_ids[project]:
                continue
            entry = by_id.get(ident) or source_rows.get((project, ident))
            if entry is not None:
                local[project].append(entry)
    tv_by_id = {row["id"]: row for row in local["eu5-towards-victory"]}
    missing_promotions = sorted(PROMOTE_TO_BASE - set(tv_by_id) - set(by_id))
    if missing_promotions:
        raise SystemExit(f"Entries are not in shared or TV local registry: {missing_promotions}")
    base.extend(tv_by_id[ident] for ident in sorted(PROMOTE_TO_BASE) if ident not in by_id and ident in tv_by_id)
    local["eu5-towards-victory"] = [row for row in local["eu5-towards-victory"] if row["id"] not in PROMOTE_TO_BASE]
    base = sorted((row for row in base if row["id"] not in moved), key=lambda row: row["id"])
    for project in local:
        local[project] = sorted(local[project], key=lambda row: row["id"])
    dump(base_path, "# Reusable EU5 engine/tooling anti-patterns. Project-specific rules stay in each workspace.\n", base)
    for project, rows in local.items():
        dump(ROOT.parent / project / "docs/knowledge/anti_patterns.yaml", f"# {project} project-specific anti-patterns; reusable entries are loaded from .eu5-base/docs/knowledge/anti_patterns.yaml.\n", rows)

    for row in manifest.get("entries", []):
        project = row.get("source_project")
        if project in MOVED and row.get("id") in MOVED[project]:
            row["destination"] = "local"
            row["destination_path"] = "docs/knowledge/anti_patterns.yaml"
        if project == "eu5-towards-victory" and row.get("id") in PROMOTE_TO_BASE:
            row["destination"] = "base"
            row["destination_path"] = ".eu5-base/docs/knowledge/anti_patterns.yaml"
    dump(manifest_path, "", manifest)
    print(f"[OK] reclassified {len(moved)} implementation-specific entries")


if __name__ == "__main__":
    main()
