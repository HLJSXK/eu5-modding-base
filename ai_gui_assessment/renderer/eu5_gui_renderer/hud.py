"""Compose vanilla HUD roots with sample data and native outliner entries."""
from . import scen_hud
from .gui import Element

UNSUPPORTED = scen_hud.UNSUPPORTED


def walk(element):
    yield element
    for child in element.children:
        yield from walk(child)


def find_root(db, suffix, name):
    for path, nodes in db.roots.items():
        if path.replace(chr(92), '/').endswith(suffix):
            for node in nodes:
                if node.is_block() and any(p.key == 'name' and p.value == name for p in node.value):
                    return path, node
    raise ValueError(f'HUD root not found: {suffix}: {name}')


def mocks():
    return scen_hud.hud() + [
        (r"Outliner\.IsExpanded|Outliner\.IsPinned", True),
        (r"Outliner\.(IsMouseOver|IsSettingsShowing|IsAnyOccludingPanelOpened)", False),
        (r"(?:AccessMessageLog|MessageLog)\.IsExpanded|IsMessageLogShown", False),
        (r"InGameTopbar\.AccessControlGroups\.AccessGroups", []),
        (r"OutlinerEntry\.IsVisible|OutlinerCategoryEntry\.IsOpened", True),
        (r"OutlinerEntry\.IsHighlighted|OutlinerCategoryEntry\.IsClosed", False),
        (r"Unit\.GetAttrition", 0),
        (r"Unit\.IsExiled|Unit\.IsAutomated", False),
        (r"Unit\.HasPrisoners|IsUnitSelected\(Unit.Self\)", False),
        (r"Unit\.GetTotalRegularCount", 12),
        (r"Unit\.GetTotalLevyCount|Unit\.GetTotalMercenaryCount", 0),
        (r"Unit\.GetStatusTexture", 'gfx/interface/icons/unit_status/stationed.dds'),
        (r"GetQuickUnitAdjustedCount\(Unit.Self\)", {'__type__': 'UnitAdjustedCount', 'GetRegularCount': 12, 'GetLevyCount': 0, 'GetMercenaryCount': 0, 'GetPrisonerCount': 0}),
    ]


def build(db, ex, width, height):
    root = Element('widget', 'offline_hud', {'size': [str(width), str(height)]})
    for filename, name in [('ingame_topbar.gui', 'ingame_topbar'),
                           ('outliner.gui', 'outliner'),
                           ('message_log.gui', 'message_log')]:
        path, node = find_root(db, 'in_game/gui/' + filename, name=name)
        root.children.append(ex.build(node.key, node.value, {}, path, node.line))
    # In the game these original GUI roots are inserted by native code. Here
    # supply a small, explicitly invented army list using the same roots.
    entries = next(e for e in walk(root) if e.props.get('name') == 'outliner_entries')
    entries.props['size'] = ['405', '93']
    stack = Element('vbox', 'offline_native_entry_stack', {'size': ['405', '93'], 'spacing': '0'})
    entries.children.append(stack)
    for name, context in [
        ('unit_army_category_entry', {'OutlinerCategoryEntry.GetName': '陆军', 'OutlinerCategoryEntry.GetEntryCount': 2}),
        ('army_unit_entry', {'Unit.GetNameWithNoTooltip': '王家军团', 'Unit.GetVisualStrength': '12,000'}),
        ('army_unit_entry', {'Unit.GetNameWithNoTooltip': '边境守军', 'Unit.GetVisualStrength': '6,000'}),
    ]:
        path, node = find_root(db, 'in_game/gui/outliner_entries.gui', name=name)
        child = ex.build(node.key, node.value, {}, path, node.line)
        child.ctx_item = context
        stack.children.append(child)
    return root
