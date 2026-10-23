"""Shared preview contracts without an installed game or a project scenario."""
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from eu5_gui_renderer.config import configure_paths
from eu5_gui_renderer.data import Evaluator, Unknown
from eu5_gui_renderer.engine import Engine
from eu5_gui_renderer.fixtures import load_mocks, modifier_sample_lines, object_mocks, requirements_list, set_action_availability, string_pair_list, variable_mocks
from eu5_gui_renderer.gui import Element, Expander, GuiDB
from eu5_gui_renderer.preview import DIAGNOSTIC_KEYS, RenderResources, has_diagnostics, render_tree


class PreviewTests(unittest.TestCase):
    def setUp(self):
        self.loc = type("Loc", (), {"get": lambda _, key: {"EXAMPLE_TITLE": "Title", "EMPTY": ""}.get(key)})()
        self.ev = Evaluator([], self.loc, [])
        self.engine = Engine(None, self.ev, self.loc, None, None, 1)

    def test_missing_localizations_include_dynamic_keys_without_project_prefix(self):
        self.engine.process("UNREGISTERED_TITLE")
        self.engine.process("$UNREGISTERED_REFERENCE$", raw=True)
        self.engine.process("[Localize(Concatenate('UNREGISTERED_', 'BODY'))]", raw=True)
        self.engine.process("[SelectLocalization('(bool)yes', 'UNREGISTERED_CHOICE', 'UNUSED')]", raw=True)
        self.engine.process("[SelectGameConcept('(bool)yes', 'unregistered_concept', 'unused')]", raw=True)
        missing = self.engine.missing_localizations | self.ev.missing_localizations
        self.assertEqual(missing, {"UNREGISTERED_TITLE", "UNREGISTERED_REFERENCE", "UNREGISTERED_BODY",
                                   "UNREGISTERED_CHOICE", "game_concept_unregistered_concept"})
        self.assertEqual(self.ev.fn_Localize("EMPTY"), "")

    def test_scope_bindings_do_not_merge_stores_or_hide_unknowns(self):
        self.ev = Evaluator(variable_mocks("Owner", {"zero": 0, "absent": None}) +
                            variable_mocks("Group", {"zero": 100}), self.loc, [])
        self.assertTrue(self.ev.eval_str("[Owner.GetVariable('zero').IsSet]"))
        self.assertFalse(self.ev.eval_str("[Owner.GetVariable('absent').IsSet]"))
        self.assertEqual(self.ev.eval_str("[Group.GetVariable('zero').GetValue]"), 100)
        self.assertIsInstance(self.ev.eval_str("[Owner.GetVariable('unknown').GetValue]"), Unknown)

    def test_typed_object_binding_supports_context_and_qualified_getter(self):
        context = {"__type__": "Location", "GetName": "Port"}
        self.ev = Evaluator(object_mocks("Selected.GetLocation", context), self.loc, [])
        self.assertEqual(self.ev.eval_str("[Selected.GetLocation]"), context)
        self.assertEqual(self.ev.eval_str("[Selected.GetLocation.GetName]"), "Port")

    def test_native_tables_contain_only_caller_supplied_text(self):
        table = requirements_list([("ready", True), ("pending", False), ("effect", None)])
        lines = table["GetLines"]
        self.assertTrue(lines[0]["HasPassed"])
        self.assertTrue(lines[1]["HasFailed"])
        self.assertTrue(lines[2]["IsUndefined"])
        self.assertEqual(string_pair_list([("label", "+1")])["GetRows"][0]["GetRight.GetStringView"], "+1")

    def test_action_binding_preserves_existing_context_and_unspecified_buttons(self):
        root = Element("widget", "widget")
        button = Element("button", "button", props={"scripted_action_tooltip": {"action_name": "example_action"}})
        button.ctx_item = {"Existing": 1}
        root.children.append(button)
        set_action_availability(root, {"example_action": False})
        self.assertEqual(button.ctx_item, {"Existing": 1, "PdxGuiWidget.IsUberButtonEnabled": False})
        self.assertFalse(hasattr(root, "ctx_item"))

    def test_strict_mode_includes_each_diagnostic_category(self):
        report = dict.fromkeys(DIAGNOSTIC_KEYS, [])
        self.assertFalse(has_diagnostics(report))
        for key in DIAGNOSTIC_KEYS:
            self.assertTrue(has_diagnostics({**report, key: ["unresolved"]}))

    def test_each_render_reports_cached_texture_misses_and_writes_artifacts(self):
        resources = RenderResources(GuiDB([]), self.loc, None, None)
        missing = "gfx/preview_missing_texture_for_test.dds"
        with tempfile.TemporaryDirectory() as folder:
            for index in range(2):
                root = Element("icon", "icon", props={"texture": missing})
                output = Path(folder) / f"preview_{index}.png"
                report = render_tree(root, Expander(resources.db), resources, [],
                                     width=8, height=8, output=output, metadata={"sample_data": True})
                self.assertEqual(report["missing_textures"], [missing])
                self.assertTrue(has_diagnostics(report))
                self.assertTrue(output.is_file())
                self.assertTrue(Path(report["tree"]).is_file())
                saved = json.loads(output.with_name(output.stem + "_report.json").read_text(encoding="utf-8"))
                self.assertEqual(saved, report)

    def test_mock_json_validation_and_caller_precedence(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "mocks.json"
            path.write_text(json.dumps({"mocks": [["Example", 7]]}), encoding="utf-8")
            pairs = load_mocks(path)
            self.assertEqual(Evaluator(pairs + [("Example", 2)], self.loc, []).eval_str("[Example]"), 7)
            for payload in ({}, ["wrong"], [[12, 1]], [["[", 1]]):
                path.write_text(json.dumps(payload), encoding="utf-8")
                with self.subTest(payload=payload), self.assertRaises((ValueError, re.error)):
                    load_mocks(path)

    def test_details_follow_scaled_layout_and_clip_to_the_rendered_image(self):
        resources = RenderResources(GuiDB([]), self.loc, None, None)
        focus = Element("widget", "sample_card", props={"position": [2, 3], "size": [4, 2]})
        partial = Element("widget", "sample_card", props={"position": [-2, -1], "size": [5, 4]})
        hidden = Element("widget", "sample_card", props={"visible": "no", "size": [4, 2]})
        outside = Element("widget", "sample_card", props={"position": [25, 0], "size": [2, 2]})
        root = Element("widget", "sample_panel", children=[focus, partial, hidden, outside])
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "panel.png"
            report = render_tree(root, Expander(resources.db), resources, [], width=20, height=10,
                scale=1.5, output=output, top_detail_height=4,
                detail_elements={"focus": focus, "partial": partial, "hidden": hidden, "outside": outside})
            self.assertEqual(set(report["details"]), {"focus", "partial", "top_detail"})
            with Image.open(report["details"]["focus"]) as detail, Image.open(output) as full:
                self.assertEqual(detail.size, (6, 4))
                self.assertEqual(detail.tobytes(), full.crop((3, 4, 9, 8)).tobytes())
            with Image.open(report["details"]["partial"]) as detail:
                self.assertEqual(detail.size, (4, 4))
            with Image.open(report["details"]["top_detail"]) as detail:
                self.assertEqual(detail.size, (30, 6))
            self.assertFalse((Path(folder) / "panel_hidden.png").exists())
            self.assertFalse((Path(folder) / "panel_outside.png").exists())
            self.assertEqual(json.loads(output.with_name("panel_report.json").read_text(encoding="utf-8")), report)
            self.assertFalse(has_diagnostics(report))

    def test_detail_names_cannot_escape_the_output_directory_or_collide(self):
        resources = RenderResources(GuiDB([]), self.loc, None, None)
        root = Element("widget", "widget")
        with tempfile.TemporaryDirectory() as folder:
            for name in ("../escape", "nested/name", "", "top_detail"):
                with self.subTest(name=name), self.assertRaises(ValueError):
                    render_tree(root, Expander(resources.db), resources, [], width=8, height=8,
                        output=Path(folder) / "panel.png", top_detail_height=4, detail_elements={name: root})

    def test_modifier_samples_use_supplied_metadata_and_selected_localization(self):
        metadata = {key: {"value_kind": kind} for key, kind in
                    (("test_rate", "percent"), ("test_monthly", "number"), ("test_zero", "number"))}
        values = {"test_rate": 0.2, "test_monthly": -0.1, "test_zero": 0}
        for label in ("Sample rate", "示例比率"):
            loc = type("Loc", (), {"get": lambda _, key: label if key == "MODIFIER_TYPE_NAME_test_rate" else None})()
            self.assertEqual(modifier_sample_lines(values, metadata, loc),
                [f"{label}: +20%", "test_monthly: -0.1", "test_zero: +0"])
        metadata["test_rate"]["value_kind"] = "number"
        self.assertEqual(modifier_sample_lines({"test_rate": 0.2}, metadata, self.loc), ["test_rate: +0.2"])

    def test_path_configuration_resolves_against_workspace(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {}, clear=True):
            configure_paths(workspace=Path(folder), mod_root=Path("mod"), game_root=Path("game"),
                            output_root=Path("previews"), language="english")
            self.assertEqual(Path(os.environ["EU5_RENDER_MOD_ROOT"]), Path(folder).resolve() / "mod")
            self.assertEqual(Path(os.environ["EU5_RENDER_GAME_ROOT"]), Path(folder).resolve() / "game")
            self.assertEqual(os.environ["EU5_RENDER_LANGUAGE"], "english")


if __name__ == "__main__":
    unittest.main()
