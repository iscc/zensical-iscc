"""The installed theme as Zensical sees it: discovery, built pages, options and site overrides."""

from conftest import build, edit_config
from zensical import config as zensical_config

from zensical_iscc import THEME_DIR, cli


def test_entry_point_resolves_to_theme_dir():
    assert zensical_config.get_theme_dir("zensical_iscc") == str(THEME_DIR)


def test_theme_dir_holds_no_python():
    # Zensical copies every non-template file of the theme directory into the site.
    assert not [p for p in THEME_DIR.rglob("*") if p.suffix in {".py", ".pyc"} or p.name == "__pycache__"]


def test_theme_extends_zensical_material():
    text = (THEME_DIR / "mkdocs_theme.yml").read_text(encoding="utf-8")
    assert "extends: material" in text
    assert "font: false" in text


def test_demo_home_page(demo_config):
    html = (build(demo_config) / "index.html").read_text(encoding="utf-8")
    assert "<title>ISCC Theme Demo - Zensical theme for ISCC documentation</title>" in html
    assert "assets/iscc/theme.css" in html
    assert "assets/iscc/tokens/iscc.css" in html
    assert "iscc-logo--light" in html
    assert "iscc-logo--dark" in html
    assert 'content="https://example.iscc.codes/assets/iscc/social-share.png"' in html
    assert 'data-domain="example.iscc.codes" src="https://stats.iscc.codes/js/plausible.js"' in html
    assert "assets/iscc/copypage.js" in html
    assert "iscc.ai/copilot" not in html
    assert "glightbox" not in html


def test_demo_inner_page_title(demo_config):
    html = (build(demo_config) / "components" / "index.html").read_text(encoding="utf-8")
    assert "<title>Components - ISCC Theme Demo</title>" in html


def test_demo_site_ships_theme_assets_but_no_python(demo_config):
    site = build(demo_config)
    assert (site / "assets" / "iscc" / "theme.css").is_file()
    assert (site / "assets" / "iscc" / "fonts" / "readex-pro-400.woff2").is_file()
    assert (site / "assets" / "iscc" / "favicon.svg").is_file()
    assert not list(site.rglob("*.py"))


def test_demo_site_passes_strict_check(demo_config):
    build(demo_config)
    assert cli.main(["check", "--strict", "--config-file", str(demo_config)]) == 0


def test_lightbox_pages_load_the_vendored_glightbox(demo_config):
    docs = demo_config.parent / "docs"
    (docs / "gallery.md").write_text(
        '# Gallery\n\n<a class="glightbox" href="../assets/iscc/social-share.png">Card</a>\n', encoding="utf-8"
    )
    site = build(demo_config)
    gallery = (site / "gallery" / "index.html").read_text(encoding="utf-8")
    assert "assets/iscc/vendor/glightbox/glightbox.min.js" in gallery
    assert "assets/iscc/vendor/glightbox/glightbox.min.css" in gallery
    assert "glightbox" not in (site / "index.html").read_text(encoding="utf-8")


def test_chat_on_and_copy_page_off(demo_config):
    edit_config(demo_config, "copy_page = true", "copy_page = false")
    edit_config(demo_config, "chat = false", "chat = true")
    html = (build(demo_config) / "index.html").read_text(encoding="utf-8")
    assert "assets/iscc/copypage.js" not in html
    assert "https://iscc.ai/copilot/index.js" in html
    assert "assets/iscc/copilot.js" in html


def test_site_override_on_top_of_theme(demo_config):
    overrides = demo_config.parent / "overrides" / "partials"
    overrides.mkdir(parents=True)
    (overrides / "logo.html").write_text('<img src="site-logo.svg" alt="Site">\n', encoding="utf-8")
    edit_config(demo_config, 'name = "zensical_iscc"', 'name = "zensical_iscc"\ncustom_dir = "overrides"')
    site = build(demo_config)
    html = (site / "index.html").read_text(encoding="utf-8")
    assert 'src="site-logo.svg"' in html
    assert "iscc-logo--light" not in html
    assert "assets/iscc/theme.css" in html
    assert (site / "assets" / "iscc" / "theme.css").is_file()


def test_front_matter_location_redirects(demo_config):
    docs = demo_config.parent / "docs"
    (docs / "moved.md").write_text("---\nlocation: ../components/\n---\n\n# Moved\n", encoding="utf-8")
    html = (build(demo_config) / "moved" / "index.html").read_text(encoding="utf-8")
    assert '<meta http-equiv="refresh" content="0;url=../components/">' in html


def test_analytics_domain_override(demo_config):
    edit_config(demo_config, "[project.theme]", '[project.extra.analytics]\ndomain = "iscc.codes"\n\n[project.theme]')
    html = (build(demo_config) / "index.html").read_text(encoding="utf-8")
    assert 'data-domain="iscc.codes" src="https://stats.iscc.codes/js/plausible.js"' in html


def test_no_analytics_without_site_url(demo_config):
    edit_config(demo_config, 'site_url = "https://example.iscc.codes/"', "")
    html = (build(demo_config) / "index.html").read_text(encoding="utf-8")
    assert "data-domain" not in html
    assert "plausible.js" not in html


def test_page_components_are_styled_by_the_theme(demo_config):
    css = (THEME_DIR / "assets" / "iscc" / "theme.css").read_text(encoding="utf-8")
    for selector in (
        ".md-typeset .iscc-lead",
        ".iscc-cards",
        ".md-typeset .iscc-card",
        ".md-typeset .iscc-btn--primary",
    ):
        assert selector in css
    html = (build(demo_config) / "components" / "index.html").read_text(encoding="utf-8")
    assert 'class="iscc-lead"' in html
    assert 'class="iscc-btn iscc-btn--primary"' in html
    assert html.count('class="iscc-card"') == 3
