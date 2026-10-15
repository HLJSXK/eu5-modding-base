# on_built: shared EU5 building lifecycle alert

`on_built` alone is not a reliable completion signal for an upgradeable or reusable building. Inspect current building type and on-action examples, confirm the state available at each callback, and use `on_construction_ended` or another verified completion route when appropriate. Do not infer that `location_building_level` updates synchronously during an instant-build effect.

Workspace-specific generators and tests remain local.
