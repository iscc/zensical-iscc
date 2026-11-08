"""Publish Markdown sources beside the rendered site for people and language models.

Every page under the docs directory is written to the site output as `index.md`
next to its `index.html`, which is where the theme's "Copy page" button and the
"View as Markdown" action look for it. The site root gets `llms-full.txt`, all
pages concatenated in navigation order, and `llms.txt`, an index of the pages after
<https://llmstxt.org/> that lists the "For Coding Agents" page first.

A copy lives one directory deeper than its source unless the source is an
`index.md`, and `llms-full.txt` lives at the site root, so each copy's relative
links to files in the docs directory are rewritten for its own location, the
way Zensical rewrites them in the HTML: links to pages point at their Markdown
copies, links to other files at the files. Links inside code stay as written.
"""

import posixpath
import re
from collections.abc import Callable  # noqa: F401 (used in type comments)
from functools import partial
from pathlib import Path
from urllib.parse import quote, unquote

import yaml

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
HEADING_RE = re.compile(r"^#[ \t]+(.+?)[ \t]*$", re.MULTILINE)
AGENT_PAGE = "for-coding-agents.md"
# Fenced code blocks and inline code, which stay as written, or the destination
# of an inline link or image, or of a reference definition (not a footnote).
LINK_RE = re.compile(
    r"(?P<code>(?s:^[ \t]*(?P<fence>`{3,}|~{3,}).*?^[ \t]*(?P=fence)[ \t]*$)|(?P<tick>`+)[^\n]+?(?P=tick))"
    r"|(?P<lead>\]\(\s*<?|^[ \t]{0,3}\[(?!\^)[^\]\n]+\]:[ \t]*<?)(?P<target>[^\s<>()]+)",
    re.MULTILINE,
)
NON_LOCAL_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9+.-]*:|/|#")


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


def replace_link(transform, match):
    # type: (Callable[[str], str], re.Match[str]) -> str
    """Return a `LINK_RE` match with its link destination transformed, or unchanged if it is code."""
    if match.group("code"):
        return match.group(0)
    return match.group("lead") + transform(match.group("target"))


def map_links(text, transform):
    # type: (str, Callable[[str], str]) -> str
    """Apply `transform` to every link and image destination of a Markdown text outside code."""
    return LINK_RE.sub(partial(replace_link, transform), text)


def local_links(text):
    # type: (str) -> list[str]
    """Return the relative link and image destinations of a Markdown text outside code."""
    targets = (m.group("target") for m in LINK_RE.finditer(text) if not m.group("code"))
    return [target for target in targets if not NON_LOCAL_RE.match(target)]


def docs_files(docs_dir):
    # type: (Path) -> frozenset[str]
    """Return the docs-relative POSIX paths of every file under the docs directory."""
    return frozenset(p.relative_to(docs_dir).as_posix() for p in docs_dir.rglob("*") if p.is_file())


def rebase_link(target, source_dir, copy_dir, files):
    # type: (str, str, str, frozenset[str]) -> str
    """Rewrite a link of a page in `source_dir` for a copy in `copy_dir`, both docs-relative directories.

    Only links that resolve to a file in `files` change; a page becomes its Markdown copy.
    """
    path, hash_mark, fragment = target.partition("#")
    if not path or NON_LOCAL_RE.match(target):
        return target
    resolved = posixpath.normpath(posixpath.join(source_dir, unquote(path)))
    if resolved not in files:
        return target
    if resolved.endswith(".md"):
        resolved = output_path(Path(), Path(resolved)).as_posix()
    return quote(posixpath.relpath(resolved, copy_dir)) + hash_mark + fragment


def rebase_links(text, rel_path, copy_dir, files):
    # type: (str, Path, str, frozenset[str]) -> str
    """Return the Markdown of the page at `rel_path` with its links rewritten for a copy in `copy_dir`."""
    source_dir = rel_path.parent.as_posix()
    return map_links(text, partial(rebase_link, source_dir=source_dir, copy_dir=copy_dir, files=files))


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
    """Write each source page, the concatenated `llms-full.txt` and the `llms.txt` index into the site.

    Links in each copy are rewritten for its location, and in `llms-full.txt` for the site root.
    """
    files = docs_files(docs_dir)
    pages = [(rel_path, (docs_dir / rel_path).read_text(encoding="utf-8")) for rel_path in sources]
    for rel_path, text in pages:
        target = output_path(site_dir, rel_path)
        copy_dir = output_path(Path(), rel_path).parent.as_posix()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rebase_links(clean_markdown(text), rel_path, copy_dir, files), encoding="utf-8")
    full = [rebase_links(clean_markdown(text), rel_path, ".", files) for rel_path, text in pages]
    (site_dir / "llms-full.txt").write_text("\n\n".join(full), encoding="utf-8")
    (site_dir / "llms.txt").write_text(llms_index(config, pages), encoding="utf-8")
