"""
Utilities for detecting and managing Steam games on the local system.
Parses Steam's libraryfolders.vdf and appmanifest files to find installed games.
"""

import os
import re
import struct
import winreg
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class SteamGame:
    """Represents an installed Steam game."""
    app_id: str
    name: str
    install_dir: str
    size_on_disk: int = 0
    last_played: int = 0
    header_image_url: str = ""
    capsule_image_url: str = ""
    library_hero_url: str = ""

    def __post_init__(self):
        self.header_image_url = (
            f"https://cdn.akamai.steamstatic.com/steam/apps/{self.app_id}/header.jpg"
        )
        self.capsule_image_url = (
            f"https://cdn.akamai.steamstatic.com/steam/apps/{self.app_id}/library_600x900_2x.jpg"
        )
        self.library_hero_url = (
            f"https://cdn.akamai.steamstatic.com/steam/apps/{self.app_id}/library_hero.jpg"
        )


def find_steam_install_path() -> Optional[str]:
    """Find Steam installation path from the Windows registry."""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam")
        path, _ = winreg.QueryValueEx(key, "InstallPath")
        winreg.CloseKey(key)
        return path
    except FileNotFoundError:
        pass

    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam")
        path, _ = winreg.QueryValueEx(key, "InstallPath")
        winreg.CloseKey(key)
        return path
    except FileNotFoundError:
        pass

    # Fallback: common paths
    common_paths = [
        r"C:\Program Files (x86)\Steam",
        r"C:\Program Files\Steam",
        os.path.expanduser(r"~\Steam"),
    ]
    for p in common_paths:
        if os.path.isdir(p):
            return p

    return None


def parse_vdf_text(text: str) -> dict:
    """
    Simple VDF (Valve Data Format) text parser.
    Returns a nested dict representation.
    """
    result = {}
    stack = [result]
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1

        if not line or line.startswith("//"):
            continue

        if line == "{":
            continue
        if line == "}":
            if len(stack) > 1:
                stack.pop()
            continue

        # Match key-value pairs: "key"  "value"
        kv_match = re.match(r'"([^"]*)"[\s\t]+"([^"]*)"', line)
        if kv_match:
            key, value = kv_match.groups()
            stack[-1][key] = value
            continue

        # Match section start: "key" \n {
        section_match = re.match(r'"([^"]*)"', line)
        if section_match:
            key = section_match.group(1)
            new_dict = {}
            stack[-1][key] = new_dict
            stack.append(new_dict)
            continue

    return result


def get_library_folders(steam_path: str) -> list[str]:
    """Get all Steam library folders from libraryfolders.vdf."""
    vdf_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
    if not os.path.isfile(vdf_path):
        # Try alternate path
        vdf_path = os.path.join(steam_path, "config", "libraryfolders.vdf")
        if not os.path.isfile(vdf_path):
            return [os.path.join(steam_path, "steamapps")]

    try:
        with open(vdf_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return [os.path.join(steam_path, "steamapps")]

    data = parse_vdf_text(content)
    folders = []

    # Navigate the parsed structure
    lib_folders = data.get("libraryfolders", data.get("LibraryFolders", {}))
    for key, value in lib_folders.items():
        if isinstance(value, dict) and "path" in value:
            folder_path = value["path"]
            steamapps_path = os.path.join(folder_path, "steamapps")
            if os.path.isdir(steamapps_path):
                folders.append(steamapps_path)
        elif isinstance(value, str) and os.path.isdir(value):
            steamapps_path = os.path.join(value, "steamapps")
            if os.path.isdir(steamapps_path):
                folders.append(steamapps_path)

    if not folders:
        default = os.path.join(steam_path, "steamapps")
        if os.path.isdir(default):
            folders.append(default)

    return folders


def parse_acf_file(filepath: str) -> dict:
    """Parse a .acf manifest file (VDF format)."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return parse_vdf_text(content)
    except Exception:
        return {}


# Blacklisted app IDs (tools, redistributables, etc.)
BLACKLISTED_APPS = {
    "228980",   # Steamworks Common Redistributables
    "1070560",  # Steam Linux Runtime
    "1391110",  # Steam Linux Runtime - Soldier
    "1628350",  # Steam Linux Runtime - Sniper
    "250820",   # SteamVR
}


def discover_installed_games(steam_path: Optional[str] = None) -> list[SteamGame]:
    """Discover all installed Steam games on the system."""
    if steam_path is None:
        steam_path = find_steam_install_path()

    if steam_path is None:
        return []

    library_folders = get_library_folders(steam_path)
    games = []
    seen_ids = set()

    for folder in library_folders:
        if not os.path.isdir(folder):
            continue

        for filename in os.listdir(folder):
            if not filename.startswith("appmanifest_") or not filename.endswith(".acf"):
                continue

            filepath = os.path.join(folder, filename)
            data = parse_acf_file(filepath)
            app_state = data.get("AppState", {})

            app_id = app_state.get("appid", "")
            name = app_state.get("name", "")
            install_dir = app_state.get("installdir", "")

            if not app_id or not name or app_id in BLACKLISTED_APPS:
                continue

            if app_id in seen_ids:
                continue
            seen_ids.add(app_id)

            size = int(app_state.get("SizeOnDisk", 0))
            last_played = int(app_state.get("LastPlayed", 0))

            games.append(SteamGame(
                app_id=app_id,
                name=name,
                install_dir=install_dir,
                size_on_disk=size,
                last_played=last_played,
            ))

    # Sort by name
    games.sort(key=lambda g: g.name.lower())
    return games


def launch_steam_game(app_id: str):
    """Launch a Steam game by its app ID."""
    os.startfile(f"steam://rungameid/{app_id}")


def format_size(size_bytes: int) -> str:
    """Format bytes into human-readable size."""
    if size_bytes <= 0:
        return "—"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"
