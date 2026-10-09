---
name: iscc-docs-theme
description: Set up, migrate, upgrade or check the ISCC documentation theme (zensical-iscc) in an ISCC project. Use when asked to apply the ISCC theme or branding to a project's documentation, to move docs from MkDocs Material, from Zensical with old overrides or from a vendored zensical_iscc copy onto the theme package, to bump the theme version, or to fix `zensical-iscc check` findings.
---

# ISCC documentation theme

The goal is a documentation site built by Zensical with the `zensical-iscc` package that passes
`zensical-iscc check --strict` and is built, checked and deployed by CI.

The theme repository is <https://github.com/iscc/zensical-iscc>; ISCC checkouts usually sit next to each other, so
look for `../zensical-iscc` first. Files referenced here, relative to that repository:

| File                                       | Use                                                              |
| ------------------------------------------ | ---------------------------------------------------------------- |
| `demo/zensical.toml`                       | Reference configuration; values marked `# site` are per site     |
| `README.md`                                | Theme options, design rules, third-party requests and known gaps |
| `skills/iscc-docs-theme/docs-workflow.yml` | GitHub Actions template: build, check, deploy to GitHub Pages    |

The project needs Python 3.11 or newer.

## 1. Survey the project first

Read before changing anything and note what you find:

- **Generator**: `zensical.toml`, `mkdocs.yml` (MkDocs Material) or no docs yet.
- **Packaging and commands**: `pyproject.toml` dependency groups, `uv.lock`, docs tasks in poe, a Makefile or a
    justfile, and the docs commands in `README.md` and `CLAUDE.md`.
- **Overrides** in `custom_dir` (often `docs/overrides/` or `overrides/`), file by file:
    - Duplicates of the theme: a `main.html` that sets the title, Open Graph tags or the Plausible script,
        `partials/integrations/analytics/custom.html`, a logo partial. These go.
    - Site-specific: page templates selected with `template:` front matter, partials for features the theme
        lacks. These stay.
- **Analytics domain**: the `data-domain` of the old Plausible snippet. Reuse it.
- **Styling**: `extra_css` and `extra_javascript`. Rules that restyle fonts, colours or the logo go; component
    styles stay.
- **Third-party content**: hot-linked images and badges (shields.io and the like), web fonts, scripts from CDNs.
- **Mermaid**: `custom_fences` with `mermaid`, or fenced `mermaid` blocks in the docs.
- **Plugins**: mkdocstrings, glightbox, redirects and others; keep the ones Zensical supports.
- **Deployment**: the docs workflow, GitHub Pages, `docs/CNAME`, and the published URL.

## 2. Ask the human about what only they know

Ask in one message, with your recommendation for each:

- `tagline`, the suffix of the home page title, if the old overrides do not show one.
- `chat = true` only if the human confirms that iscc.ai serves the site's domain.
- The analytics domain if there was none before; the convention is the host name of `site_url`.
- Mermaid diagrams: the theme does not serve Mermaid yet, and the Zensical bundle would load it from unpkg.com. Do
    not keep them without a decision.
- Anything in the survey that looks site-specific but would also suit other ISCC sites: it may belong in the theme.

Do not ask about settings that `demo/zensical.toml` already settles.

## 3. Add the dependency

Find the latest release tag:

```bash
git ls-remote --tags --refs --sort=-v:refname https://github.com/iscc/zensical-iscc | head -1
```

For a uv project, put the theme in the dependency group that holds the docs tools (usually `docs`) and remove any
direct `zensical`, `mkdocs` or `mkdocs-material` requirement. The theme pins the Zensical version it is tested with.

```toml
[dependency-groups]
docs = ["zensical-iscc"]

[tool.uv.sources]
zensical-iscc = { git = "https://github.com/iscc/zensical-iscc", tag = "vX.Y.Z" } # the tag found above
```

Then run `uv lock` and `uv sync`. Without uv:
`pip install "zensical-iscc @ git+https://github.com/iscc/zensical-iscc@vX.Y.Z"`.

## 4. Configure zensical.toml

Start from `demo/zensical.toml`: replace every value marked `# site`, then carry over the project's own `nav`,
Markdown extensions and plugins. The rules that matter:

| Setting                              | Rule                                                                           |
| ------------------------------------ | ------------------------------------------------------------------------------ |
| `[project.theme] name`               | `"zensical_iscc"`                                                              |
| `[project.theme] custom_dir`         | Only for site-specific overrides; never a copy of the theme, never `main.html` |
| `font`, `logo`, `favicon`, `palette` | Leave unset; the theme provides them                                           |
| `features`                           | Leave unset to get the theme defaults; never add `navigation.instant`          |
| `site_url`                           | The published URL with a trailing slash                                        |
| `edit_uri`                           | `"edit/main/<docs dir>/"`; the default points at a `master` branch             |
| `[project.extra.iscc]`               | `tagline`, `copy_page = true`, `chat = false` unless confirmed                 |
| `[project.extra.analytics]`          | `provider = "plausible"`, `domain` = host name of `site_url`                   |
| `copyright`                          | The ISCC footer from the demo, with the project's years                        |

Coming from `mkdocs.yml`: write `zensical.toml` by hand (MkDocs keys become keys of `[project]`, plugin and
extension options become tables, see <https://zensical.org/docs/setup/basics/>), then delete `mkdocs.yml`.

## 5. Remove what the theme provides

- A vendored theme directory (`zensical_iscc/`) and `scripts/gen_markdown_pages.py`.
- Override files classified as duplicates in step 1. A page template may keep `{% extends "main.html" %}`; it then
    extends the theme.
- Logos, favicons and fonts under `docs/` that nothing references any more.
- Brand rules in `extra_css`, and `extra_css` itself if nothing remains.
- Hot-linked images and badges: download them into `docs/` and link the copies.

Never edit theme files inside a site. A change the site needs from the theme goes into the theme repository and a
new release tag.

## 6. Build commands

| Task    | Command                                                                            |
| ------- | ---------------------------------------------------------------------------------- |
| Build   | `zensical-iscc build` (Zensical build plus the Markdown copies for "Copy page")    |
| Check   | `zensical-iscc check --strict`                                                     |
| Preview | `zensical serve --dev-addr 127.0.0.1:<port>`; keep a port the project already uses |

`zensical-iscc build` replaces `zensical build` followed by `gen_markdown_pages.py`. Update the project's poe
tasks or Makefile, and the docs commands in `README.md` and `CLAUDE.md`. Both commands read `zensical.toml` in the
working directory; pass `--config-file` for another location.

## 7. CI

Copy `docs-workflow.yml` to `.github/workflows/docs.yml`, or add its build and check steps to the existing docs
workflow. Keep the project's deployment target and its newer action pins. Trigger on `pyproject.toml` and `uv.lock`
too, so a theme bump rebuilds the site.

## 8. Verify

1. `uv run zensical-iscc build` and `uv run zensical-iscc check --strict` end with `0 errors, 0 warnings`. Explain
    any warning you leave to the human.
1. Serve the built `site/` directory (for example `python -m http.server <port> --directory site`) and look at the
    home page and one inner page in the light and the dark scheme: ISCC logo, Readex Pro headings, "Copy page"
    button.
1. Search the repository for leftovers: `zensical_iscc/`, `gen_markdown_pages`, `mkdocs`, old logo file names.

## Upgrading the theme

Change the `tag` in `[tool.uv.sources]`, run `uv lock --upgrade-package zensical-iscc`, then build and check. The
release notes on GitHub say what changed and which Zensical version the release pins.

## Rules

- Pages load nothing from other origins except Plausible (`stats.iscc.codes`) and, with chat on, `iscc.ai`.
    `zensical-iscc check` enforces this for the built HTML and CSS. The README lists the requests it cannot see.
- No Mermaid until the theme serves it.
- No `navigation.instant`: lightbox pages would then load GLightbox from unpkg.com.
- `README.md` of the theme documents `[project.extra.iscc]` and the CSS classes for ISCC-UNIT labels.
