"""The changelog page of the docs site is the root CHANGELOG.md with front matter, kept in sync by a git hook."""

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "sync_changelog.py"


def load_script():
    """Import the sync script, which lives outside the package."""
    spec = importlib.util.spec_from_file_location("sync_changelog", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_changelog_page_matches_changelog():
    sync = load_script()
    assert sync.TARGET.read_text(encoding="utf-8") == sync.page(sync.SOURCE.read_text(encoding="utf-8"))


def test_sync_writes_a_stale_copy_and_reports_it(tmp_path, monkeypatch):
    sync = load_script()
    monkeypatch.setattr(sync, "SOURCE", tmp_path / "CHANGELOG.md")
    monkeypatch.setattr(sync, "TARGET", tmp_path / "docs" / "changelog.md")
    monkeypatch.setattr(sync, "ROOT", tmp_path)
    sync.SOURCE.write_text("# Changelog\n", encoding="utf-8")
    sync.TARGET.parent.mkdir()
    assert sync.main() == 1
    assert sync.TARGET.read_text(encoding="utf-8") == sync.FRONT_MATTER + "# Changelog\n"
    assert sync.main() == 0
