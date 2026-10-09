"""Shared fixtures: a writable copy of the demo site and a helper to build it with the theme."""

import shutil
from pathlib import Path

import pytest

from zensical_iscc import cli

DEMO_DIR = Path(__file__).parent.parent / "demo"


@pytest.fixture
def demo_config(tmp_path):
    """Return the configuration path of a fresh copy of the demo site."""
    target = tmp_path / "demo"
    shutil.copytree(DEMO_DIR, target, ignore=shutil.ignore_patterns("site"))
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
