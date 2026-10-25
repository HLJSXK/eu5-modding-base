# GUI: shared EU5 checks

Read `.eu5-base/docs/guides/EU5_GUI_Modding_Guide.md` before editing `.gui` files, GUI expressions, tooltip layouts, or GUI-bound localization. Resolve every type/template and its actual block shape from game files; check data context inheritance, widget sizes, text wrapping, and visible bindings. For icons, check vanilla `font_icons.gui` or engine-registered goods texticons before creating widgets or sprites.

Use the shared renderer for source-level previews and an in-game check for final behavior. Workspace cards may add local GUI ownership and compatibility rules.

## Player-facing text: say less

Agents often put too much detail into player-facing text. Players do not need to know everything.

- A title names the thing and nothing more.
- A subtitle is one short sentence that says what the number means.
- Describe the concept generically ("这表示人们……的整体质量"). Don't paraphrase its current inputs, such as "funds per 1,000 people". When new sources are added (buildings, modifiers), an input-based description silently becomes false.
- Leave out formulas, multipliers and floors, weighting rules, threshold tables, and lists of what the value affects. Leave out "does not change X" disclaimers too.
- Put that material in design docs or modifier notes. If you think the player truly needs a fact, ask the user before adding it.

Before adding any line, ask whether the player needs it to read this panel right now. If not, cut it.

No colons in title-like text. Value breakdowns split a name at a colon (":" or "：") and right-align the part after it. You can't predict which strings the engine will show in a breakdown. So keep every title-like value colon-free in both languages: names, titles, legends, option names, map-tooltip headlines, log titles, and "label: value" lines. Use parentheses or a space instead (`localization_title_value_contains_colon`).

When asked to remove text, remove it everywhere. The same text or builder often feeds several surfaces: topbar tooltips, map-mode tooltips, situation panels, local panels, and compat submods. A removal request applies to all of them unless the user names a surface. Never gate the removal behind a per-surface flag. Remove it at the shared builder, drop the dead localization keys, and regenerate every consumer.

Evidence: user review, 2026-10-24, SOL living-standard tooltip.

- The title "生活水平与同比" became "生活水平".
- The subtitle used to be the formula. A first rewrite listed migration and growth effects, and the user rejected that too. A second rewrite, "每千人每年可自由支配的钱", was false, because buildings also affect SOL. The accepted version is "这表示人们衣食、居住和日常生活的整体质量。"
- The footnote about floors, weighting and YoY thresholds was removed.
- Removing the goods-hover notes and the summary/legend lines only from the topbar was rejected. The fix removed them from every surface.
