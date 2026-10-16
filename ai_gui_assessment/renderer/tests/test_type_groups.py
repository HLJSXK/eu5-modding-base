import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from eu5_gui_renderer.pdx import parse
from eu5_gui_renderer.gui import GuiDB, Expander

class TypeGroupTests(unittest.TestCase):
    def test_both_spellings_register_and_expand(self):
        for spelling in ('types', 'Types'):
            with self.subTest(spelling=spelling), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / 'hud.gui'
                path.write_text(spelling + ' HUD { type topbar = widget { size = { 640 40 } } } '
                                'widget = { name = "hud" topbar = {} }', encoding='utf-8')
                db = GuiDB([path])
                node = db.roots[str(path)][1]
                element = Expander(db).build(node.key, node.value, {})
                self.assertEqual(len(element.children), 1)
                self.assertEqual(element.children[0].kind, 'widget')
                self.assertEqual(element.children[0].props['size'], ['640', '40'])

    def test_type_names_remain_case_sensitive(self):
        nodes = parse('Types HUD { type TopBar = widget {} type topbar = icon {} }')
        self.assertEqual(nodes[0].key, 'types')
        self.assertEqual([n.key for n in nodes[0].value], ['type:TopBar', 'type:topbar'])

    def test_truncated_group_has_no_index_error(self):
        for spelling in ('types', 'Types'):
            self.assertEqual(parse(spelling + ' HUD'), [])

if __name__ == '__main__':
    unittest.main()
