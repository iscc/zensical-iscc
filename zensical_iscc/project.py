"""Read the parts of a Zensical configuration file that the theme commands need."""

import tomllib
from pathlib import Path


def load_project(config_path):
    # type: (Path) -> dict
    """Return the `[project]` table of a Zensical configuration file."""
    with config_path.open("rb") as fp:
        return tomllib.load(fp)["project"]


def resolve_dir(config_path, value):
    # type: (Path, str) -> Path
    """Resolve a directory setting against the directory of the configuration file."""
    path = Path(value)
    return path if path.is_absolute() else config_path.resolve().parent / path


def docs_dir(config_path, project):
    # type: (Path, dict) -> Path
    """Return the directory holding the Markdown sources."""
    return resolve_dir(config_path, project.get("docs_dir", "docs"))


def site_dir(config_path, project):
    # type: (Path, dict) -> Path
    """Return the directory Zensical builds the site into."""
    return resolve_dir(config_path, project.get("site_dir", "site"))


def custom_dir(config_path, project):
    # type: (Path, dict) -> Path | None
    """Return the site's own theme override directory, if it sets one."""
    value = project.get("theme", {}).get("custom_dir")
    return resolve_dir(config_path, value) if value else None
