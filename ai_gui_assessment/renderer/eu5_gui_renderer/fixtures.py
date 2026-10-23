"""Reusable mock bindings and native text-table context shapes.

Calling projects own variable names, values, table text and action rules.
These helpers only serialize that explicit sample data for the renderer.
"""
from __future__ import annotations

import json
from pathlib import Path
import re


def load_mocks(path: Path) -> list:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    pairs = payload.get("mocks") if isinstance(payload, dict) else payload
    if not isinstance(pairs, list) or any(
        not isinstance(pair, list) or len(pair) != 2 or not isinstance(pair[0], str)
        for pair in pairs
    ):
        raise ValueError("Mocks must be a list of [expression regex, value] pairs")
    for pattern, _ in pairs:
        re.compile(pattern)
    return pairs


def variable_mocks(prefix: str, values: dict) -> list:
    """Zero/False are set values; None is an absent variable in this scope."""
    result = []
    for name, value in values.items():
        accessor = f"{prefix}.GetVariable('{name}')"
        result.extend([
            (re.escape(accessor + ".IsSet"), value is not None),
            (re.escape(accessor + ".GetValue"), 0 if value is None else value),
        ])
    return result


def object_mocks(expression: str, context: dict) -> list:
    """Bind an explicit typed context and its fully qualified accessors."""
    return [(re.escape(expression), context)] + [
        (re.escape(expression + "." + key), value)
        for key, value in context.items() if key != "__type__"
    ]


def modifier_sample_lines(values: dict, metadata: dict, loc) -> list[str]:
    """Format explicit sample modifiers using caller-owned index metadata.

    This does not evaluate effects or load any project's modifier index.
    Localization is taken from the selected renderer resources.
    """
    lines = []
    for key, value in values.items():
        label = loc.get(f"MODIFIER_TYPE_NAME_{key}") or key
        number = f"{value * 100:+g}%" if metadata[key]["value_kind"] == "percent" else f"{value:+g}"
        lines.append(f"{label}: {number}")
    return lines


def set_action_availability(element, availability: dict[str, bool]) -> None:
    """Attach supplied availability to concrete scripted-action buttons."""
    action = element.props.get("scripted_action_tooltip", {}).get("action_name")
    if action in availability:
        element.ctx_item = {**getattr(element, "ctx_item", {}),
                            "PdxGuiWidget.IsUberButtonEnabled": availability[action]}
    for child in element.children:
        set_action_availability(child, availability)


def string_pair_list(rows: list[tuple[str, str]]) -> dict:
    return {"__type__": "StringPairList", "GetRows": [
        {"__type__": "StringViewPair", "GetLeft.GetStringView": left,
         "GetLeft.IsStringViewNotEmptyOrNull": bool(left), "GetRight.GetStringView": right,
         "GetRight.IsStringViewNotEmptyOrNull": bool(right), "GetIndent": 0}
        for left, right in rows
    ], "GetFooter": [], "GetTitle.IsStringViewNotEmptyOrNull": False,
        "GetTitle.GetStringView": ""}


def requirements_list(rows: list[tuple[str, bool | None]]) -> dict:
    """RequirementsList shape from the vanilla main_menu_cooltip_types GUI."""
    return {"__type__": "RequirementsList", "GetLines": [
        {"__type__": "RequirementLine", "Self": str(index), "GetText": text,
         "GetIndent": 0, "HasPassed": passed is True, "HasFailed": passed is False,
         "IsUndefined": passed is None, "IsSkipped": False, "IsBlocker": False}
        for index, (text, passed) in enumerate(rows)
    ], "GetTitle.IsStringViewNotEmptyOrNull": False, "GetTitle.GetStringView": ""}
