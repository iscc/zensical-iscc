"""Markdown copies of the pages and `llms-full.txt` beside the rendered site."""

from pathlib import Path

from conftest import build

from zensical_iscc import markdown


def test_flatten_nav_follows_sections_in_order():
    nav = [
        {"Home": "index.md"},
        {"Guide": ["guide/index.md", {"Setup": "guide/setup.md"}]},
        "about.md",
        {"GitHub": "https://github.com/iscc"},
    ]
    assert markdown.flatten_nav(nav) == [
        "index.md",
        "guide/index.md",
        "guide/setup.md",
        "about.md",
        "https://github.com/iscc",
    ]


def test_page_sources_skip_the_override_directory(tmp_path):
    for name in ("index.md", "guide/setup.md", "overrides/README.md"):
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text("# Page\n", encoding="utf-8")
    assert markdown.page_sources(tmp_path, tmp_path / "overrides") == [Path("guide/setup.md"), Path("index.md")]
    assert len(markdown.page_sources(tmp_path, None)) == 3


def test_output_path_uses_directory_urls(tmp_path):
    assert markdown.output_path(tmp_path, Path("index.md")) == tmp_path / "index.md"
    assert markdown.output_path(tmp_path, Path("guide/index.md")) == tmp_path / "guide" / "index.md"
    assert markdown.output_path(tmp_path, Path("guide/setup.md")) == tmp_path / "guide" / "setup" / "index.md"


def test_clean_markdown_strips_front_matter():
    assert markdown.clean_markdown("---\ntitle: X\n---\n\n# X\n\n") == "# X\n"
    assert markdown.clean_markdown("---\r\ntitle: X\r\n---\r\n# X") == "# X\n"
    assert markdown.clean_markdown("# X\n\n---\n") == "# X\n\n---\n"


def test_ordered_sources_put_unlisted_pages_last():
    sources = [Path("a.md"), Path("b.md"), Path("index.md")]
    nav = [{"Home": "index.md"}, {"B": "b.md"}, {"Gone": "gone.md"}]
    assert markdown.ordered_sources(sources, nav) == [Path("index.md"), Path("b.md"), Path("a.md")]


def test_build_publishes_markdown_pages(demo_config):
    site = build(demo_config)
    home = (site / "index.md").read_text(encoding="utf-8")
    components = (site / "components" / "index.md").read_text(encoding="utf-8")
    assert home.startswith("# ISCC Theme Demo\n")
    assert components.startswith("# Components\n")
    full = (site / "llms-full.txt").read_text(encoding="utf-8")
    assert full == home + "\n\n" + components
