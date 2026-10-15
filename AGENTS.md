# Shared EU5 agent requirements

Read `.eu5-base/CLAUDE.md` before acting. Then read the current workspace `CLAUDE.md` and `AGENTS.md` (if present). Shared rules and workspace rules are cumulative: the workspace may add constraints but must not hide the base reference corpus or workflow.

When working from the `eu5-modding-base` checkout itself, treat `.eu5-base/`
references as paths relative to the base root and read `CLAUDE.md`,
`AGENTS.md`, and `docs/knowledge/BRIEF.md` directly.

The workspace must provide `.eu5-base`; if it is absent, run `scripts/bootstrap_base.py`. Use the workspace context builder to load both roots. Do not infer that a local BRIEF or route table contains the complete knowledge set.
