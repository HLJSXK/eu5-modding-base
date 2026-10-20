"""Regressions exposed by concrete IO panels (no installed assets needed)."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image
from eu5_gui_renderer import data
from eu5_gui_renderer.data import Evaluator
from eu5_gui_renderer.engine import Engine
from eu5_gui_renderer.gui import Element, Expander, GuiDB
from eu5_gui_renderer.gui import build_target


class PanelRenderingTests(unittest.TestCase):
    def setUp(self):
        self.loc = type("Loc", (), {"get": lambda _, k: None})()
        self.log = []
        self.ev = Evaluator([], self.loc, self.log)
        self.engine = Engine(None, self.ev, self.loc, None, None, 1)

    def test_selected_instance_retains_overrides(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "panel.gui"
            path.write_text('types { type panel = widget { block "content" { size={10 20} } } } '
                            'panel={blockoverride "content" {size={300 400}}}', encoding="utf-8")
            db = GuiDB([path])
            ex = Expander(db)
            self.assertEqual(build_target(db, ex, "panel", path).props["size"], ["300", "400"])
            self.assertEqual(build_target(db, ex, "panel", None).props["size"], ["10", "20"])

    def test_using_inlines_inherited_type_properties(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "types.gui"
            path.write_text('types {type base = widget { alpha=0.5 } '
                            'type deco = base {size={20 30}}} widget={using=deco}', encoding="utf-8")
            db = GuiDB([path])
            node = db.roots[str(path)][1]
            el = Expander(db).build(node.key, node.value, {})
            self.assertEqual(el.props["size"], ["20", "30"])
            self.assertEqual(el.props["alpha"], "0.5")

    def test_textcontext_stays_local_to_each_table(self):
        self.ev.mocks = [(data.re.compile("Country"), {"__type__": "Country", "GetName": "Hungary"}),
                         (data.re.compile("Effects"), {"__type__": "StringPairList", "GetRows": [1, 2]})]
        parent = Element("widget", "widget", props={"datacontexts": ["[Country]"]})
        table = Element("vbox", "table", props={"textcontext": "[Effects]", "ontextcontextchanged": "handler"})
        outer = self.engine.push(parent)
        inner = self.engine.push(table)
        self.assertEqual(self.ev.eval_str("[Country.GetName]"), "Hungary")
        self.assertEqual(self.ev.eval_str("[StringPairList.GetRows]"), [1, 2])
        self.engine.pop(inner)
        self.assertIsInstance(self.ev.eval_str("[StringPairList.GetRows]"), data.Unknown)
        self.engine.pop(outer)
        self.assertEqual(self.ev.item_stack, [])

    def test_arbitrary_effect_text_is_reported_without_guessing(self):
        el = Element("vbox", "table", props={"textcontext": "unparsed effect text", "ontextcontextchanged": "handler"})
        self.assertEqual(self.engine.push(el), 0)
        self.assertEqual(self.engine.unsupported_textcontexts, {"unparsed effect text"})

    def test_dynamic_margin_and_numeric_id(self):
        el = Element("widget", "widget", props={"margin_left": "[Add_int32('(int32)10','(int32)5')]"})
        self.assertEqual(self.engine.margins(el), (15, 0, 0, 0))
        self.assertEqual(self.ev.eval_str("[ToString_int32('(int32)3')]"), "3")

    def test_mod_concepts_and_font_icons_override_game(self):
        with tempfile.TemporaryDirectory() as folder:
            game, mod = Path(folder) / "game", Path(folder) / "mod"
            for root, texture in ((game, "vanilla"), (mod, "mod")):
                concepts = root / "main_menu/common/game_concepts"
                concepts.mkdir(parents=True)
                (concepts / "images.txt").write_text(f'preview={{texture="gfx/{texture}.dds"}}', encoding="utf-8")
                icons = root / "main_menu/gui/shared"
                icons.mkdir(parents=True)
                (icons / "font_icons.gui").write_text('texticon={icon=custom iconsize={texture="gfx/' + texture + '.dds" size={18 18}}}', encoding="utf-8")
            with patch.object(data, "GAME", game), patch.object(data, "MOD", mod):
                self.assertEqual(data.load_concept_textures()["preview"], "gfx/mod.dds")
                self.assertEqual(data.TextIcons().get("custom")["texture"], "gfx/mod.dds")

    def test_progressbar_pixels_at_both_support_ranges(self):
        for value in (0, 35, 68, 100):
            with self.subTest(value=value):
                el = Element("progressbar", "progressbar", props={"max": "100", "value": str(value),
                             "progresstexture": "fill", "noprogresstexture": "empty"}, w=100, h=10)
                self.engine._texture_layer = lambda _, texture, w, h, color=None: Image.new(
                    "RGBA", (int(w), int(h)), "blue" if texture == "fill" else "black")
                image = Image.new("RGBA", (100, 10))
                self.engine._progressbar(el, image, 1, None)
                pixels = [image.getpixel((x, 5)) for x in range(100)]
                self.assertEqual(sum(p == (0, 0, 255, 255) for p in pixels), value)

    def test_disabled_button_uses_native_disableframe(self):
        el = Element("button", "button", props={"texture": "button.dds", "enabled": "no",
                     "disableframe": "4", "upframe": "1", "down": "yes", "downframe": "3"}, w=20, h=10)
        with patch("eu5_gui_renderer.engine.compose", return_value=None) as compose:
            self.engine.render(el, Image.new("RGBA", (20, 10)))
        self.assertEqual(compose.call_args.args[0]["frame"], "4")


    def test_conditional_tints_only_apply_when_visible(self):
        from eu5_gui_renderer.textures import compose
        for visible, expected in ((False, "white"), (True, "red"), ("no", "white"), (None, "white")):
            with self.subTest(visible=visible), patch("eu5_gui_renderer.textures.TEXTURES.load", return_value=Image.new("RGBA", (2, 2), "white")):
                spec = {"texture": "base", "modifies": [
                    {"visible": "[completed]", "color": [1, 0, 0, 1]},
                ]}
                output = compose(spec, 2, 2, 1, lambda value: visible if value == "[completed]" else value)
                self.assertEqual(output.getpixel((0, 0)), Image.new("RGBA", (1, 1), expected).getpixel((0, 0)))

    def test_hidden_tint_does_not_load_its_texture(self):
        from eu5_gui_renderer.textures import compose
        with patch("eu5_gui_renderer.textures.TEXTURES.load", return_value=Image.new("RGBA", (2, 2), "white")) as load:
            compose({"texture": "base", "modifies": [{"visible": "no", "texture": "missing"}]},
                    2, 2, 1, lambda value: value)
        load.assert_called_once_with("base")


if __name__ == "__main__":
    unittest.main()
