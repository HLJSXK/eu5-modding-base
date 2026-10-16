# EU5 GUI Modding Guide (Shared)

> **Read this before writing or changing any `.gui` file, GUI expression, or GUI-displayed localization.**
> Every rule below is marked by evidence level:
> **[实机]** = confirmed against a 1080p in-game screenshot (2026-10-11),
> **[源]** = read directly from game/official files, **[推]** = inferred, not yet confirmed.
> Detailed derivations and the reusable renderer live in the `eu5-modding-base` project.
> Workspace-specific screenshots and scenarios remain in each mod project.

## 0. How to work on GUI in any project

1. **Read the type definition before using it.** Never guess a type's blocks. The tools accept an absolute `--workspace` path, a `--mod-root` path relative to that workspace (or absolute), and a `--game-root` that points to the installed game or its `game/` directory.

   ```powershell
   $base = if (Test-Path .eu5-base) { (Resolve-Path .eu5-base).Path } else { (Resolve-Path .).Path }
   $workspace = (Resolve-Path .).Path
   $modRoot = 'src' # Select the deployable mod root for this workspace.
   $gameRoot = 'C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis V'
   $env:PYTHONUTF8 = '1'
   & $env:EU5_PYTHON (Join-Path $base 'ai_gui_assessment/renderer/guidef.py') --workspace $workspace --mod-root $modRoot --game-root $gameRoot situation_card_common card_common
   ```

2. **Use the vanilla component catalogue.** `reference_game_files/game/in_game/gui/ui_library.gui` is Paradox's own
   catalogue of reusable types (windows, buttons, text formats, cards, portraits). Find the visual you want there,
   then copy its type. In-game it opens with `GUI.CreateWidget gui/ui_library.gui ui_library_window`
   (close: `GUI.ClearWidgets ui_library_window`).

3. **Render before launching the game.** The shared renderer reads the selected game's GUI, textures, fonts, and localization, overlays the selected mod root, then writes a PNG and an element tree. Text-only `reference_game_files/` snapshots are suitable for `guidef.py`, but rendered output needs the installed game for fonts and textures.

   ```powershell
   & $env:EU5_PYTHON (Join-Path $base 'ai_gui_assessment/renderer/run.py') --workspace $workspace --mod-root $modRoot --game-root $gameRoot --name situation_card_common --output preview.png
   & $env:EU5_PYTHON (Join-Path $base 'ai_gui_assessment/renderer/compare.py') SHOT RENDER sx sy w h OUT
   ```

   To check a design before it exists in a mod, write a throwaway `.gui` and render it with `run.py --gui-file prototype.gui --name root_name --mocks mocks.json --output preview.png`. `--output-root` chooses the output directory; a relative value is resolved against `--workspace`. The generic command accepts a JSON list of `[expression regex, value]` pairs and reports unresolved bindings rather than silently inventing values. `RENDER_EXTRA_ROOTS` (separated by `;` on Windows) adds prototype texture roots. Workspace scenario runners may provide richer screen presets and mock schemas.

4. **When the renderer and the game disagree, the game wins.** Record the corrected rule here and in the
   workspace's GUI verification notes.

## 1. Files, composition and overrides

| Rule | Level |
|---|---|
| `.gui` files override **by whole relative path**; there is no INJECT/REPLACE for GUI. Owning one button in `location_window.gui` means owning the full file (so a generator owns the complete file). | 源 |
| A `blockoverride` requires an inherited block with that exact name. Verify the inherited type and the scope available at the insertion point before adding tooltip content. | 源 + 实机验证 |
| `type a = b { ... }` inherits `b`; `template x { }` + `using = x` pastes properties; `block "n" { default }` is a slot replaced **entirely** by `blockoverride "n" { }` (empty override deletes the default). | 源 |
| Override content lands **where the block sits**, and is validated there: a layout child of an `hbox`/`vbox` cannot receive `parentanchor` or a `%` size (`pdx_gui_validation.cpp: Unsupported property ... child of a hbox/vbox`). This also applies to properties written directly in the shared type. Vanilla floating decorations set `ignore_layout = yes` (main_menu_cooltip_types.gui:254). The renderer checks resolved children after inheritance and overrides. | 实机错误日志 + 源 |
| Overrides propagate into nested type instances, but **an instance's own `blockoverride` beats one inherited from outside** (otherwise nested scrollbox-in-scrollbox would recurse forever). | 实机 |
| Text set on a button (`text` / `raw_text`) is drawn by the button type's `buttonText = { textbox }` child. | 实机 |
| Hidden children in `hbox`/`vbox` take **neither size nor spacing**. | 实机 |
| Nested widget `datacontext` expressions can refer to an ancestor's context: the battle view binds `Combat.GetDefender`, then a child binds `CombatSide.GetLeft`. A static renderer must retain the parent object while resolving the child. | 源 |

## 2. Layout

| Rule | Level |
|---|---|
| Box children: `fixed` keeps its hint; `expanding` / `growing` take extra space. **`expanding` children get extra space first; `growing` only gets leftovers.** `expand = {}` is a `growing` widget, so it does *not* steal space from an expanding sibling. | 实机 |
| If no child can grow, leftover space is **distributed evenly between the children** (first/last flush with the edges) — the box behaves like `justify-content: space-between`, not left-aligned. Use `expand = {}` to left/right align. Final-row spacer widgets are one way to make this intent explicit. | 实机 |
| `min_width` on a non-text element acts as a minimum width. | 实机 |
| **`text_single` inherits `autoresize = yes`, and autoresize beats a declared `size`.** A fixed-width column cell that does not set `autoresize = no` collapses to its content width, so neighbouring columns run together. | 实机 |
| **A wrapping text with no `max_width` reports its unwrapped width as a *minimum*.** An hbox measures its children with no width hint, so one uncapped paragraph (or `TooltipListBase` body) becomes the frame's minimum width and drags the whole tooltip past its 450px budget. Give every wrapping text an explicit `max_width`. | 实机 |
| `max_width` also caps the element's width; an expanding `text_multi` stops at `max_width` and the parent centres it. | 实机 |
| `widgetanchor` defaults to `parentanchor`. | 实机 |
| A vertical scrollbar overlays the content; it does not narrow it. | 实机 |
| Fixed-width single-line text that does not fit **shrinks its font** down to `fontsize_min` (vanilla default 8). | 实机 |
| **Fixed-width rows can contain children outside their own measured rectangle.** Budget the label, icons and all gaps, and split large groups explicitly. Inspect descendant positions as well as total dimensions; fixed-width columns should set `autoresize = no` when neighboring values must remain aligned. | 源 + 渲染检查 |
| `righttoleft = yes` / `bottomtotop = yes` reverse box order. | 源 |
| A `dynamicgridbox` with `flipdirection = yes` lays items horizontally; `datamodel_wrap = 1` then starts a new row after each item. The IOs member list uses this to show three estate rows. This verified case does not establish vertical wrapping semantics. | 实机 |
| **A bare `widget` never sizes to its children.** A widget-like element takes its hint from its own `size`, or only from children carrying `set_parent_size_to_minimum = yes` (a child's `resizeparent = yes` works the same). A bare `widget` holding an `hbox` measures **0** high, and `minimumsize` on the widget itself is measured too late to rescue it. Use a `vbox` as a framed container, and emit art as a **sized child widget**, never as a bare `background` on a childless element. | 源 |
| **Expression-valued properties must be bracketed as `"[...]"`.** Unbracketed, a numeric property does not evaluate and silently takes its default - two `layoutstretchfactor_horizontal` children then split a row evenly (36/36 in a 72px box) instead of proportionally. | 源 |

## 3. Textures

| Rule | Level |
|---|---|
| `spriteborder` and `framesize` are in **GUI units**, not texture pixels: texture pixels = value × `texture_density`. | 实机 |
| A `ranged_slider` part instantiated through a template may have both its own `texture` and `background` layers. For example, `economy_slider_track` uses `bg_progress_bar_frame`; render the background before the track texture, including its margin and alpha. | 实机 |
| `corneredtiled` tiles the middle; a border-only pattern (e.g. `pattern_bevel_vertical_bis`) shows only the edge strip. | 实机 |
| A `modify_texture` with a `color` but no texture is a flat colour layer; the colour may be data-bound (`"[LocationPopItem.GetColor]"`). | 实机 |
| `modify_texture` without `blend_mode` behaves as normal (mask textures with black RGB still tint correctly). | 推 |
| Pie slices are drawn through the slice texture; `piechart_alpha.dds` is a ring, so vanilla pies are rings with an icon in the centre. A `pieslice` `color` must be a literal `{ r g b a }` - a named colour cannot be used there. Slice `value`s may be expressions and are normalised by the engine, so pass raw counts and one chart works at any scale. | 实机 |
| Pop-type colours come from `main_menu/common/named_colors/02_map.txt` (`pop_nobles` …). | 源 |
| **Stacked and offset bars are `barchart` + `barslice`/`barslice_no_highlight`.** Slice values are normalised (raw counts are fine), `direction = vertical` stacks bottom-up, `righttoleft = yes` reverses; vanilla uses it inside tooltips (`combat_tooltips.gui:2909`). A transparent leading slice used as an offset has no vanilla precedent. | 源 |
| `flowcontainer` does not wrap by available width; vanilla wraps only with a fixed `wrap_count`. Split width-dependent rows in the generator. | 源 |
| **`using = X` inlines a `type X`, it is not a texture reference.** A `progressbar` whose `using` names a non-existent type resolves no texture and draws **nothing while still occupying its layout slot and reporting a full size** - invisible to any measurement check. Name `progresstexture` / `noprogresstexture` outright (progressbars.gui:285) and carry `texture_density` / `spriteType` / `spriteborder` on the element. Verify bars by pixel. | 源 |
| **`TooltipListBase` already contains a `TooltipTableHeader`.** A section caption needs only to override `tableheader_text` / `table_header_background`; adding a body child stacks a second header and roughly doubles the band height (~60px vs ~33px). | 实机 |
| **A `blockoverride` replaces a block entirely, and an instance's own override beats one inherited from outside.** One shared block name therefore cannot carry different values into sibling instances - each keeps its own default. Expose one container block per repeated row and let the caller fill it with children that each carry their own override. Getting this wrong duplicates elements silently rather than erroring: emitting five cells *alongside* a block that already held five defaults produced ten per row. | 实机 |

## 4. Text, numbers and icons

**[Runtime lexer log + vanilla source] GUI strings do not accept `\n` or `\t` escapes.** Use `[Localize('NEWLINE_BREAK')]` between tooltip sections, as `in_game/gui/shared/character_tooltips.gui:1571` does. Localization and GUI strings have different escaping rules; escaping another backslash only makes the GUI string lexically valid. The shared GUI parser rejects unsupported quoted-string escapes before expansion.

**[Runtime log + vanilla source] Tooltip text templates need tooltip context.** `tooltip_text_block_template` inherits `fonttintcolor = "[ExtraTooltipInfo.GetTintColor]"` from `main_menu_cooltip_types.gui:336`. A regular panel has no `ExtraTooltipInfo`, so static text can repeatedly report `No context supplied` / `FetchData failed`. In an always-visible panel use `text_multi` with `layoutpolicy_horizontal = expanding`, `autoresize = yes`, and an explicit `max_width`, as in `council_of_trent.gui:219`. Keep tooltip templates inside contextual tooltips.

**[Runtime log + vanilla source] GUI arithmetic and bindings are typed.** `ScriptValue` returns `CFixedPoint`; `Multiply_float` returns float. Keep calculations in `*_CFixedPoint` until conversion. A numeric property such as `max = "[1]"` is not a literal; write `max = 1`. Do not put text formatting suffixes such as `|+0` inside numeric properties. Separate `#format` tags from adjacent punctuation with whitespace, for example `#R -[value|2]#!`.

**[Source + screenshot symptom] Supply `noprogresstexture` explicitly.** The progressbar shader samples a separate empty-region texture; a parent background does not supply it. Missing this texture can produce a solid fallback bar, so verify rendered pixels as well as the measured rectangle.

| Rule | Level |
|---|---|
| Fonts: body `StandardGameFont` (NotoSerif; Chinese falls back to NotoSansSC), headers `HeadersFont` (NotoSerif SemiBold; Chinese NotoSerifSC). Font sizes: Small 15, Medium 18, Big 23. | 源 |
| **`text` resolves a localization key; `raw_text` is printed verbatim.** `text` also evaluates an embedded `[expression]` (`text = "[Goods.GetDemandsInfo]"`). Put keys in `text`, and expressions / `@icon!` texticons / `#colour ... #!` markup in `raw_text`. A key placed in `raw_text` prints literally in the UI. | 实机 |
| Autoresized text is **21 px per line at font size 15** (single- and multi-line). The template's `size {0 23}` does not apply to autoresized text. | 实机 |
| `#name ... #!` applies a format from `loading_screen/gui/textformatting.gui`. **`##` prints a literal `#`.** | 实机 |
| Number suffix `\|+N`: colours by sign (positive green, negative red, zero plain) **without printing a `+`**. `\|=` / `\|+=`: also prints `+` on positive values. Digits = decimals, `%` multiplies by 100. | 实机 |
| `\|<1%`, `\|W`, `\|R`, `\|G`, `\|-=`, `\|=+`, `\|Y`: not yet confirmed. Engine-formatted strings (e.g. `GetGrowthForUI`) keep their own colour. | 推 |
| **Goods icons (`@wheat!`, `@amber!` …) are registered by the engine from the goods database and are NOT in `font_icons.gui`.** Check `in_game/common/goods/` instead. They render at `NJominiIcons.MODIFIER_TEXT_ICON_SIZE` (32 px at font 18, ≈27 px at font 15). | 实机 |
| Other `@icon!` names: `main_menu/gui/shared/font_icons.gui`. | 源 |

## 6. What the renderer cannot do (verify in game)

The renderer cannot reproduce 3D scenes, illustrations without accessible textures, procedural flags/coats of arms, character portraits, animations, hover states, or real save data. A scenario adapter can statically render `dropdown`, `ranged_slider`, and tooltip-table states with mocks; the renderer does not execute game actions or parse arbitrary `textcontext` strings into live tables. Record remaining differences in the workspace's GUI verification notes.

### Named sibling containers

**[Runtime log; project-independent rule.]** Duplicate named siblings can override earlier widgets. Give repeated outer containers unique names; local child names may repeat under different parents. The renderer diagnoses explicit sibling collisions. Inherited defaults are outside this diagnostic.

## 7. Further reading

| Document | Content |
|---|---|
| `eu5-gui-renderer` package | Reusable parser, type/template expansion, data-binding evaluator, layout engine, text renderer, texture compositor |
| Workspace GUI notes | In-game verification results, screenshots, and project-specific scenarios |
| the workspace's GUI anti-patterns and validation notes | Known GUI mistakes, summarised in `BRIEF.md` |



### Full in-game HUD preview

Use the shared run.py with --scenario hud instead of --name. Default size is
1920x1080. --workspace, --mod-root, --game-root, --output-root, --output,
--width, --height, --scale and --mocks remain supported.

The scenario composes ingame_topbar, outliner and message_log from the selected
game/mod files. Native outliner rows use original army category/unit templates
with invented sample data. Custom JSON mocks take precedence. Output includes
the full PNG, top-detail crop, element tree and JSON diagnostics.
The example is Chinese Hungary in 1337, paused with closed detail panels and a
collapsed map menu. It is not save data. The 3D map, dynamic flags and portraits
remain unsupported; unresolved bindings are reported. No screen-wide
pixel-accuracy claim applies.

**[Source + parser regression]** Both types and Types group declarations must
register their children, preserving type-name case. Vanilla hud_topbar.gui:46
uses Types HUD_TopbarTypes; panels/left_panel/left_panel.gui:93 uses Types
LeftPanelTypes. Ignoring these groups silently drops both HUD bars. This is
handled by the shared parser, not a scenario-specific AST repair.
