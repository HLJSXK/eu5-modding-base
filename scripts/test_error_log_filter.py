"""Regression tests for session rotation and diagnostic suppression."""
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from types import SimpleNamespace
import unittest


FILTER_PATH = Path(__file__).resolve().parents[1] / "error_log_filter.py"
api = SimpleNamespace(**runpy.run_path(str(FILTER_PATH), run_name="filter_tests"))


class ErrorLogFilterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.started = datetime(2026, 10, 23, 17, 13, 30)

    def write(self, name, content, modified=None):
        path = self.root / name
        path.write_bytes(content.encode("utf-8"))
        stamp = (modified or self.started).timestamp()
        os.utime(path, (stamp, stamp))
        return path

    def startup(self, started=None, modified=None):
        started = started or self.started
        self.write(
            "code_revisions.log",
            f"[{started:%H:%M:%S}][jomini_game_setup.cpp:161]: game_release_tag:\n",
            modified or started,
        )

    def settings(self, **options):
        values = dict(
            source_log=self.root / "error.log",
            output_log=self.root / "filtered.log",
            vanilla_filters=self.root / "rules.txt",
            interval_seconds=1,
        )
        values.update(options)
        return api.Settings(**values)

    def test_merges_current_session_rotations_in_numeric_order(self):
        self.startup()
        self.write("error.10.log", "[17:13:31][test.cpp:1]: oldest\n")
        self.write("error.2.log", "[17:13:32][test.cpp:1]: middle\n")
        self.write("error.1.log", "[17:13:33][test.cpp:1]: newer\n")
        self.write("error.log", "[17:13:34][test.cpp:1]: current\n")
        self.write("error.11.log", "[16:00:00][test.cpp:1]: previous launch\n", self.started - timedelta(minutes=30))
        stats = api.run_once(self.settings())
        self.assertEqual(stats.source_files, ("error.10.log", "error.2.log", "error.1.log", "error.log"))
        self.assertEqual(stats.source_entries, 4)
        self.assertNotIn("previous launch", (self.root / "filtered.log").read_text())

    def test_restarted_game_discards_previous_launch_rotations(self):
        self.startup()
        self.write("error.1.log", "[17:13:31][test.cpp:1]: first launch\n")
        self.write("error.log", "[17:13:32][test.cpp:1]: first tail\n")
        api.run_once(self.settings())
        restarted = self.started + timedelta(hours=1)
        self.startup(restarted)
        self.write("error.log", "[18:13:31][test.cpp:1]: second launch\n", restarted + timedelta(seconds=1))
        stats = api.run_once(self.settings())
        self.assertEqual(stats.source_files, ("error.log",))
        self.assertEqual(stats.source_entries, 1)
        self.assertNotIn("first launch", (self.root / "filtered.log").read_text())

    def test_midnight_with_buffered_startup_log(self):
        started = datetime(2026, 10, 23, 23, 59, 30)
        after_midnight = started + timedelta(minutes=2)
        self.startup(started, after_midnight)
        self.write("error.2.log", "[23:58:00][test.cpp:1]: old\n", started - timedelta(minutes=1))
        self.write("error.1.log", "[23:59:31][test.cpp:1]: before midnight\n", started + timedelta(seconds=1))
        self.write("error.log", "[00:01:30][test.cpp:1]: after midnight\n", after_midnight)
        stats = api.run_once(self.settings())
        self.assertEqual(stats.source_files, ("error.1.log", "error.log"))
        self.assertEqual(stats.source_entries, 2)

    def test_without_startup_marker_includes_available_rotations(self):
        self.write("custom.1.log", "[17:13:31][test.cpp:1]: rotated\n")
        self.write("custom.log", "[17:13:32][test.cpp:1]: current\n")
        paths = api.source_log_paths(self.settings(source_log=self.root / "custom.log"))
        self.assertEqual([path.name for path in paths], ["custom.1.log", "custom.log"])

    def test_current_only_does_not_read_rotations(self):
        self.write("error.1.log", "[17:13:31][test.cpp:1]: rotated\n")
        self.write("error.log", "[17:13:32][test.cpp:1]: current\n")
        stats = api.run_once(self.settings(include_rotated_logs=False))
        self.assertEqual(stats.source_files, ("error.log",))
        self.assertEqual(stats.source_entries, 1)

    def test_multiline_entry_split_across_rotation_and_duplicate(self):
        self.startup()
        header = "[17:13:31][jomini_script_system.cpp:256]: Script system error!\n"
        body = "  Error: Invalid object 'tv_missing'\n  Script location: effects/tv_test.txt:1\n\n"
        self.write("error.1.log", header)
        self.write("error.log", body + header.replace("17:13:31", "17:13:32") + body)
        stats = api.run_once(self.settings())
        self.assertEqual(stats.source_entries, 2)
        self.assertEqual(stats.duplicate_entries_removed, 1)
        self.assertEqual((self.root / "filtered.log").read_text(), header + body)
        self.assertFalse(api.run_once(self.settings()).output_changed)

    def test_mod_diagnostics_survive_broad_engine_and_file_rules(self):
        rules = [
            api.FilterRule("contains", "[jomini_script_system.cpp:256]:", 1),
            api.FilterRule("contains", "[jomini_effect.cpp:141]:", 2),
            api.FilterRule("contains", "events/DHE/flavor_MOS.txt", 3),
            api.FilterRule("regex", "Unknown loc key .*", 4, re.compile("Unknown loc key .*")),
        ]
        protected = (
            "[jomini_script_system.cpp:256]: Invalid object tv_wonder_display_1_local_level_1",
            "[jomini_effect.cpp:141]: PostValidate failed at tv_wonder_effects.txt:1",
            "[test.cpp:1]: tv_wonder error at events/DHE/flavor_MOS.txt:9",
            "[test.cpp:1]: Unknown loc key TV_WONDER_TOOLTIP",
        )
        for key in protected:
            with self.subTest(key=key):
                self.assertTrue(api.is_vanilla_filtered(key, rules))
                self.assertFalse(api.is_vanilla_filtered(key, rules, ("tv_",)))
        self.assertTrue(api.is_vanilla_filtered("[jomini_script_system.cpp:256]: vanilla issue", rules, ("tv_",)))

    def test_exact_rule_can_explicitly_suppress_protected_diagnostic(self):
        key = "[test.cpp:1]: Known warning in tv_test.txt"
        rules = [api.FilterRule("contains", "[test.cpp:1]:", 1), api.FilterRule("exact", key, 2)]
        self.assertTrue(api.is_vanilla_filtered(key, rules, ("tv_",)))

    def test_crlf_multiline_matches_lf_rule_and_deduplicates(self):
        entry = "[17:13:31][test.cpp:1]: Script error!\n  Error: known vanilla issue\n"
        crlf = entry.replace("\n", "\r\n")
        self.assertEqual(api.match_key(entry), api.match_key(crlf))
        rules = [api.FilterRule("exact", api.match_key(entry), 1)]
        kept, duplicates, filtered = api.filter_entries([crlf, entry], rules)
        self.assertEqual((kept, duplicates, filtered), ([], 1, 1))

    def test_configuration_and_cli_once(self):
        self.startup()
        self.write("error.1.log", "[17:13:31][test.cpp:1]: TV_hidden_before_fix\n")
        self.write("error.log", "[17:13:32][test.cpp:1]: vanilla issue\n")
        self.write("rules.txt", "contains:[test.cpp:1]:\n")
        config = self.write("config.json", json.dumps({
            "source_log": "error.log", "output_log": "filtered.log",
            "vanilla_filters": "rules.txt", "include_rotated_logs": True,
            "protected_markers": ["tv_"],
        }))
        result = subprocess.run([sys.executable, "-B", str(FILTER_PATH), "--config", str(config), "--once"], capture_output=True, text=True, check=True)
        self.assertIn("sources=error.1.log,error.log", result.stdout)
        self.assertIn("TV_hidden_before_fix", (self.root / "filtered.log").read_text())
        self.assertNotIn("vanilla issue", (self.root / "filtered.log").read_text())
        args = api.build_parser().parse_args(["--config", str(config), "--current-only"])
        self.assertFalse(api.load_settings(args).include_rotated_logs)

    def test_invalid_protection_configuration_is_rejected(self):
        for invalid in ["tv_", [""], [False]]:
            with self.subTest(value=invalid):
                config = self.write("config.json", json.dumps({"protected_markers": invalid}))
                args = api.build_parser().parse_args(["--config", str(config)])
                with self.assertRaisesRegex(ValueError, "protected_markers"):
                    api.load_settings(args)


if __name__ == "__main__":
    unittest.main()
