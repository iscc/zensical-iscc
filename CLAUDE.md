# CLAUDE.md

Guidance for coding agents working in this repository.

## Project

**zensical-iscc** is the ISCC theme for Zensical documentation sites, installed from GitHub release tags. It ships
the theme (`zensical_iscc/theme/`), the `zensical-iscc` command (`build`, `markdown`, `check`) and an agent skill
for setting the theme up in ISCC projects (`skills/iscc-docs-theme/`). The repository is also a Claude Code plugin
marketplace (`.claude-plugin/`) that serves that skill.

Sites that use the theme: `../iscc-codes`, `../iscc-c2pa-resolver`.

## Commands

```bash
uv sync                  # dev dependencies
uv run prek install      # git hooks (once per clone)
uv run poe all           # format, type check, test (local loop)
uv run poe ci            # all gates without modifying files
uv run poe test          # pytest, 100% branch coverage required
uv run poe demo          # build the demo site and serve it on 127.0.0.1:45472
```

## Layout

- `zensical_iscc/theme/` - the theme directory Zensical loads; no Python files here, Zensical copies everything
    that is not a template into the built site
- `zensical_iscc/__init__.py` - `THEME`, the object the `mkdocs.themes` entry point names
- `zensical_iscc/cli.py`, `markdown.py`, `check.py`, `project.py` - the `zensical-iscc` command
- `demo/` - demo site and reference configuration; tests build copies of it
- `skills/iscc-docs-theme/` - agent skill and the docs workflow template for sites
- `tests/` - pytest; real Zensical builds of the demo site in temporary directories

## Rules

- `pyproject.toml` pins one Zensical version. Upgrading it means: bump the pin, build the demo, compare both colour
    schemes in a browser, run the tests, release.
- Brand assets under `theme/assets/iscc/` (`tokens/`, `fonts/`, `logos/`, favicons) are copies; refresh them from
    `../iscc-brand` and `../iscc-io/public/`, never edit them here. `vendor/` holds GLightbox 3.3.1 unchanged.
- Keep the theme's promise of no third-party requests; `zensical_iscc/check.py` enforces it for sites.
- Every page option, check and command change is reflected in `README.md`, `demo/zensical.toml` and
    `skills/iscc-docs-theme/SKILL.md`.
- Theme styles reference the `--iscc-*` tokens and `--md-*` variables, never raw hex values. Content width is capped
    at 1385px.
- Type hints as PEP 484 type comments. Short pure functions, a docstring on every module and function.
- Commits follow Conventional Commits (`feat:`, `fix:`, `build:`, `docs:`, `ci:`).

## Zensical quirks

- Templates run on MiniJinja, not Jinja2: attribute access on an undefined value raises. Guard with
    `{% set meta = page.meta or {} %}` before reading `meta.description`. `page.is_homepage` is unreliable, so
    `main.html` also checks `page.url == ""`.
- The modern variant styles `.md-nav--primary .md-nav__item .md-nav__link--active` and
    `.md-header__button.md-logo img`; overrides in `theme.css` must match that specificity.
- Zensical sets `html { font-size: 125% }` (20px), rising to 137.5% and 150% on wide screens. Rem-based third-party
    widgets render larger; pin pixel values for them.
- There is no plugin system for post-build steps; `zensical-iscc build` runs the Markdown export after
    `zensical build`.
- `zensical build --clean` clears the build cache, not the site directory.
