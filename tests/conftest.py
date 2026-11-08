"""Shared fixtures: a writable copy of the theme's documentation site and a helper to build it with the theme."""

import shutil
from pathlib import Path

import pytest

from zensical_iscc import cli

ROOT = Path(__file__).parent.parent


@pytest.fixture
def docs_config(tmp_path):
    """Return the configuration path of a fresh copy of the theme's documentation site."""
    target = tmp_path / "site-copy"
    shutil.copytree(ROOT / "docs", target / "docs")
    shutil.copy(ROOT / "zensical.toml", target / "zensical.toml")
    return target / "zensical.toml"


def build(config_path):
    """Build a site with `zensical-iscc build`, assert success and return its site directory."""
    assert cli.main(["build", "--config-file", str(config_path)]) == 0
    return config_path.parent / "site"


def edit_config(config_path, old, new):
    """Replace one exact snippet of a configuration file."""
    text = config_path.read_text(encoding="utf-8")
    assert old in text
    config_path.write_text(text.replace(old, new, 1), encoding="utf-8")
