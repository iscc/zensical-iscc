"""Product wordmark lockups: fidelity to the reference lockups, product names and the build step."""

import re
from pathlib import Path

import pytest
from conftest import build, edit_config

from zensical_iscc import check, cli, wordmark

REFERENCE_LOCKUPS = Path(__file__).parent / "fixtures" / "products"


@pytest.mark.parametrize("path", sorted(REFERENCE_LOCKUPS.glob("*.svg")), ids=lambda p: p.stem)
def test_compose_matches_the_reference_lockups(path):
    # Fixtures are reference lockups from the ISCC brand assets; refresh them together with the font.
    name, treatment = re.fullmatch(r"iscc-(.+)-(white-coral|black-coral)", path.stem).groups()
    assert wordmark.compose(name, treatment) == path.read_text(encoding="utf-8")


def test_display_size_sets_one_h_and_keeps_the_drawing():
    native, display = wordmark.compose("monitor"), wordmark.compose("monitor", display_h=30)
    assert 'width="335.69" height="39.64"' in display
    assert re.sub(r'width="[^"]*" height="[^"]*"', "", native, count=1) == re.sub(
        r'width="[^"]*" height="[^"]*"', "", display, count=1
    )


def test_compose_rejects_names_outside_the_rule():
    with pytest.raises(ValueError, match="lowercase"):
        wordmark.compose("Monitor")


def test_is_valid():
    assert wordmark.is_valid("monitor")
    assert wordmark.is_valid("c2pa-resolver")
    assert not wordmark.is_valid("iscc-hub")
    assert not wordmark.is_valid("Hub")
    assert not wordmark.is_valid("hub-")
    assert not wordmark.is_valid("")


def test_product_name_prefers_the_option_then_the_repository():
    assert wordmark.product_name({"extra": {"iscc": {"product": "hub"}}, "repo_name": "iscc/iscc-web"}) == "hub"
    assert wordmark.product_name({"repo_name": "iscc/iscc-monitor"}) == "monitor"
    assert wordmark.product_name({"repo_name": "iscc/ISCC-Search"}) == "search"
    assert wordmark.product_name({"repo_name": "iscc/zensical-iscc"}) == "zensical-iscc"
    assert wordmark.product_name({"repo_name": "iscc/iscc"}) is None
    assert wordmark.product_name({}) is None


def test_build_writes_the_header_lockup(docs_config):
    site = build(docs_config)
    svg = (site / "assets" / "iscc" / "product.svg").read_text(encoding="utf-8")
    assert 'aria-label="ISCC theme"' in svg
    assert 'fill="#FFFFFF"' in svg
    html = (site / "index.html").read_text(encoding="utf-8")
    assert 'class="iscc-product" src="./assets/iscc/product.svg"' in html
    assert 'onerror="this.remove()"' in html


def test_build_without_a_product_name_keeps_the_plain_logo(docs_config, capsys):
    edit_config(docs_config, 'product = "theme"', "")
    edit_config(docs_config, 'repo_name = "iscc/zensical-iscc"', "")
    site = build(docs_config)
    assert not (site / wordmark.OUTPUT).exists()
    assert "no product name" in capsys.readouterr().out
    findings = check.check(docs_config)
    assert ("warning", check.product_findings({})[0][1]) in findings


def test_build_fails_on_a_product_outside_the_rule(docs_config):
    edit_config(docs_config, 'product = "theme"', 'product = "ISCC Hub"')
    assert cli.main(["build", "--config-file", str(docs_config)]) == 1


def test_product_findings():
    assert check.product_findings({"repo_name": "iscc/iscc-hub"}) == []
    assert check.product_findings({})[0][0] == "warning"
    assert check.product_findings({"extra": {"iscc": {"product": "iscc-hub"}}})[0][0] == "error"


def test_check_finds_a_missing_lockup(docs_config):
    site = build(docs_config)
    (site / wordmark.OUTPUT).unlink()
    assert any("wordmark is missing" in message for _, message in check.check(docs_config))
