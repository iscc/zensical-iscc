"""The Claude Code plugin marketplace that serves the theme's agent skills."""

import json
import struct
import tomllib
from pathlib import Path

ROOT = Path(__file__).parent.parent
MARKETPLACE = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
ENTRY = MARKETPLACE["plugins"][0]
PLUGIN_ROOT = ROOT / ENTRY["source"]
MANIFEST = json.loads((PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))


def test_plugin_version_follows_the_package_version():
    # A pinned version keeps users on their cached copy until it changes, so it moves with each release.
    package = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    assert MANIFEST["version"] == package


def test_marketplace_entry_names_the_plugin_in_skills():
    assert ENTRY["source"] == "./skills"
    assert ENTRY["name"] == MANIFEST["name"] == "zensical-iscc"
    assert MANIFEST["skills"] == "./"
    assert sorted(p.parent.name for p in PLUGIN_ROOT.glob("*/SKILL.md")) == ["docs-for-agents", "iscc-docs-theme"]


def test_plugin_icon_is_a_square_png_the_directory_accepts():
    icon = (PLUGIN_ROOT / MANIFEST["icon"]).read_bytes()
    assert icon[:8] == b"\x89PNG\r\n\x1a\n"
    width, height = struct.unpack(">II", icon[16:24])
    assert width == height
    assert 512 <= width <= 2048
