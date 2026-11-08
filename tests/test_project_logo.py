"""Project logos: fidelity to the reference logos, project names and the build step."""

import re
from pathlib import Path

import pytest
from conftest import build, edit_config

from zensical_iscc import check, cli, project_logo

REFERENCE_LOGOS = Path(__file__).parent / "fixtures" / "project-logos"


@pytest.mark.parametrize("path", sorted(REFERENCE_LOGOS.glob("*.svg")), ids=lambda p: p.stem)
def test_compose_matches_the_reference_logos(path):
    # Fixtures are reference logos from the ISCC brand assets; refresh them together with the font.
    name, treatment = re.fullmatch(r"iscc-(.+)-(white-coral|black-coral)", path.stem).groups()
    assert project_logo.compose(name, treatment) == path.read_text(encoding="utf-8")


def test_display_size_sets_one_h_and_keeps_the_drawing():
    native, display = project_logo.compose("monitor"), project_logo.compose("monitor", display_h=30)
    assert 'width="335.69" height="39.64"' in display
    assert re.sub(r'width="[^"]*" height="[^"]*"', "", native, count=1) == re.sub(
        r'width="[^"]*" height="[^"]*"', "", display, count=1
    )


def test_compose_rejects_names_outside_the_rule():
    with pytest.raises(ValueError, match="lowercase"):
        project_logo.compose("Monitor")


def test_is_valid():
    assert project_logo.is_valid("monitor")
    assert project_logo.is_valid("c2pa-resolver")
    assert not project_logo.is_valid("iscc-hub")
    assert not project_logo.is_valid("Hub")
    assert not project_logo.is_valid("hub-")
    assert not project_logo.is_valid("")


def test_project_name_prefers_the_option_then_the_repository():
    assert project_logo.project_name({"extra": {"iscc": {"project": "hub"}}, "repo_name": "iscc/iscc-web"}) == "hub"
    assert project_logo.project_name({"repo_name": "iscc/iscc-monitor"}) == "monitor"
    assert project_logo.project_name({"repo_name": "iscc/ISCC-Search"}) == "search"
    assert project_logo.project_name({"repo_name": "iscc/zensical-iscc"}) == "zensical-iscc"
    assert project_logo.project_name({"repo_name": "iscc/iscc"}) is None
    assert project_logo.project_name({}) is None


def test_build_writes_the_project_logo(docs_config):
    site = build(docs_config)
    svg = (site / "assets" / "iscc" / "project-logo.svg").read_text(encoding="utf-8")
    assert 'aria-label="ISCC theme"' in svg
    assert 'fill="#FFFFFF"' in svg
    html = (site / "index.html").read_text(encoding="utf-8")
    assert 'class="iscc-project-logo" src="./assets/iscc/project-logo.svg"' in html
    assert 'onerror="this.remove()"' in html


def test_build_without_a_project_name_keeps_the_plain_logo(docs_config, capsys):
    edit_config(docs_config, 'project = "theme"', "")
    edit_config(docs_config, 'repo_name = "iscc/zensical-iscc"', "")
    site = build(docs_config)
    assert not (site / project_logo.OUTPUT).exists()
    assert "no project name" in capsys.readouterr().out
    findings = check.check(docs_config)
    assert ("warning", check.project_name_findings({})[0][1]) in findings


def test_build_fails_on_a_project_name_outside_the_rule(docs_config):
    edit_config(docs_config, 'project = "theme"', 'project = "ISCC Hub"')
    assert cli.main(["build", "--config-file", str(docs_config)]) == 1


def test_project_name_findings():
    assert check.project_name_findings({"repo_name": "iscc/iscc-hub"}) == []
    assert check.project_name_findings({})[0][0] == "warning"
    assert check.project_name_findings({"extra": {"iscc": {"project": "iscc-hub"}}})[0][0] == "error"


def test_check_finds_a_missing_project_logo(docs_config):
    site = build(docs_config)
    (site / project_logo.OUTPUT).unlink()
    assert any("project logo is missing" in message for _, message in check.check(docs_config))
