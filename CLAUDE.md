# CLAUDE.md

Guidance for coding agents working in this repository.

## Project

**zensical-iscc** is the ISCC theme for Zensical documentation sites, installed from GitHub release tags. It ships
the theme (`zensical_iscc/theme/`), the `zensical-iscc` command (`build`, `markdown`, `check`) and two agent
skills: `skills/iscc-docs-theme/` sets the theme up in ISCC projects, `skills/docs-for-agents/` writes their "For
Coding Agents" page. The repository is also a Claude Code plugin marketplace (`.claude-plugin/marketplace.json`)
that serves both from the plugin rooted at `skills/` (`skills/.claude-plugin/plugin.json`, whose `version` follows
the package version), and the source of the theme's documentation at <https://theme.iscc.codes/> (`zensical.toml`,
`docs/`).

## Commands

```bash
uv sync                  # dev dependencies
uv run prek install      # git hooks (once per clone)
uv run poe all           # format, type check, test (local loop)
uv run poe ci            # all gates without modifying files
uv run poe test          # pytest, 100% branch coverage required
uv run poe docs          # build the docs site and serve it on 127.0.0.1:45472
```

## Layout

- `zensical_iscc/theme/` - the theme directory Zensical loads; no Python files here, Zensical copies everything
    that is not a template into the built site
- `zensical_iscc/__init__.py` - `THEME`, the object the `mkdocs.themes` entry point names
- `zensical_iscc/cli.py`, `markdown.py`, `check.py`, `project.py`, `wordmark.py` - the `zensical-iscc` command;
    `wordmark.py` draws the product lockup and must match `tests/fixtures/products/` byte for byte
- `zensical.toml`, `docs/` - theme.iscc.codes and the reference configuration for sites; tests build copies of it
- `CHANGELOG.md` - release notes; the `changelog` git hook (`scripts/sync_changelog.py`) copies it to
    `docs/changelog.md`, so edit only the root file and commit the copy
- `skills/iscc-docs-theme/` - setup skill and the docs workflow template for sites
- `skills/docs-for-agents/SKILL.md` - verbatim copy of `plugins/docs-for-agents/` in `titusz/skills`; refresh it
    from there, never edit or format it here
- `tests/` - pytest; real Zensical builds of the docs site in temporary directories

## Rules

- `pyproject.toml` pins one Zensical version. Upgrading it means: bump the pin, build the docs site, compare both colour
    schemes in a browser, run the tests, release. `theme/partials/header.html` is Zensical's header plus one
    include; when Zensical's changes, a test fails until the copy is refreshed.
- Brand assets under `theme/assets/iscc/` (`tokens/`, `fonts/`, `logos/`, favicons, `grain.png`) are copies of
    the ISCC brand assets; refresh them from their sources (paths in the untracked `CLAUDE.local.md`), never edit
    them here. `vendor/` holds GLightbox 3.3.1 unchanged.
- Keep the theme's promise of no third-party requests; `zensical_iscc/check.py` enforces it for sites.
- Every page option, check and command change is reflected in `docs/`, `zensical.toml`,
    `skills/iscc-docs-theme/SKILL.md` and `CHANGELOG.md` under "Unreleased". After changing the public API, CLI or
    configuration, run the docs-for-agents skill with `update` on `docs/for-coding-agents.md`.
- `README.md` stays a short entry point that links to theme.iscc.codes; the details live in `docs/`.
- Content width is capped at 1385px.
- Type hints as PEP 484 type comments. Short pure functions, a docstring on every module and function.
- Commits follow Conventional Commits (`feat:`, `fix:`, `build:`, `docs:`, `ci:`).

## Zensical quirks

- Templates run on MiniJinja, not Jinja2: attribute access on an undefined value raises. Guard with
    `{% set meta = page.meta or {} %}` before reading `meta.description`. `page.is_homepage` is unreliable, so
    `main.html` also checks `page.url == ""`.
- The modern variant styles `.md-nav--primary .md-nav__item .md-nav__link--active`,
    `.md-header__button.md-logo img` and `html .md-footer-meta.md-typeset a:not(:focus, :hover)`; overrides in
    `theme.css` must match that specificity (a `:not()` adds the weight of its argument).
- Zensical sets `html { font-size: 125% }` (20px), rising to 137.5% and 150% on wide screens; `theme.css` holds it
    at 125%. Rem-based third-party widgets still render at 20px per rem; pin pixel values for them.
- There is no plugin system for post-build steps; `zensical-iscc build` runs the Markdown export after
    `zensical build`.
- `zensical build --clean` clears the build cache, not the site directory.

@AGENTS.md
