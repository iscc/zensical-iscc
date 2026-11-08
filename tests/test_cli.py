"""The `zensical-iscc` command line."""

import pytest
from conftest import build, edit_config

from zensical_iscc import cli


def test_help_lists_the_commands(capsys):
    with pytest.raises(SystemExit) as exit_info:
        cli.main(["--help"])
    assert exit_info.value.code == 0
    out = capsys.readouterr().out
    for command in cli.COMMANDS:
        assert f"zensical-iscc {command}" in out


def test_missing_configuration_file(tmp_path, capsys):
    assert cli.main(["check", "--config-file", str(tmp_path / "zensical.toml")]) == 1
    assert "configuration file not found" in capsys.readouterr().err


def test_markdown_before_build(docs_config, capsys):
    assert cli.main(["markdown", "--config-file", str(docs_config)]) == 1
    assert "site directory not found" in capsys.readouterr().err


def test_markdown_after_build(docs_config, capsys):
    site = build(docs_config)
    (site / "index.md").unlink()
    assert cli.main(["markdown", "--config-file", str(docs_config)]) == 0
    assert (site / "index.md").is_file()
    pages = len(list((docs_config.parent / "docs").rglob("*.md")))
    assert f"wrote {pages} Markdown pages, llms-full.txt and llms.txt" in capsys.readouterr().out


def test_build_stops_when_zensical_fails(docs_config):
    edit_config(docs_config, 'site_name = "ISCC Theme"', "")
    assert cli.main(["build", "--config-file", str(docs_config)]) != 0
    assert not (docs_config.parent / "site" / "llms-full.txt").exists()


def test_check_passes_with_warnings_unless_strict(docs_config, capsys):
    build(docs_config)
    edit_config(docs_config, 'tagline = "Zensical theme for ISCC documentation"', "")
    assert cli.main(["check", "--config-file", str(docs_config)]) == 0
    assert cli.main(["check", "--strict", "--config-file", str(docs_config)]) == 1
    out = capsys.readouterr().out
    assert "warning: set `tagline`" in out
    assert "0 errors, 1 warnings" in out


def test_check_fails_on_errors(docs_config, capsys):
    build(docs_config)
    edit_config(docs_config, "[project.theme]", '[project.theme]\nfeatures = ["navigation.instant"]')
    assert cli.main(["check", "--config-file", str(docs_config)]) == 1
    assert "error: remove the `navigation.instant` feature" in capsys.readouterr().out
