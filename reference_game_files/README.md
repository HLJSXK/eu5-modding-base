# Filtered EU5 game reference

`game/` is the shared text-only mirror produced by [`scripts/sync_reference.py`](../scripts/sync_reference.py). The 4,571 game files from both source projects matched byte-for-byte at extraction. Their most recent preserved sync logs are in `migration/sync_logs/` (2026-10-03 for SOL and 2026-10-13 for Towards Victory). Those logs identify collection times, not an exact game build; recheck syntax against the installed version when needed.

The filter excludes the installed `mod/` directory, every `gfx/` directory, binary/media files, other language locales, individual files above 10 MiB, and directories with more than 30 MiB of eligible direct files. It keeps English/Simplified Chinese localization and other small text formats after a binary-content sniff. See the script for the executable policy and `migration/source_readmes/` for the original descriptions.

From this base checkout run `python scripts/sync_reference.py --dry-run`, then `python scripts/sync_reference.py` to refresh. Refreshing replaces `game/` and writes `data/sync_reference.log`.
