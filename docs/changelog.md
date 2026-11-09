---
icon: lucide/history
description: What changed in each release of the ISCC theme
---

# Changelog

To upgrade a site, change the `tag` in its `[tool.uv.sources]` and run `uv lock --upgrade-package zensical-iscc`.

## Unreleased

- **Diagrams open in a lightbox.** A click on a Mermaid diagram, or Enter on it, shows it as large as the screen
    allows, and never smaller than Mermaid drew it: on a phone, a diagram that the page shrinks becomes readable,
    and a diagram wider than the screen scrolls. The lightbox follows the color scheme. Pages with a diagram also
    load the theme's copy of GLightbox.

## 0.3.1 - 2026-11-09

Pins **Zensical 0.1.0**.

- **Mermaid diagrams.** Fenced `mermaid` blocks become diagrams. The theme serves its own copy of Mermaid 12.2.0,
    only on pages with a diagram, so no page loads it from unpkg.com. Sequence diagrams now take the theme colors
    like flowcharts. `zensical-iscc check` accepts these pages and reports a diagram only when the page lacks the
    theme's copy.
- **Links in the Markdown copies.** Links between pages work in `<page>/index.md` and `llms-full.txt`: the build
    rewrites each relative link to a page or file for the copy's location, so "Copy page", "View as Markdown" and
    agents following links no longer reach missing files. `zensical-iscc check` warns about a link in a copy that
    points at nothing.

Upgrade: add `custom_fences = [{ name = "mermaid", class = "mermaid" }]` to
`[project.markdown_extensions.pymdownx.superfences]`, as in the reference `zensical.toml`.

## 0.3.0 - 2026-11-08

Pins **Zensical 0.1.0**.

- **Project logo.** The header shows the ISCC project logo, for example "ISCC | monitor.". `zensical-iscc build`
    draws it from `project` in `[project.extra.iscc]`, or from `repo_name` without `iscc-`.
- **Header and footer.** Both are Deep Navy with grain and align with the page columns. A "Projects" menu links the
    related ISCC sites in `[[project.extra.iscc.related]]`. The footer shows the ISCC links and the social links of
    the site and of the ISCC Foundation.
- **For Coding Agents.** Each site ends its navigation with `for-coding-agents.md`. The `docs-for-agents` skill of
    the plugin writes it. The build writes an `llms.txt` index with this page first.
- **Type.** Body text is Readex Pro Light at 16px. Pages set a navigation icon with `icon: lucide/<name>`.
- The theme documentation is at <https://theme.iscc.codes/>.

Upgrade: `zensical-iscc check --strict` fails until the site has a For Coding Agents page and a plain-text
`copyright`.

## 0.2.0 - 2026-10-09

Pins **Zensical 0.0.69**.

- **Plausible analytics by default.** Each site counts visits under the host name of its `site_url`.
    `[project.extra.analytics] domain` sets a different host. Register new hosts at stats.iscc.codes.
- **Page components:** lead paragraph (`.iscc-lead`), calls to action (`.iscc-btn`, `.iscc-btn--primary`) and
    audience cards (`.iscc-cards`, `.iscc-card`). Remove these rules from site stylesheets.
- `zensical-iscc check` does not ask for an analytics table anymore. It reports a different analytics provider and
    a domain that is not the `site_url` host.

## 0.1.0 - 2026-10-09

First release of the ISCC theme for Zensical as a package. Pins **Zensical 0.0.69**.

- The theme files are the same as the copy that ISCC sites used before.
- `zensical-iscc build` builds a site and writes the Markdown copies of its pages and `llms-full.txt`.
- `zensical-iscc check` reports errors in the theme configuration and resources from other domains.
- The agent skill `iscc-docs-theme` sets up the theme in ISCC projects.
