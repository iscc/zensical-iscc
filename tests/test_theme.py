"""The installed theme as Zensical sees it: discovery, built pages, options and site overrides."""

import re
from pathlib import Path

import zensical_ui
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


def test_docs_home_page(docs_config):
    html = (build(docs_config) / "index.html").read_text(encoding="utf-8")
    assert "<title>ISCC Theme - Zensical theme for ISCC documentation</title>" in html
    assert "assets/iscc/theme.css" in html
    assert "assets/iscc/tokens/iscc.css" in html
    assert "iscc-logo--light" in html
    assert "iscc-logo--dark" in html
    assert 'content="https://theme.iscc.codes/assets/iscc/social-share.png"' in html
    assert 'data-domain="theme.iscc.codes" src="https://stats.iscc.codes/js/plausible.js"' in html
    assert "assets/iscc/copypage.js" in html
    assert "iscc.ai/copilot" not in html
    assert "glightbox" not in html


def test_docs_inner_page_title(docs_config):
    html = (build(docs_config) / "components" / "index.html").read_text(encoding="utf-8")
    assert "<title>Components - ISCC Theme</title>" in html


def test_pages_link_their_markdown_copy_but_the_404_page_does_not(docs_config):
    site = build(docs_config)
    link = '<link rel="alternate" type="text/markdown" href="./index.md">'
    assert link in (site / "index.html").read_text(encoding="utf-8")
    assert link in (site / "components" / "index.html").read_text(encoding="utf-8")
    assert "text/markdown" not in (site / "404.html").read_text(encoding="utf-8")


def test_docs_site_publishes_the_changelog_and_its_domain(docs_config):
    site = build(docs_config)
    assert (site / "changelog" / "index.md").read_text(encoding="utf-8").startswith("# Changelog\n")
    assert (site / "CNAME").read_text(encoding="utf-8").strip() == "theme.iscc.codes"


def test_front_matter_icons_in_navigation(docs_config):
    html = (build(docs_config) / "components" / "index.html").read_text(encoding="utf-8")
    nav = html[html.index("md-nav--primary") : html.index("md-nav--secondary")]
    assert 'class="lucide lucide-house"' in nav
    assert 'class="lucide lucide-layout-grid"' in nav


def template_body(path):
    """Return a template without its leading comment block."""
    return re.sub(r"\A\{#-.*?-#\}\n", "", path.read_text(encoding="utf-8"), count=1, flags=re.DOTALL)


def test_header_is_zensicals_plus_the_projects_menu():
    upstream = template_body(Path(zensical_ui.__file__).parent / "templates" / "partials" / "header.html")
    ours = template_body(THEME_DIR / "partials" / "header.html")
    include = '    {% include "partials/projects.html" %}\n'
    assert ours.count(include) == 1
    assert ours.replace(include, "") == upstream


def test_docs_header_lists_related_projects(docs_config):
    html = (build(docs_config) / "components" / "index.html").read_text(encoding="utf-8")
    menu = html[html.index('class="md-header__option iscc-projects"') : html.index('data-md-component="palette"')]
    assert 'aria-label="Related projects"' in menu
    assert ">Projects</span>" in menu
    assert menu.count('class="md-select__link iscc-projects__link"') == 5
    assert '<span class="iscc-projects__name">ISCC Search</span>' in menu
    assert '<span class="iscc-projects__description">Similarity search engine for ISCC codes</span>' in menu
    assert menu.count("aria-current") == 1
    assert (
        '<a href="https://theme.iscc.codes/" class="md-select__link iscc-projects__link" aria-current="true">' in menu
    )


def test_no_projects_menu_without_related_projects(docs_config):
    text = docs_config.read_text(encoding="utf-8")
    text = re.sub(r"\[\[project\.extra\.iscc\.related\]\][^\[]*", "", text)
    docs_config.write_text(text, encoding="utf-8")
    html = (build(docs_config) / "index.html").read_text(encoding="utf-8")
    assert "iscc-projects" not in html


def test_no_current_site_marker_without_site_url(docs_config):
    edit_config(docs_config, 'site_url = "https://theme.iscc.codes/"', "")
    html = (build(docs_config) / "index.html").read_text(encoding="utf-8")
    assert html.count('class="md-select__link iscc-projects__link"') == 5
    assert "aria-current" not in html


def test_docs_site_ships_theme_assets_but_no_python(docs_config):
    site = build(docs_config)
    assert (site / "assets" / "iscc" / "theme.css").is_file()
    assert (site / "assets" / "iscc" / "fonts" / "readex-pro-400.woff2").is_file()
    assert (site / "assets" / "iscc" / "favicon.svg").is_file()
    assert (site / "assets" / "iscc" / "grain.png").is_file()
    assert not list(site.rglob("*.py"))


def test_docs_site_passes_strict_check(docs_config):
    build(docs_config)
    assert cli.main(["check", "--strict", "--config-file", str(docs_config)]) == 0


def test_lightbox_pages_load_the_vendored_glightbox(docs_config):
    docs = docs_config.parent / "docs"
    (docs / "gallery.md").write_text(
        '# Gallery\n\n<a class="glightbox" href="../assets/iscc/social-share.png">Card</a>\n', encoding="utf-8"
    )
    site = build(docs_config)
    gallery = (site / "gallery" / "index.html").read_text(encoding="utf-8")
    assert "assets/iscc/vendor/glightbox/glightbox.min.js" in gallery
    assert "assets/iscc/vendor/glightbox/glightbox.min.css" in gallery
    assert "glightbox" not in (site / "index.html").read_text(encoding="utf-8")


def test_chat_on_and_copy_page_off(docs_config):
    edit_config(docs_config, "copy_page = true", "copy_page = false")
    edit_config(docs_config, "chat = false", "chat = true")
    html = (build(docs_config) / "index.html").read_text(encoding="utf-8")
    assert "assets/iscc/copypage.js" not in html
    assert "https://iscc.ai/copilot/index.js" in html
    assert "assets/iscc/copilot.js" in html


def test_site_override_on_top_of_theme(docs_config):
    overrides = docs_config.parent / "overrides" / "partials"
    overrides.mkdir(parents=True)
    (overrides / "logo.html").write_text('<img src="site-logo.svg" alt="Site">\n', encoding="utf-8")
    edit_config(docs_config, 'name = "zensical_iscc"', 'name = "zensical_iscc"\ncustom_dir = "overrides"')
    site = build(docs_config)
    html = (site / "index.html").read_text(encoding="utf-8")
    assert 'src="site-logo.svg"' in html
    assert "iscc-logo--light" not in html
    assert "assets/iscc/theme.css" in html
    assert (site / "assets" / "iscc" / "theme.css").is_file()


def test_front_matter_location_redirects(docs_config):
    docs = docs_config.parent / "docs"
    (docs / "moved.md").write_text("---\nlocation: ../components/\n---\n\n# Moved\n", encoding="utf-8")
    html = (build(docs_config) / "moved" / "index.html").read_text(encoding="utf-8")
    assert '<meta http-equiv="refresh" content="0;url=../components/">' in html


def test_analytics_domain_override(docs_config):
    edit_config(docs_config, "[project.theme]", '[project.extra.analytics]\ndomain = "iscc.codes"\n\n[project.theme]')
    html = (build(docs_config) / "index.html").read_text(encoding="utf-8")
    assert 'data-domain="iscc.codes" src="https://stats.iscc.codes/js/plausible.js"' in html


def test_no_analytics_without_site_url(docs_config):
    edit_config(docs_config, 'site_url = "https://theme.iscc.codes/"', "")
    html = (build(docs_config) / "index.html").read_text(encoding="utf-8")
    assert "data-domain" not in html
    assert "plausible.js" not in html


def test_root_size_holds_and_primary_button_is_a_near_black_block():
    css = (THEME_DIR / "assets" / "iscc" / "theme.css").read_text(encoding="utf-8")
    assert "html {\n  font-size: 125%;\n}" in css
    assert "--iscc-btn-block: var(--iscc-ink);" in css


def test_footer_links_outweigh_zensicals_footer_link_rule():
    # Zensical colours them with `a:not(:focus, :hover)`; a plain `a` selector loses to it.
    css = (THEME_DIR / "assets" / "iscc" / "theme.css").read_text(encoding="utf-8")
    assert "html .md-footer-meta.md-typeset a:not(:focus, :hover) {\n  color: var(--md-footer-fg-color);" in css


def test_header_overrides_spare_the_drawer_and_reach_the_magnifier():
    css = (THEME_DIR / "assets" / "iscc" / "theme.css").read_text(encoding="utf-8")
    # The phone drawer keeps Zensical's offset; only sidebars beside the content move below the bar.
    assert ":root {\n  --iscc-header-height: 3.2rem;\n}" in css
    assert "\n.md-sidebar {\n  top:" not in css
    # Zensical shows drawer logos with `.md-nav .md-nav__title[for=__drawer] .md-logo img`.
    assert '.md-nav .md-nav__title[for="__drawer"] .md-logo img.iscc-product {\n  display: none;' in css
    assert ".md-search__button::before {\n  background-color: currentColor;" in css


def test_page_components_are_styled_by_the_theme(docs_config):
    css = (THEME_DIR / "assets" / "iscc" / "theme.css").read_text(encoding="utf-8")
    for selector in (
        ".md-typeset .iscc-lead",
        ".iscc-cards",
        ".md-typeset .iscc-card",
        ".md-typeset .iscc-btn--primary",
    ):
        assert selector in css
    html = (build(docs_config) / "components" / "index.html").read_text(encoding="utf-8")
    assert 'class="iscc-lead"' in html
    assert 'class="iscc-btn iscc-btn--primary"' in html
    assert html.count('class="iscc-card"') == 3


def test_projects_menu_spans_the_phone_screen():
    css = (THEME_DIR / "assets" / "iscc" / "theme.css").read_text(encoding="utf-8")
    assert ".iscc-projects__link[aria-current] {\n  box-shadow: inset 2px 0 0 var(--iscc-coral);" in css
    phone = css[css.index("@media screen and (max-width: 44.9375em) {\n  .iscc-projects .md-select {") :]
    assert "position: fixed;\n    top: var(--iscc-header-height);\n    left: 0.8rem;\n    right: 0.8rem;" in phone


def test_narrow_header_fits_a_320px_screen():
    # Logo, menu button, scheme toggle and search need 332px with Zensical's margins, 376px with Projects.
    css = (THEME_DIR / "assets" / "iscc" / "theme.css").read_text(encoding="utf-8")
    narrow = css[css.index("@media screen and (max-width: 23.4375em) {") :]
    rule = ".md-header__button,\n  .md-header__title {\n    margin-left: 0;\n    margin-right: 0;"
    assert narrow.index(rule) < narrow.index("}")
