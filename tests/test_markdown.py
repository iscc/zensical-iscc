"""Markdown copies of the pages, `llms-full.txt` and the `llms.txt` index beside the rendered site."""

from pathlib import Path

from conftest import build

from zensical_iscc import markdown, project


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


def test_nav_titles_map_paths_to_labels():
    nav = [{"Home": "index.md"}, {"Guide": ["guide/index.md", {"Setup": "guide/setup.md"}]}, "about.md"]
    assert markdown.nav_titles(nav) == {"index.md": "Home", "guide/setup.md": "Setup"}


def test_index_entry_titles_and_descriptions():
    titles = {"setup.md": "Setup"}
    text = "---\nicon: lucide/rocket\ndescription: 'Install it'\n---\n\n# Installing\n"
    assert markdown.index_entry(Path("setup.md"), text, titles) == "- [Setup](setup/index.md): Install it"
    assert markdown.index_entry(Path("guide/index.md"), text, {}) == "- [Installing](guide/index.md): Install it"
    assert markdown.index_entry(Path("notes.md"), "Text only\n", {}) == "- [notes](notes/index.md)"


def test_index_entry_encodes_link_destinations():
    assert markdown.index_entry(Path("user)guide.md"), "# Guide\n", {}) == "- [Guide](user%29guide/index.md)"
    assert markdown.index_entry(Path("a b/c#d.md"), "# CD\n", {}) == "- [CD](a%20b/c%23d/index.md)"


def test_index_entry_escapes_link_text():
    titles = {"setup.md": "Setup [beta]"}
    assert markdown.index_entry(Path("setup.md"), "", titles) == r"- [Setup \[beta\]](setup/index.md)"
    assert markdown.index_entry(Path("x.md"), "# A\\B ]\n", {}) == r"- [A\\B \]](x/index.md)"


def test_description_parses_yaml():
    assert markdown.description("---\ndescription: >-\n  Long text\n  over lines\n---\n# X\n") == "Long text over lines"
    assert markdown.description("---\ndescription: 'It''s \"here\"'\n---\n") == 'It\'s "here"'
    assert markdown.description("---\r\ndescription: Windows\r\n---\r\n") == "Windows"
    assert markdown.description("---\ndescription: 42\n---\n") == "42"
    assert markdown.description("---\nicon: lucide/x\n---\n") == ""
    assert markdown.description("---\n- a list\n---\n") == ""
    assert markdown.description("---\ndescription: [unclosed\n---\n") == ""
    assert markdown.description("# No front matter\n") == ""


def test_llms_index_without_agent_page_or_description():
    pages = [(Path("index.md"), "# Home\n")]
    assert markdown.llms_index({"site_name": "Site"}, pages) == (
        "# Site\n\n## Pages\n\n- [Home](index.md)\n\n## Optional\n\n- [All pages in one file](llms-full.txt)\n"
    )


def test_agent_page():
    assert markdown.agent_page([Path("index.md"), Path("dev/for-coding-agents.md")]) == Path("dev/for-coding-agents.md")
    assert markdown.agent_page([Path("index.md")]) is None


def test_build_publishes_markdown_pages(docs_config):
    site = build(docs_config)
    nav = markdown.flatten_nav(project.load_project(docs_config)["nav"])
    copies = [markdown.output_path(site, Path(p)).read_text(encoding="utf-8") for p in nav]
    assert copies[0].startswith("# ISCC Theme\n")
    assert (site / "components" / "index.md").read_text(encoding="utf-8").startswith("# Components\n")
    assert (site / "llms-full.txt").read_text(encoding="utf-8") == "\n\n".join(copies)


def test_build_writes_llms_index_with_the_agent_page_first(docs_config):
    lines = (build(docs_config) / "llms.txt").read_text(encoding="utf-8").splitlines()
    assert lines[:3] == ["# ISCC Theme", "", "> Zensical theme, command and agent skills for ISCC documentation sites"]
    first = lines.index("## For coding agents") + 2
    assert lines[first].startswith("- [For Coding Agents](for-coding-agents/index.md): ")
    assert "- [Components](components/index.md): " in "\n".join(lines)
    assert sum("for-coding-agents" in line for line in lines) == 1
