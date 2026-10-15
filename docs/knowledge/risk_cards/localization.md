# Localization: shared EU5 checks

EU5 localization YAML needs UTF-8 BOM and straight ASCII double quotes. Verify key uniqueness, language coverage, interpolation scope, and supported color/format tags. A localization parse error can hide otherwise valid script and GUI behavior. Check dynamic keys and generated files at their source data/generator, then validate English and Simplified Chinese outputs together when the workspace supports both.

Do not use a workspace-specific semantic color scheme as a universal engine rule.
