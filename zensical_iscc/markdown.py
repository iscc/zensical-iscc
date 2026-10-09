"""Publish Markdown sources beside the rendered site for people and language models.

Every page under the docs directory is written to the site output as `index.md`
next to its `index.html`, which is where the theme's "Copy page" button and the
"View as Markdown" action look for it. A concatenated `llms-full.txt` in
navigation order is written to the site root.
"""

import re
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\r?\n.*?\r?\n---\r?\n", re.DOTALL)


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


def write_pages(docs_dir, site_dir, sources):
    # type: (Path, Path, list[Path]) -> None
    """Write each source page and the concatenated `llms-full.txt` into the site."""
    full = []
    for rel_path in sources:
        text = clean_markdown((docs_dir / rel_path).read_text(encoding="utf-8"))
        target = output_path(site_dir, rel_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        full.append(text)
    (site_dir / "llms-full.txt").write_text("\n\n".join(full), encoding="utf-8")
