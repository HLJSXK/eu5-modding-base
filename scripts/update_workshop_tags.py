#!/usr/bin/env python3
"""Preview, inspect, or replace an existing EU5 Workshop item's tags only.

Uses the installed game's Steam API DLL; no pip packages or API keys required.
See docs/guides/Workshop_Tags.md for usage and the verified SDK ABI sources.
"""
from __future__ import annotations

import argparse
import ctypes as ct
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
APP_ID = 3450310
INVALID_HANDLE = (1 << 64) - 1
U64, U32, I32, PTR, BOOL = ct.c_uint64, ct.c_uint32, ct.c_int32, ct.c_void_p, ct.c_bool
RESULT_NAMES = {1: "OK", 2: "Fail", 3: "NoConnection", 8: "InvalidParam",
                9: "FileNotFound", 15: "AccessDenied", 16: "Timeout",
                20: "ServiceUnavailable", 21: "NotLoggedOn", 24: "InsufficientPrivilege",
                25: "LimitExceeded", 84: "RateLimitExceeded"}


class ToolError(Exception):
    """An actionable error that should not produce a Python traceback."""


# Windows x64 Steamworks SDK 1.53 / ISteamUGC016, pack(8).
# Deliberately require these exact exported factories instead of guessing a new ABI.
class ItemDetails(ct.Structure):
    _pack_ = 8
    _fields_ = [
        ("item_id", U64), ("result", I32), ("file_type", I32),
        ("creator_app", U32), ("consumer_app", U32),
        ("title", ct.c_char * 129), ("description", ct.c_char * 8000),
        ("owner", U64), ("created", U32), ("updated", U32), ("added", U32),
        ("visibility", I32), ("banned", BOOL), ("accepted", BOOL),
        ("tags_truncated", BOOL), ("tags", ct.c_char * 1025),
        ("file_handle", U64), ("preview_handle", U64), ("filename", ct.c_char * 260),
        ("file_size", I32), ("preview_size", I32), ("url", ct.c_char * 256),
        ("votes_up", U32), ("votes_down", U32), ("score", ct.c_float), ("children", U32),
    ]


class QueryCompleted(ct.Structure):
    _pack_ = 8
    _fields_ = [("handle", U64), ("result", I32), ("count", U32),
                ("total", U32), ("cached", BOOL), ("cursor", ct.c_char * 256)]


class UpdateCompleted(ct.Structure):
    _pack_ = 8
    _fields_ = [("result", I32), ("needs_agreement", BOOL), ("item_id", U64)]


class StringArray(ct.Structure):
    _pack_ = 8
    _fields_ = [("strings", ct.POINTER(ct.c_char_p)), ("count", I32)]


def result_ok(result: int, operation: str) -> None:
    if result != 1:
        raise ToolError(f"{operation}: Steam returned {RESULT_NAMES.get(result, 'EResult')} ({result}).")


def read_tags(metadata: Path, definitions: Path) -> list[str]:
    data = json.loads(metadata.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict) or data.get("game_id") != "eu5":
        raise ToolError("Metadata must be an EU5 object with game_id = eu5.")
    tags = data.get("tags")
    if not isinstance(tags, list) or not tags:
        raise ToolError("Metadata tags must be a nonempty list; refusing to clear all categories.")
    allowed = {tag["SteamRef"] for tag in json.loads(
        definitions.read_text(encoding="utf-8-sig"))["tags"]}
    for tag in tags:
        if not isinstance(tag, str) or not tag or tag != tag.strip():
            raise ToolError("Each tag must be a nonempty string without surrounding whitespace.")
        if len(tag.encode("utf-8")) > 255 or "," in tag or not tag.isprintable():
            raise ToolError(f"Invalid Steam tag: {tag!r}")
        if tag not in allowed:
            raise ToolError(f"Unknown EU5 category {tag!r}; use the exact SteamRef spelling.")
    if len(tags) != len(set(tags)):
        raise ToolError("Duplicate tags in metadata.")
    return tags


def find_game(explicit: Path | None) -> Path:
    if explicit is not None:
        candidates = [explicit]
    elif os.environ.get("EU5_GAME_DIR"):
        candidates = [Path(os.environ["EU5_GAME_DIR"])]
    else:
        steam_roots = [Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Steam"]
        if sys.platform == "win32":
            import winreg
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
                    steam_roots.insert(0, Path(winreg.QueryValueEx(key, "SteamPath")[0]))
            except OSError:
                pass
        libraries = list(steam_roots)
        for steam in steam_roots:
            vdf = steam / "steamapps/libraryfolders.vdf"
            if vdf.is_file():
                libraries.extend(Path(p.replace("\\\\", "\\")) for p in re.findall(
                    r'"path"\s+"([^"\r\n]+)"', vdf.read_text(encoding="utf-8-sig")))
        candidates = [p / "steamapps/common/Europa Universalis V" for p in libraries]
    for candidate in candidates:
        # Accept either the install root or its game/ subdirectory.
        root = candidate.parent if candidate.name.lower() == "game" else candidate
        if (root / "binaries/steam_api64.dll").is_file():
            return root.resolve()
    raise ToolError("EU5 install not found. Use --game-dir with the Europa Universalis V install folder.")


class SteamClient:
    """Minimal, explicitly typed, tag-only Steamworks client for the installed EU5 DLL."""

    def __init__(self, game: Path, timeout: float):
        self.game, self.timeout = game, timeout
        self.initialized = False
        self.temp = self.dll_directory = None
        self.saved_cwd = None
        self.saved_env: dict[str, str | None] = {}

    def bind(self, name, restype, *argtypes):
        try:
            fn = getattr(self.dll, name)
        except AttributeError as exc:
            raise ToolError(f"Installed Steam DLL lacks {name}; its ABI needs review before use.") from exc
        fn.restype, fn.argtypes = restype, list(argtypes)
        return fn

    def __enter__(self):
        if sys.platform != "win32" or ct.sizeof(PTR) != 8:
            raise ToolError("Online operations require Windows and a 64-bit Python interpreter.")
        try:
            dll_path = self.game / "binaries/steam_api64.dll"
            self.dll_directory = os.add_dll_directory(str(dll_path.parent))
            self.dll = ct.CDLL(str(dll_path))  # Steam's flat API uses C calling conventions.
            init = self.bind("SteamAPI_Init", BOOL)
            self.shutdown = self.bind("SteamAPI_Shutdown", None)
            self.run_callbacks = self.bind("SteamAPI_RunCallbacks", None)
            ugc = self.bind("SteamAPI_SteamUGC_v016", PTR)
            utils = self.bind("SteamAPI_SteamUtils_v010", PTR)
            user = self.bind("SteamAPI_SteamUser_v021", PTR)
            # Validate all needed exports before Steam initialization or any request.
            self.api = {}
            signatures = {
                "IsAPICallCompleted": ("Utils", BOOL, U64, ct.POINTER(BOOL)),
                "GetAPICallResult": ("Utils", BOOL, U64, PTR, I32, I32, ct.POINTER(BOOL)),
                "GetAppID": ("Utils", U32), "BLoggedOn": ("User", BOOL),
                "GetSteamID": ("User", U64),
                "CreateQueryUGCDetailsRequest": ("UGC", U64, ct.POINTER(U64), U32),
                "SetAllowCachedResponse": ("UGC", BOOL, U64, U32),
                "SendQueryUGCRequest": ("UGC", U64, U64),
                "GetQueryUGCResult": ("UGC", BOOL, U64, U32, ct.POINTER(ItemDetails)),
                "GetQueryUGCNumTags": ("UGC", U32, U64, U32),
                "GetQueryUGCTag": ("UGC", BOOL, U64, U32, U32, PTR, U32),
                "ReleaseQueryUGCRequest": ("UGC", BOOL, U64),
                "StartItemUpdate": ("UGC", U64, U32, U64),
                "SetItemTags": ("UGC", BOOL, U64, ct.POINTER(StringArray)),
                "SubmitItemUpdate": ("UGC", U64, U64, ct.c_char_p),
            }
            for name, (family, restype, *args) in signatures.items():
                self.api[name] = self.bind(f"SteamAPI_ISteam{family}_{name}", restype, PTR, *args)
            self.saved_env = {key: os.environ.get(key) for key in ("SteamAppId", "SteamGameId")}
            os.environ.update(SteamAppId=str(APP_ID), SteamGameId=str(APP_ID))
            self.temp = tempfile.TemporaryDirectory(prefix="eu5-workshop-tags-")
            Path(self.temp.name, "steam_appid.txt").write_text(str(APP_ID), encoding="ascii")
            self.saved_cwd = Path.cwd()
            os.chdir(self.temp.name)
            if not init():
                raise ToolError("SteamAPI_Init failed. Start Steam, log in to the item's owner account, "
                                "and run this tool from normal PowerShell outside an agent sandbox "
                                "at the same Windows privilege level as Steam.")
            self.initialized = True
            self.ugc, self.utils, self.user = ugc(), utils(), user()
            if not all((self.ugc, self.utils, self.user)):
                raise ToolError("Steam returned a null interface.")
            if self.api["GetAppID"](self.utils) != APP_ID:
                raise ToolError("Steam initialized for a different app; no update was started.")
            if not self.api["BLoggedOn"](self.user):
                raise ToolError("Steam is offline or not logged in.")
            self.account_id = self.api["GetSteamID"](self.user)
            return self
        except BaseException:
            self.close()
            raise

    def close(self):
        if self.initialized:
            self.shutdown()
            self.initialized = False
        if self.saved_cwd is not None:
            os.chdir(self.saved_cwd)
            self.saved_cwd = None
        for key, value in self.saved_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.saved_env.clear()
        if self.temp is not None:
            self.temp.cleanup()
            self.temp = None
        if self.dll_directory is not None:
            self.dll_directory.close()
            self.dll_directory = None

    def __exit__(self, *exc):
        self.close()

    def wait(self, call: int, structure, callback: int):
        if not call:
            raise ToolError("Steam returned an invalid asynchronous call handle.")
        deadline = time.monotonic() + self.timeout
        while time.monotonic() < deadline:
            self.run_callbacks()
            failed = BOOL()
            if self.api["IsAPICallCompleted"](self.utils, call, ct.byref(failed)):
                if failed.value:
                    raise ToolError("Steam asynchronous request failed (connection or I/O error).")
                result = structure()
                ok = self.api["GetAPICallResult"](
                    self.utils, call, ct.byref(result), ct.sizeof(result), callback, ct.byref(failed))
                if not ok or failed.value:
                    raise ToolError("Cannot read Steam callback; no successful result was confirmed.")
                return result
            time.sleep(0.1)
        raise ToolError(f"Steam request timed out after {self.timeout:g} seconds.")

    def query(self, item_id: int):
        ids = (U64 * 1)(item_id)
        handle = self.api["CreateQueryUGCDetailsRequest"](self.ugc, ids, 1)
        if handle in (0, INVALID_HANDLE):
            raise ToolError("Cannot create Steam item query.")
        try:
            if not self.api["SetAllowCachedResponse"](self.ugc, handle, 0):
                raise ToolError("Cannot disable Steam's query cache.")
            result = self.wait(self.api["SendQueryUGCRequest"](self.ugc, handle), QueryCompleted, 3401)
            result_ok(result.result, "Query item")
            if result.handle != handle or result.count != 1:
                raise ToolError("Query did not return exactly the requested Workshop item.")
            details = ItemDetails()
            if not self.api["GetQueryUGCResult"](self.ugc, handle, 0, ct.byref(details)):
                raise ToolError("Cannot read Workshop item details.")
            result_ok(details.result, "Item details")
            if details.item_id != item_id:
                raise ToolError("Steam returned the wrong item ID.")
            tags = []
            for index in range(self.api["GetQueryUGCNumTags"](self.ugc, handle, 0)):
                value = ct.create_string_buffer(1024)
                if not self.api["GetQueryUGCTag"](self.ugc, handle, 0, index, value, len(value)):
                    raise ToolError("Cannot read the full Workshop tag list.")
                tags.append(value.value.decode("utf-8"))
            return details, tags
        finally:
            self.api["ReleaseQueryUGCRequest"](self.ugc, handle)

    def set_tags(self, item_id: int, tags: list[str]):
        encoded = (ct.c_char_p * len(tags))(*(tag.encode("utf-8") for tag in tags))
        values = StringArray(encoded, len(tags))
        handle = self.api["StartItemUpdate"](self.ugc, APP_ID, item_id)
        if handle in (0, INVALID_HANDLE):
            raise ToolError("Cannot start the Workshop update.")
        if not self.api["SetItemTags"](self.ugc, handle, ct.byref(values)):
            raise ToolError("Steam rejected SetItemTags; nothing was submitted.")
        # This is the ONLY submitted field. Do not add content/title/description setters.
        call = self.api["SubmitItemUpdate"](self.ugc, handle, None)
        try:
            result = self.wait(call, UpdateCompleted, 3404)
        except ToolError as exc:
            raise ToolError(f"{exc} Submission outcome is unknown; run --check before retrying --apply.") from exc
        result_ok(result.result, "Submit tags")
        if result.needs_agreement:
            raise ToolError("Steam requires the Workshop legal agreement. Review it in Steam, then --check.")
        if result.item_id != item_id:
            raise ToolError("Submission returned an unexpected item ID; inspect the page before retrying.")


def synchronize(client, item_id: int, tags: list[str], apply: bool) -> None:
    before, old_tags = client.query(item_id)
    if before.consumer_app != APP_ID:
        raise ToolError(f"Item belongs to app {before.consumer_app}, not EU5 ({APP_ID}).")
    print("Workshop title:", before.title.decode("utf-8", errors="replace"))
    print("Current tags:", ", ".join(old_tags) or "(none)")
    print("Add:", ", ".join(tag for tag in tags if tag not in old_tags) or "(none)")
    print("Remove:", ", ".join(tag for tag in old_tags if tag not in tags) or "(none)")
    is_owner = before.owner == client.account_id
    print("Logged-in account owns item:", "yes" if is_owner else "no")
    if not apply:
        print("Read-only check complete. No changes submitted.")
        return
    if not is_owner:
        raise ToolError("Refusing update: sign into the item's original owner account.")
    if set(old_tags) == set(tags):
        print("Tags already match; no update needed.")
        return
    client.set_tags(item_id, tags)
    print("Steam accepted the tag update. Reading it back...")
    try:
        after, actual = client.query(item_id)
    except ToolError as exc:
        raise ToolError(f"Update accepted, but readback failed: {exc} Use --check; do not blindly resubmit.") from exc
    if set(actual) != set(tags):
        raise ToolError(f"Update accepted, but readback is {actual!r}. It may be propagating; run --check later.")
    protected = ("title", "description", "visibility", "file_handle", "preview_handle", "owner", "consumer_app")
    if any(getattr(before, field) != getattr(after, field) for field in protected):
        raise ToolError("Tags match, but other remote fields changed during the operation; review the page.")
    print("Verified: Workshop tags match metadata; title, description, visibility and file handles are unchanged.")


def item_number(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use the numeric existing Workshop item ID.") from exc
    if not 0 < number < INVALID_HANDLE:
        raise argparse.ArgumentTypeError("Item ID must be an existing positive uint64 ID (not 0).")
    return number


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--item-id", required=True, type=item_number, help="Existing Workshop item ID")
    parser.add_argument("--metadata", required=True, type=Path,
                        help="Metadata JSON for this item; relative paths use the current directory")
    parser.add_argument("--game-dir", type=Path, help="EU5 install root (auto-detected if omitted)")
    parser.add_argument("--timeout", type=float, default=60, help="Seconds per Steam request (default: 60)")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--check", action="store_true", help="Read current Workshop tags without changing them")
    modes.add_argument("--apply", action="store_true", help="Replace remote tags and verify the result")
    args = parser.parse_args(argv)
    try:
        if not math.isfinite(args.timeout) or not 0 < args.timeout <= 300:
            raise ToolError("Timeout must be finite and between 0 and 300 seconds.")
        metadata = args.metadata.resolve()
        online = args.check or args.apply
        game = find_game(args.game_dir) if online or args.game_dir else None
        definitions = (game / "game/main_menu/create_mod_tags.json" if game else
                       ROOT / "reference_game_files/game/main_menu/create_mod_tags.json")
        tags = read_tags(metadata, definitions)
        print(f"Item: https://steamcommunity.com/sharedfiles/filedetails/?id={args.item_id}")
        print("Metadata:", metadata)
        print("Desired tags:", ", ".join(tags))
        if not online:
            print("Offline preview only. Use --check to inspect Steam or --apply to update tags.")
            return 0
        print("Steam DLL:", game / "binaries/steam_api64.dll", flush=True)
        with SteamClient(game, args.timeout) as client:
            synchronize(client, args.item_id, tags, args.apply)
        return 0
    except (ToolError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Interrupted. If submission had started, run --check before retrying.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
