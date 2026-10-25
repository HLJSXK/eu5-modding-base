# Generic Actions: shared EU5 checks

## Required action registration — read before editing

A generic action is incomplete until these THREE companion registrations exist
in the same mod root as the action, whether the action is handwritten or generated:

1. Its id is **inside** an AI list's `actions = { ... }` block.
2. `PERFORM_<action_id>_ACTION` is registered in
   `main_menu/gui/messagetypes/<mod>.txt` (EU5 1.4.3+, additive; omit vanilla copies).
3. All **FIVE** localized keys exist: `HEADER`, `TITLE`, `SETUP`, `LOG`, `MAP`.
   `SETUP/LOG/MAP` alone is incomplete. Keep UTF-8 BOM and ensure `$aliases$` resolve.

For action `my_action`, the exact localization keys are:

```yaml
l_english:
 PERFORM_my_action_ACTION_HEADER:0 "My action"
 PERFORM_my_action_ACTION_TITLE:0 "My action"
 PERFORM_my_action_ACTION_SETUP:0 "My action"
 PERFORM_my_action_ACTION_LOG:0 "My action"
 PERFORM_my_action_ACTION_MAP:0 "My action"
```

On add/rename/move/delete, update or remove all companion entries together.
For generated actions, fix the owner and data inputs in `data/generated_files.yaml`,
regenerate, and run `scripts/validate.py --changed --fix --ai-report`.
An empty error log, filtered diagnostics, or a check covering only three fields
does not establish this contract. Do not suppress missing registrations.

Before editing a generic action, verify `potential`, `select_trigger`, `allow`, `effect`, AI list, and message type against current official definitions or vanilla examples. A selector or tooltip may evaluate before the final click, so guard optional scopes and numeric variables at the exact read site. Keep the actor, root, target, and saved-scope relationships explicit. Validate the action in both the selection UI and final execution path.

Read `.eu5-base/docs/technical/EU5_Modding_Knowledge_Base.md` and the matching shared anti-pattern entries for concrete syntax. Workspace cards add implementation-specific contracts.
