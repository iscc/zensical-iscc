"""Check that a site uses the ISCC theme as intended and loads nothing from other origins.

Configuration checks read `zensical.toml`. Site checks scan the built HTML and
CSS, so run them after `zensical-iscc build`. Requests that the Zensical bundle
makes at runtime are beyond a static scan; the README lists the ones that remain.
Each finding is a `(level, message)` pair with level `error` or `warning`.
"""

import re
from pathlib import Path  # noqa: F401 (used in type comments)
from urllib.parse import urlsplit

from zensical_iscc import markdown, project

THEME_NAME = "zensical_iscc"
ALLOWED_HOSTS = frozenset({"stats.iscc.codes", "iscc.ai"})
LINKED_RESOURCES = frozenset({"stylesheet", "icon", "preload", "modulepreload", "prefetch", "manifest"})
RESOURCE_TAG_RE = re.compile(r"<(script|img|iframe|source|audio|video|embed|link)\b[^>]*>", re.IGNORECASE)
ATTR_RE = re.compile(r"""([\w:-]+)\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)""")
CSS_URL_RE = re.compile(r"""(?:url\(\s*|@import\s+)["']?((?:https?:)?//[^"')\s;]+)""", re.IGNORECASE)
MERMAID_RE = re.compile(r"""class=["'][^"']*\bmermaid\b""")


def error(message):
    # type: (str) -> tuple[str, str]
    """Return an error finding."""
    return ("error", message)


def warning(message):
    # type: (str) -> tuple[str, str]
    """Return a warning finding."""
    return ("warning", message)


def external_host(url):
    # type: (str) -> str | None
    """Return the host of an absolute or protocol-relative URL, None for a site-relative one."""
    if url.startswith(("http://", "https://", "//")):
        return urlsplit(url).hostname
    return None


def is_foreign(url):
    # type: (str) -> bool
    """Tell whether a URL points at another origin that the theme does not allow."""
    host = external_host(url)
    return host is not None and host not in ALLOWED_HOSTS


def theme_findings(theme):
    # type: (dict) -> list[tuple[str, str]]
    """Check the `[project.theme]` table."""
    findings = []
    if theme.get("name") != THEME_NAME:
        findings.append(error(f'set `name = "{THEME_NAME}"` in [project.theme]'))
    if theme.get("font", False) is not False:
        findings.append(error("remove `font` from [project.theme]: the theme serves its own fonts"))
    if "navigation.instant" in theme.get("features", []):
        findings.append(error("remove the `navigation.instant` feature: it makes lightbox pages load from unpkg.com"))
    for key in ("logo", "favicon", "palette"):
        if key in theme:
            findings.append(
                warning(f"[project.theme] sets `{key}`, replacing the ISCC {key}; remove it unless intended")
            )
    return findings


def custom_dir_findings(override_dir):
    # type: (Path | None) -> list[tuple[str, str]]
    """Flag a `custom_dir` that holds a copy of the theme or replaces its main template."""
    if not override_dir:
        return []
    if (override_dir / "assets" / "iscc" / "theme.css").is_file():
        return [error(f"`custom_dir` {override_dir.name}/ holds a copy of the ISCC theme; delete it")]
    if (override_dir / "main.html").is_file():
        message = "main.html replaces the theme's main.html and drops its styles, metadata and widgets; delete it"
        return [error(f"{override_dir.name}/{message} (page templates may extend main.html)")]
    return []


def metadata_findings(config):
    # type: (dict) -> list[tuple[str, str]]
    """Check the site settings that titles, link previews and edit links depend on."""
    findings = []
    if not config.get("site_url"):
        findings.append(warning("set `site_url`: link previews and canonical URLs need it"))
    if config.get("repo_url") and not config.get("edit_uri"):
        findings.append(warning('set `edit_uri` (for example "edit/main/docs/"): the default uses the master branch'))
    if not config.get("extra", {}).get("iscc", {}).get("tagline"):
        findings.append(warning("set `tagline` in [project.extra.iscc]: it completes the home page title"))
    return findings


def analytics_findings(config):
    # type: (dict) -> list[tuple[str, str]]
    """Check that Plausible analytics count the site under its own host name."""
    analytics = config.get("extra", {}).get("analytics", {})
    domain = analytics.get("domain")
    if analytics.get("provider") != "plausible" or not domain:
        return [warning('set `provider = "plausible"` and `domain` in [project.extra.analytics]')]
    host = urlsplit(config.get("site_url") or "").hostname
    if host and domain != host:
        return [warning(f"analytics domain {domain} differs from the site_url host {host}")]
    return []


def extra_asset_findings(config):
    # type: (dict) -> list[tuple[str, str]]
    """Flag `extra_css` and `extra_javascript` entries served by other origins."""
    findings = []
    for key in ("extra_css", "extra_javascript"):
        for entry in config.get(key, []):
            url = entry if isinstance(entry, str) else entry.get("path", "")
            if is_foreign(url):
                findings.append(error(f"`{key}` loads {url}; serve a copy from the docs directory"))
    return findings


def tag_attrs(tag):
    # type: (str) -> dict[str, str]
    """Return the attributes of an HTML start tag with lowercase names and unquoted values."""
    return {name.lower(): value.strip("\"'") for name, value in ATTR_RE.findall(tag)}


def resource_urls(html):
    # type: (str) -> list[str]
    """Return the URLs of scripts, images, media, frames and linked resources in an HTML page."""
    urls = []
    for match in RESOURCE_TAG_RE.finditer(html):
        attrs = tag_attrs(match.group(0))
        if match.group(1).lower() != "link":
            urls.append(attrs.get("src", ""))
        elif LINKED_RESOURCES & set(attrs.get("rel", "").lower().split()):
            urls.append(attrs.get("href", ""))
    return urls


def page_findings(name, html):
    # type: (str, str) -> list[tuple[str, str]]
    """Check one built HTML page for resources from other origins and for Mermaid diagrams."""
    findings = [error(f"{name} loads {url}") for url in resource_urls(html) if is_foreign(url)]
    if MERMAID_RE.search(html):
        findings.append(error(f"{name} has a Mermaid diagram, which the Zensical bundle loads from unpkg.com"))
    return findings


def stylesheet_findings(name, css):
    # type: (str, str) -> list[tuple[str, str]]
    """Check one built stylesheet for imports and URLs from other origins."""
    return [error(f"{name} loads {url}") for url in CSS_URL_RE.findall(css) if is_foreign(url)]


def site_findings(built_dir):
    # type: (Path) -> list[tuple[str, str]]
    """Scan every HTML page and stylesheet of a built site."""
    findings = []
    for path in sorted(built_dir.rglob("*.html")):
        findings += page_findings(path.relative_to(built_dir).as_posix(), path.read_text(encoding="utf-8"))
    for path in sorted(built_dir.rglob("*.css")):
        findings += stylesheet_findings(path.relative_to(built_dir).as_posix(), path.read_text(encoding="utf-8"))
    return findings


def markdown_findings(built_dir, sources):
    # type: (Path, list[Path]) -> list[tuple[str, str]]
    """Check that the Markdown copies of the pages and `llms-full.txt` are in the built site."""
    missing = [p for p in sources if not markdown.output_path(built_dir, p).is_file()]
    if missing or not (built_dir / "llms-full.txt").is_file():
        return [error("Markdown pages are missing from the site; build with `zensical-iscc build`")]
    return []


def check(config_path):
    # type: (Path) -> list[tuple[str, str]]
    """Return all findings for the site configured by `config_path`."""
    config = project.load_project(config_path)
    override_dir = project.custom_dir(config_path, config)
    findings = theme_findings(config.get("theme", {}))
    findings += custom_dir_findings(override_dir)
    findings += metadata_findings(config) + analytics_findings(config) + extra_asset_findings(config)
    built_dir = project.site_dir(config_path, config)
    if not built_dir.is_dir():
        return [*findings, warning("the site is not built; run `zensical-iscc build` to check its pages")]
    sources = markdown.page_sources(project.docs_dir(config_path, config), override_dir)
    return findings + site_findings(built_dir) + markdown_findings(built_dir, sources)
