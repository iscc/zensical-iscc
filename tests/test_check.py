"""Configuration and built-site checks."""

from pathlib import Path

from conftest import build, edit_config

from zensical_iscc import check


def messages(findings):
    """Return the levels and the first words of each finding for compact assertions."""
    return [(level, message.split(":")[0]) for level, message in findings]


def test_external_host():
    assert check.external_host("https://unpkg.com/x.js") == "unpkg.com"
    assert check.external_host("//fonts.googleapis.com/css") == "fonts.googleapis.com"
    assert check.external_host("assets/iscc/theme.css") is None
    assert check.external_host("/assets/x.css") is None


def test_is_foreign_allows_plausible_and_chat():
    assert not check.is_foreign("https://stats.iscc.codes/js/plausible.js")
    assert not check.is_foreign("https://iscc.ai/copilot/index.js")
    assert not check.is_foreign("../assets/x.png")
    assert check.is_foreign("https://img.shields.io/badge.svg")


def test_theme_findings_for_a_correct_theme():
    assert check.theme_findings({"name": "zensical_iscc", "font": False, "features": ["toc.follow"]}) == []


def test_theme_findings_for_a_misconfigured_theme():
    theme = {"name": "material", "font": {"text": "Roboto"}, "features": ["navigation.instant"], "logo": "x.svg"}
    levels = [level for level, _ in check.theme_findings(theme)]
    assert levels == ["error", "error", "error", "warning"]


def test_theme_findings_for_palette_and_favicon():
    findings = check.theme_findings({"name": "zensical_iscc", "favicon": "f.png", "palette": []})
    assert [level for level, _ in findings] == ["warning", "warning"]


def test_custom_dir_findings_for_site_overrides(tmp_path):
    assert check.custom_dir_findings(None) == []
    (tmp_path / "recovery.html").write_text('{% extends "main.html" %}\n', encoding="utf-8")
    assert check.custom_dir_findings(tmp_path) == []


def test_custom_dir_findings_for_a_vendored_theme(tmp_path):
    (tmp_path / "assets" / "iscc").mkdir(parents=True)
    (tmp_path / "assets" / "iscc" / "theme.css").write_text("", encoding="utf-8")
    (tmp_path / "main.html").write_text("", encoding="utf-8")
    findings = check.custom_dir_findings(tmp_path)
    assert len(findings) == 1
    assert "holds a copy of the ISCC theme" in findings[0][1]


def test_custom_dir_findings_for_a_main_template(tmp_path):
    (tmp_path / "main.html").write_text('{% extends "base.html" %}\n', encoding="utf-8")
    findings = check.custom_dir_findings(tmp_path)
    assert len(findings) == 1
    assert "main.html replaces the theme's main.html" in findings[0][1]


def test_metadata_findings():
    complete = {
        "site_url": "https://x.iscc.codes/",
        "repo_url": "https://github.com/iscc/x",
        "edit_uri": "edit/main/docs/",
    }
    complete["extra"] = {"iscc": {"tagline": "X"}}
    assert check.metadata_findings(complete) == []
    findings = check.metadata_findings({"repo_url": "https://github.com/iscc/x"})
    assert messages(findings) == [
        ("warning", "set `site_url`"),
        ("warning", 'set `edit_uri` (for example "edit/main/docs/")'),
        ("warning", "set `tagline` in [project.extra.iscc]"),
    ]


def test_analytics_findings():
    site = {"site_url": "https://core.iscc.codes/"}
    plausible = {"provider": "plausible", "domain": "core.iscc.codes"}
    assert check.analytics_findings({**site, "extra": {"analytics": plausible}}) == []
    assert check.analytics_findings({"extra": {"analytics": plausible}}) == []
    assert len(check.analytics_findings(site)) == 1
    assert len(check.analytics_findings({**site, "extra": {"analytics": {"provider": "custom"}}})) == 1
    other = {"provider": "plausible", "domain": "iscc.codes"}
    findings = check.analytics_findings({**site, "extra": {"analytics": other}})
    assert findings == [("warning", "analytics domain iscc.codes differs from the site_url host core.iscc.codes")]


def test_extra_asset_findings():
    config = {
        "extra_css": ["stylesheets/custom.css", "https://fonts.googleapis.com/css2?family=Inter"],
        "extra_javascript": [{"path": "https://unpkg.com/x.js", "defer": True}, "js/local.js"],
    }
    findings = check.extra_asset_findings(config)
    assert [level for level, _ in findings] == ["error", "error"]
    assert "fonts.googleapis.com" in findings[0][1]
    assert "unpkg.com" in findings[1][1]


def test_resource_urls():
    html = """
    <link rel="stylesheet" href="https://cdn.example/a.css">
    <link rel="canonical" href="https://x.iscc.codes/">
    <link rel="alternate icon" href='assets/favicon.ico'>
    <link href="https://example.org/about">
    <script src=https://cdn.example/b.js defer></script>
    <SCRIPT>inline()</SCRIPT>
    <img alt="x" src="https://img.shields.io/c.svg">
    <a href="https://github.com/iscc">GitHub</a>
    """
    assert check.resource_urls(html) == [
        "https://cdn.example/a.css",
        "assets/favicon.ico",
        "https://cdn.example/b.js",
        "",
        "https://img.shields.io/c.svg",
    ]


def test_page_findings():
    html = '<script src="https://stats.iscc.codes/js/plausible.js"></script><img src="https://img.shields.io/x.svg">'
    assert check.page_findings("index.html", html) == [("error", "index.html loads https://img.shields.io/x.svg")]
    mermaid = '<pre class="mermaid"><code>graph LR</code></pre>'
    assert messages(check.page_findings("flow/index.html", mermaid)) == [
        ("error", "flow/index.html has a Mermaid diagram, which the Zensical bundle loads from unpkg.com")
    ]


def test_stylesheet_findings():
    css = """
    @import url("https://fonts.googleapis.com/css2?family=Inter");
    @import 'https://cdn.example/x.css';
    .a { background: url(../img/a.png); }
    .b { background: url(https://stats.iscc.codes/pixel.gif); }
    """
    assert check.stylesheet_findings("x.css", css) == [
        ("error", "x.css loads https://fonts.googleapis.com/css2?family=Inter"),
        ("error", "x.css loads https://cdn.example/x.css"),
    ]


def test_markdown_findings(tmp_path):
    sources = [Path("index.md")]
    assert len(check.markdown_findings(tmp_path, sources)) == 1
    (tmp_path / "index.md").write_text("# Home\n", encoding="utf-8")
    assert len(check.markdown_findings(tmp_path, sources)) == 1
    (tmp_path / "llms-full.txt").write_text("# Home\n", encoding="utf-8")
    assert check.markdown_findings(tmp_path, sources) == []


def test_check_before_build_reports_configuration_only(demo_config):
    assert messages(check.check(demo_config)) == [
        ("warning", "the site is not built; run `zensical-iscc build` to check its pages")
    ]


def test_check_finds_foreign_images_in_pages(demo_config):
    docs = demo_config.parent / "docs"
    (docs / "badges.md").write_text(
        "# Badges\n\n![PyPI](https://img.shields.io/pypi/v/iscc-core.svg)\n", encoding="utf-8"
    )
    build(demo_config)
    assert check.check(demo_config) == [
        ("error", "badges/index.html loads https://img.shields.io/pypi/v/iscc-core.svg")
    ]


def test_check_finds_missing_markdown_pages(demo_config):
    site = build(demo_config)
    (site / "components" / "index.md").unlink()
    assert messages(check.check(demo_config)) == [
        ("error", "Markdown pages are missing from the site; build with `zensical-iscc build`")
    ]


def test_check_finds_vendored_theme(demo_config):
    vendored = demo_config.parent / "zensical_iscc" / "assets" / "iscc"
    vendored.mkdir(parents=True)
    (vendored / "theme.css").write_text("", encoding="utf-8")
    edit_config(demo_config, 'name = "zensical_iscc"', 'custom_dir = "zensical_iscc"')
    findings = check.check(demo_config)
    assert [level for level, _ in findings][:2] == ["error", "error"]
    assert "holds a copy of the ISCC theme" in findings[1][1]
