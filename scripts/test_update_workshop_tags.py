"""Exercise tag-only boundaries, ABI layout and failures without changing Steam."""
import contextlib
import ctypes as ct
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import update_workshop_tags as tags_tool

ITEM_ID = 1234567890  # Synthetic item ID; these tests never connect to Steam.
TAGS = ["Balance", "Trade and Economics", "User Interface"]


def item(owner=42, app=tags_tool.APP_ID, title=b"Example Mod"):
    result = tags_tool.ItemDetails()
    result.item_id = ITEM_ID
    result.owner, result.consumer_app, result.title = owner, app, title
    result.description = b"Existing description must survive"
    result.file_handle, result.preview_handle = 12, 34
    return result


class TagToolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.metadata = self.root / "metadata.json"
        self.definitions = self.root / "create_mod_tags.json"
        self.definitions.write_text(json.dumps({"tags": [{"SteamRef": x} for x in TAGS]}), encoding="utf-8")
        self.write_metadata(TAGS)
        self.output = io.StringIO()
        self.redirect = contextlib.redirect_stdout(self.output)
        self.redirect.__enter__()
        self.addCleanup(self.redirect.__exit__, None, None, None)

    def write_metadata(self, tags, **extra):
        self.metadata.write_text(json.dumps({"game_id": "eu5", "tags": tags, **extra}), encoding="utf-8-sig")

    def test_bom_metadata_is_read_without_rewriting(self):
        original = self.metadata.read_bytes()
        self.assertEqual(tags_tool.read_tags(self.metadata, self.definitions), TAGS)
        self.assertEqual(self.metadata.read_bytes(), original)

    def test_invalid_tag_lists_are_rejected(self):
        for bad in ([], None, "Balance", [1], [""], [" Balance"], ["Balance", "Balance"],
                    ["balance"], ["Balance,Gameplay"], ["Balance\n"], ["x" * 256]):
            with self.subTest(tags=bad):
                self.write_metadata(bad)
                with self.assertRaises(tags_tool.ToolError):
                    tags_tool.read_tags(self.metadata, self.definitions)

    def test_other_game_metadata_rejected(self):
        self.write_metadata(TAGS, game_id="other")
        with self.assertRaises(tags_tool.ToolError):
            tags_tool.read_tags(self.metadata, self.definitions)

    def test_offline_preview_never_initializes_steam(self):
        with patch.object(tags_tool, "SteamClient") as native, patch.object(tags_tool, "read_tags", return_value=TAGS):
            self.assertEqual(tags_tool.main(["--item-id", str(ITEM_ID), "--metadata", str(self.metadata)]), 0)
        native.assert_not_called()

    def test_metadata_is_required_in_shared_entry(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as exited:
            tags_tool.main(["--item-id", str(ITEM_ID)])
        self.assertEqual(exited.exception.code, 2)

    def test_offline_definitions_come_from_base_not_caller_workspace(self):
        with patch.object(tags_tool, "read_tags", return_value=TAGS) as read:
            self.assertEqual(tags_tool.main([
                "--item-id", str(ITEM_ID), "--metadata", str(self.metadata)]), 0)
        read.assert_called_once_with(
            self.metadata.resolve(),
            tags_tool.ROOT / "reference_game_files/game/main_menu/create_mod_tags.json")

    def test_relative_metadata_uses_callers_working_directory(self):
        import os
        previous = Path.cwd()
        try:
            os.chdir(self.root)
            with patch.object(tags_tool, "read_tags", return_value=TAGS) as read:
                self.assertEqual(tags_tool.main([
                    "--item-id", str(ITEM_ID), "--metadata", "metadata.json"]), 0)
            self.assertEqual(read.call_args.args[0], self.metadata.resolve())
        finally:
            os.chdir(previous)

    def test_item_ids_cannot_create_or_wrap(self):
        for invalid in ("0", "-1", str(1 << 64), str(tags_tool.INVALID_HANDLE), "oops"):
            with self.subTest(value=invalid), self.assertRaises(tags_tool.argparse.ArgumentTypeError):
                tags_tool.item_number(invalid)

    def client(self, before=None, old=None, after=None, new=None):
        client = Mock(account_id=42)
        client.query.side_effect = [(before or item(), old if old is not None else ["Advancements"]),
                                    (after or item(), new if new is not None else TAGS)]
        return client

    def test_check_is_read_only_even_for_non_owner(self):
        client = self.client(before=item(owner=999))
        tags_tool.synchronize(client, ITEM_ID, TAGS, False)
        client.set_tags.assert_not_called()
        self.assertIn("owns item: no", self.output.getvalue())

    def test_wrong_app_and_non_owner_cannot_submit(self):
        for details in (item(app=480), item(owner=999)):
            client = self.client(before=details)
            with self.assertRaises(tags_tool.ToolError):
                tags_tool.synchronize(client, ITEM_ID, TAGS, True)
            client.set_tags.assert_not_called()

    def test_matching_tags_do_not_submit(self):
        client = self.client(old=list(reversed(TAGS)))
        tags_tool.synchronize(client, ITEM_ID, TAGS, True)
        client.set_tags.assert_not_called()

    def test_apply_replaces_tags_then_reads_back(self):
        client = self.client()
        tags_tool.synchronize(client, ITEM_ID, TAGS, True)
        client.set_tags.assert_called_once_with(ITEM_ID, TAGS)
        self.assertEqual(client.query.call_count, 2)
        self.assertIn("Verified:", self.output.getvalue())

    def test_readback_mismatch_is_not_success_and_not_retried(self):
        client = self.client(new=["Advancements"])
        with self.assertRaisesRegex(tags_tool.ToolError, "propagating"):
            tags_tool.synchronize(client, ITEM_ID, TAGS, True)
        client.set_tags.assert_called_once()
        self.assertNotIn("Verified:", self.output.getvalue())

    def test_concurrent_non_tag_change_is_reported(self):
        client = self.client(after=item(title=b"Someone changed the title"))
        with self.assertRaisesRegex(tags_tool.ToolError, "other remote fields"):
            tags_tool.synchronize(client, ITEM_ID, TAGS, True)

    def native_client(self):
        client = tags_tool.SteamClient(self.root, 0.001)
        client.ugc, client.utils = 1, 2
        client.api = {
            "StartItemUpdate": Mock(return_value=123),
            "SetItemTags": Mock(return_value=True),
            "SubmitItemUpdate": Mock(return_value=456),
        }
        completed = tags_tool.UpdateCompleted()
        completed.result, completed.item_id = 1, ITEM_ID
        client.wait = Mock(return_value=completed)
        return client, completed

    def test_native_update_only_sets_tags_and_has_no_change_note(self):
        client, _ = self.native_client()
        captured = []

        def capture(_ugc, _handle, array_pointer):
            array = ct.cast(array_pointer, ct.POINTER(tags_tool.StringArray)).contents
            captured.extend(array.strings[i].decode() for i in range(array.count))
            return True

        client.api["SetItemTags"].side_effect = capture
        client.set_tags(ITEM_ID, TAGS)
        self.assertEqual(captured, TAGS)
        client.api["StartItemUpdate"].assert_called_once_with(1, tags_tool.APP_ID, ITEM_ID)
        client.api["SubmitItemUpdate"].assert_called_once_with(1, 123, None)
        client.wait.assert_called_once_with(456, tags_tool.UpdateCompleted, 3404)

    def test_rejected_tags_do_not_submit(self):
        client, _ = self.native_client()
        client.api["SetItemTags"].return_value = False
        with self.assertRaisesRegex(tags_tool.ToolError, "nothing was submitted"):
            client.set_tags(ITEM_ID, TAGS)
        client.api["SubmitItemUpdate"].assert_not_called()

    def test_callback_failure_and_legal_agreement_are_not_success(self):
        for result, agreement in ((15, False), (1, True)):
            client, completed = self.native_client()
            completed.result, completed.needs_agreement = result, agreement
            with self.assertRaises(tags_tool.ToolError):
                client.set_tags(ITEM_ID, TAGS)

    def test_submission_timeout_reports_unknown_outcome(self):
        client, _ = self.native_client()
        client.wait.side_effect = tags_tool.ToolError("timed out")
        with self.assertRaisesRegex(tags_tool.ToolError, "outcome is unknown"):
            client.set_tags(ITEM_ID, TAGS)
        client.api["SubmitItemUpdate"].assert_called_once()

    def test_query_handle_is_released_on_async_failure(self):
        client, _ = self.native_client()
        client.api.update({
            "CreateQueryUGCDetailsRequest": Mock(return_value=100),
            "SetAllowCachedResponse": Mock(return_value=True),
            "SendQueryUGCRequest": Mock(return_value=200),
            "ReleaseQueryUGCRequest": Mock(),
        })
        client.wait.side_effect = tags_tool.ToolError("network failure")
        with self.assertRaises(tags_tool.ToolError):
            client.query(ITEM_ID)
        client.api["ReleaseQueryUGCRequest"].assert_called_once_with(1, 100)

    @unittest.skipUnless(sys.platform == "win32" and ct.sizeof(ct.c_void_p) == 8, "Windows x64 ABI")
    def test_sdk_153_callback_layouts(self):
        self.assertEqual(ct.sizeof(tags_tool.StringArray), 16)
        self.assertEqual(ct.sizeof(tags_tool.QueryCompleted), 280)
        self.assertEqual(ct.sizeof(tags_tool.UpdateCompleted), 16)
        self.assertEqual(tags_tool.UpdateCompleted.item_id.offset, 8)
        self.assertEqual(tags_tool.ItemDetails.owner.offset, 8160)
        self.assertEqual(ct.sizeof(tags_tool.ItemDetails), 9776)


if __name__ == "__main__":
    unittest.main()
