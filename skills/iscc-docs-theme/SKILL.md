---
name: iscc-docs-theme
description: Set up, migrate, upgrade or check the ISCC documentation theme (zensical-iscc) in an ISCC project. Use when asked to apply the ISCC theme or branding to a project's documentation, to move docs from MkDocs Material, from Zensical with old overrides or from a vendored zensical_iscc copy onto the theme package, to bump the theme version, or to fix `zensical-iscc check` findings.
---

# ISCC documentation theme

The goal is a documentation site built by Zensical with the `zensical-iscc` package that passes
`zensical-iscc check --strict` and is built, checked and deployed by CI.

The theme repository is <https://github.com/iscc/zensical-iscc>; read the files from a local checkout of it if
there is one. Its documentation is published at <https://theme.iscc.codes/> (all pages in one
file: <https://theme.iscc.codes/llms-full.txt>). Files referenced here, relative to that repository:

| File                                       | Use                                                                |
| ------------------------------------------ | ------------------------------------------------------------------ |
| `zensical.toml`                            | Reference configuration; values marked `# site` are per site       |
| `docs/configuration.md`                    | Every setting and option, the project logo, the "Projects" menu    |
| `docs/writing.md`                          | Page conventions: front matter, icons, the For Coding Agents page  |
| `docs/components.md`                       | The CSS classes the theme styles                                   |
| `docs/command-line.md`                     | Commands, build outputs, every check finding, third-party requests |
| `skills/iscc-docs-theme/docs-workflow.yml` | GitHub Actions template: build, check, deploy to GitHub Pages      |
| `skills/docs-for-agents/SKILL.md`          | Skill that writes the site's For Coding Agents page                |

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
- **Analytics domain**: the `data-domain` of the old Plausible snippet. The theme counts visits under the host
    name of `site_url`; note the old domain only if it differs.
- **Styling**: `extra_css` and `extra_javascript`. Rules that restyle fonts, colours or the logo go, and so do
    the lead paragraph, call-to-action and card styles that the theme provides (see `docs/components.md`); other
    component styles stay.
- **Third-party content**: hot-linked images and badges (shields.io and the like), web fonts, scripts from CDNs.
- **Mermaid**: `custom_fences` with `mermaid`, or fenced `mermaid` blocks in the docs.
- **Plugins**: mkdocstrings, glightbox, redirects and others; keep the ones Zensical supports.
- **Deployment**: the docs workflow, GitHub Pages, `docs/CNAME`, and the published URL.
- **Agent docs**: an existing page for coding agents, an `AGENTS.md` or `CLAUDE.md`, and an `llms.txt` generator.
- **Related ISCC sites**: links to other ISCC sites in `nav`, the README or the home page, and the services the
    project calls or serves. They are the candidates for the "Projects" menu.

## 2. Ask the human about what only they know

Ask in one message, with your recommendation for each:

- `tagline`, the suffix of the home page title, if the old overrides do not show one.
- `chat = true` only if the human confirms that iscc.ai serves the site's domain.
- The header's "Projects" menu, which every ISCC site should have: propose the list, in order, from the survey.
    Recommend the site itself, the specification at iscc.codes and the sites the project works with, each with a
    one-line description you draft for this site's readers (under 60 characters) for the human to edit.
- Mermaid diagrams: the theme does not serve Mermaid yet, and the Zensical bundle would load it from unpkg.com. Do
    not keep them without a decision.
- Anything in the survey that looks site-specific but would also suit other ISCC sites: it may belong in the theme.

Do not ask about settings that the reference `zensical.toml` already settles.

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

Start from the theme's `zensical.toml`: replace every value marked `# site`, then carry over the project's own `nav`,
Markdown extensions and plugins. The rules that matter:

| Setting                              | Rule                                                                               |
| ------------------------------------ | ---------------------------------------------------------------------------------- |
| `[project.theme] name`               | `"zensical_iscc"`                                                                  |
| `[project.theme] custom_dir`         | Only for site-specific overrides; never a copy of the theme, never `main.html`     |
| `font`, `logo`, `favicon`, `palette` | Leave unset; the theme provides them                                               |
| `features`                           | Leave unset to get the theme defaults; never add `navigation.instant`              |
| `site_url`                           | The published URL with a trailing slash                                            |
| `edit_uri`                           | `"edit/main/<docs dir>/"`; the default points at a `master` branch                 |
| `[project.extra.iscc]`               | `tagline`, `copy_page = true`, `chat = false` unless confirmed                     |
| `project` in `[project.extra.iscc]`  | Leave unset when `repo_name` minus `iscc-` is the project name; else set it        |
| `[[project.extra.iscc.related]]`     | One table per related site, this one included: `name`, https `link`, `description` |
| `[project.extra.analytics]`          | Leave unset: Plausible counts the host of `site_url`; set `domain` if it differs   |
| `copyright`                          | Plain text, `"Copyright © <years> The Authors"`; the theme adds the ISCC links     |
| `nav`                                | Ends with `{ "For Coding Agents" = "for-coding-agents.md" }`                       |

Two TOML traps:

- Keep `nav = [...]` directly under `[project]`, before any subtable such as `[project.extra.iscc]` or
    `[[project.extra.social]]`; after a table header TOML scopes it into that table.
- Listing any Markdown extension replaces Zensical's default set, so the list must be complete. The reference list is
    the baseline; add the project's extras to it.

Every page gets a navigation icon: `icon: lucide/<name>` in its front matter, a name from
<https://lucide.dev/icons/>. Keep the icons that pages already set and pick a fitting one for the others; section
labels in `nav` take none.

Coming from `mkdocs.yml`: write `zensical.toml` by hand (MkDocs keys become keys of `[project]`, plugin and
extension options become tables, see <https://zensical.org/docs/setup/basics/>), then delete `mkdocs.yml`.

## 5. Remove what the theme provides

- A vendored theme directory (`zensical_iscc/`) and `scripts/gen_markdown_pages.py`.
- Override files classified as duplicates in step 1. A page template may keep `{% extends "main.html" %}`; it then
    extends the theme.
- Logos, favicons and fonts under `docs/` that nothing references any more.
- Brand rules and theme-provided components (`.iscc-lead`, `.iscc-btn`, `.iscc-cards`, `.iscc-card`) in
    `extra_css`, and `extra_css` itself if nothing remains. Remaining site styles reference the
    `--iscc-*` tokens and `--md-*` variables, not raw colour values.
- Hot-linked images and badges: download them into `docs/` and link the copies.

Never edit theme files inside a site. A change the site needs from the theme goes into the theme repository and a
new release tag.

## 6. Write the For Coding Agents page

Every ISCC site ends its navigation with `docs/for-coding-agents.md`, a dense reference for agents that work on the
project or integrate with it. Write it with the `docs-for-agents` skill of the same plugin
(`/zensical-iscc:docs-for-agents create`); without the plugin, follow `skills/docs-for-agents/SKILL.md` of the
theme repository. Give it `icon: lucide/bot` and a `description`, and fold an existing agent page into it.

Add this line to the project's `CLAUDE.md` or `AGENTS.md`, creating the file if needed, so later sessions keep the
page current:

```markdown
After changing the public API, CLI or configuration, run the docs-for-agents skill with `update`.
```

`zensical-iscc check` warns while the page is missing or not in `nav`.

## 7. Build commands

| Task    | Command                                                                            |
| ------- | ---------------------------------------------------------------------------------- |
| Build   | `zensical-iscc build` (Zensical build, Markdown copies, `llms.txt`, project logo)  |
| Check   | `zensical-iscc check --strict`                                                     |
| Preview | `zensical serve --dev-addr 127.0.0.1:<port>`; keep a port the project already uses |

`zensical-iscc build` replaces `zensical build` followed by `gen_markdown_pages.py`. Update the project's poe
tasks or Makefile, and the docs commands in `README.md` and `CLAUDE.md`. Both commands read `zensical.toml` in the
working directory; pass `--config-file` for another location.

## 8. CI

Copy `docs-workflow.yml` to `.github/workflows/docs.yml`, or add its build and check steps to the existing docs
workflow. Keep the project's deployment target and its newer action pins. Trigger on `pyproject.toml` and `uv.lock`
too, so a theme bump rebuilds the site.

## 9. Verify

1. `uv run zensical-iscc build` and `uv run zensical-iscc check --strict` end with `0 errors, 0 warnings`. Explain
    any warning you leave to the human.
1. Serve the built `site/` directory (for example `python -m http.server <port> --directory site`) and look at the
    home page and one inner page in the light and the dark scheme: the project logo in the header
    (for example "ISCC | monitor."), Readex Pro headings, "Copy page" button, an icon in front of every page in
    the navigation, the "Projects" menu with this site marked, "For Coding Agents" last in the navigation.
    `zensical serve` shows the plain ISCC logo instead of the project logo; only the built site has it.
1. `site/llms.txt` lists the For Coding Agents page first.
1. If the host of `site_url` is new to Plausible, tell the human to add it at stats.iscc.codes; until then
    visits are not counted.
1. Search the repository for leftovers: `zensical_iscc/`, `gen_markdown_pages`, `mkdocs`, old logo file names.

## Upgrading the theme

Change the `tag` in `[tool.uv.sources]`, run `uv lock --upgrade-package zensical-iscc`, then build and check. The
release notes on GitHub say what changed and which Zensical version the release pins. If the site has no
`[[project.extra.iscc.related]]` entries yet, propose the "Projects" menu as in step 2; if it has no For Coding
Agents page yet, write it as in step 6. If `copyright` still holds the old HTML string with links, replace it with
the plain text.

## Rules

- Pages load nothing from other origins except Plausible (`stats.iscc.codes`) and, with chat on, `iscc.ai`.
    `zensical-iscc check` enforces this for the built HTML and CSS. `docs/command-line.md` lists the requests it
    cannot see.
- No Mermaid until the theme serves it.
- No `navigation.instant`: lightbox pages would then load GLightbox from unpkg.com.
- The theme's `docs/` documents `[project.extra.iscc]` and the CSS classes for ISCC-UNIT labels.
