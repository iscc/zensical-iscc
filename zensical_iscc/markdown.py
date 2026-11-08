"""Publish Markdown sources beside the rendered site for people and language models.

Every page under the docs directory is written to the site output as `index.md`
next to its `index.html`, which is where the theme's "Copy page" button and the
"View as Markdown" action look for it. The site root gets `llms-full.txt`, all
pages concatenated in navigation order, and `llms.txt`, an index of the pages after
<https://llmstxt.org/> that lists the "For Coding Agents" page first.
"""

import re
from pathlib import Path
from urllib.parse import quote

import yaml

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
HEADING_RE = re.compile(r"^#[ \t]+(.+?)[ \t]*$", re.MULTILINE)
AGENT_PAGE = "for-coding-agents.md"


def flatten_nav(nav):
    # type: (list) -> list[str]
    """Return the Markdown paths of a Zensical `nav` list in reading order."""
    paths = []
    for item in nav:
        if isinstance(item, dict):
            for value in item.values():
                paths.extend(flatten_nav(value if isinstance(value, list) else [value]))
        else:
            paths.append(item)
    return paths


def nav_titles(nav):
    # type: (list) -> dict[str, str]
    """Return the navigation label of each Markdown path that a Zensical `nav` list names."""
    titles = {}
    for item in nav:
        if isinstance(item, dict):
            for label, value in item.items():
                if isinstance(value, list):
                    titles.update(nav_titles(value))
                else:
                    titles[value] = label
    return titles


def page_sources(docs_dir, excluded_dir):
    # type: (Path, Path | None) -> list[Path]
    """Return every Markdown page under docs, excluding the theme override directory."""
    excluded = excluded_dir.resolve() if excluded_dir else None
    sources = []
    for path in sorted(docs_dir.rglob("*.md")):
        if excluded and excluded in path.resolve().parents:
            continue
        sources.append(path.relative_to(docs_dir))
    return sources


def output_path(site_dir, rel_path):
    # type: (Path, Path) -> Path
    """Map a docs-relative Markdown path to its directory-URL location in the site."""
    if rel_path.name == "index.md":
        return site_dir / rel_path
    return site_dir / rel_path.with_suffix("") / "index.md"


def clean_markdown(text):
    # type: (str) -> str
    """Strip YAML frontmatter and surrounding whitespace."""
    return FRONTMATTER_RE.sub("", text).strip() + "\n"


def ordered_sources(sources, nav):
    # type: (list[Path], list) -> list[Path]
    """Sort sources by navigation order, appending pages the nav does not mention."""
    nav_paths = [Path(p) for p in flatten_nav(nav)]
    ordered = [p for p in nav_paths if p in sources]
    ordered.extend(p for p in sources if p not in ordered)
    return ordered


def agent_page(sources):
    # type: (list[Path]) -> Path | None
    """Return the "For Coding Agents" page among the sources, if the site has one."""
    return next((p for p in sources if p.name == AGENT_PAGE), None)


def description(text):
    # type: (str) -> str
    """Return the front matter `description` of a page on one line, or "" if it has none."""
    front = FRONTMATTER_RE.match(text)
    try:
        meta = yaml.safe_load(front.group(1)) if front else None
    except yaml.YAMLError:
        return ""
    value = meta.get("description") if isinstance(meta, dict) else None
    return " ".join(str(value).split()) if value else ""


def index_entry(rel_path, text, titles):
    # type: (Path, str, dict[str, str]) -> str
    """Return the `llms.txt` line of one page: title, encoded Markdown URL and front matter description."""
    heading = HEADING_RE.search(clean_markdown(text))
    title = titles.get(rel_path.as_posix()) or (heading.group(1) if heading else rel_path.stem)
    label = re.sub(r"([\\\[\]])", r"\\\1", title)
    line = f"- [{label}]({quote(output_path(Path(), rel_path).as_posix())})"
    summary = description(text)
    return f"{line}: {summary}" if summary else line


def llms_index(config, pages):
    # type: (dict, list[tuple[Path, str]]) -> str
    """Return the `llms.txt` index of a site's pages, given as (path, source text) in navigation order."""
    titles = nav_titles(config.get("nav", []))
    agent = agent_page([rel_path for rel_path, _ in pages])
    lines = [f"# {config.get('site_name', 'Documentation')}", ""]
    if config.get("site_description"):
        lines += [f"> {config['site_description']}", ""]
    if agent:
        lines += ["## For coding agents", "", index_entry(agent, dict(pages)[agent], titles), ""]
    lines += ["## Pages", "", *(index_entry(p, text, titles) for p, text in pages if p != agent), ""]
    lines += ["## Optional", "", "- [All pages in one file](llms-full.txt)", ""]
    return "\n".join(lines)


def write_pages(docs_dir, site_dir, sources, config):
    # type: (Path, Path, list[Path], dict) -> None
    """Write each source page, the concatenated `llms-full.txt` and the `llms.txt` index into the site."""
    pages = [(rel_path, (docs_dir / rel_path).read_text(encoding="utf-8")) for rel_path in sources]
    full = [clean_markdown(text) for _, text in pages]
    for (rel_path, _), text in zip(pages, full, strict=True):
        target = output_path(site_dir, rel_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    (site_dir / "llms-full.txt").write_text("\n\n".join(full), encoding="utf-8")
    (site_dir / "llms.txt").write_text(llms_index(config, pages), encoding="utf-8")
