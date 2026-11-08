# Changelog

To upgrade a site, change the `tag` in its `[tool.uv.sources]` and run `uv lock --upgrade-package zensical-iscc`.

## Unreleased

Pins **Zensical 0.1.0**.

- **Product wordmark.** `zensical-iscc build` draws the ISCC product wordmark, for example "ISCC |
    monitor.". The name comes from `product` in `[project.extra.iscc]`, or else from `repo_name` without `iscc-`.
    The check reports a missing or invalid name and a missing wordmark.
- **Header.** The header is Deep Navy with grain and 64px high. It aligns with the body at all screen widths. A
    "Projects" menu links to the related ISCC sites in `[[project.extra.iscc.related]]`.
- **For Coding Agents.** The last navigation entry of each site is the `for-coding-agents.md` page. The check gives
    a warning if the page is missing or not in `nav`. The plugin has the `docs-for-agents` skill, which writes the
    page.
- **Markdown for agents.** The build writes an `llms.txt` index with the agent page first. Each page links to its
    Markdown copy with `<link rel="alternate" type="text/markdown">`.
- **Type and buttons.** Body text is Readex Pro Light at 16px, with lines of about 75 characters. The primary button
    is a near-black pointed block with a white label and a coral chevron.
- **Navigation icons.** Pages set `icon: lucide/<name>` in their front matter.
- Footer links are easier to read in the light scheme. The phone drawer keeps its top offset and shows only the ISCC
    logo.
- The theme documentation has its own site at theme.iscc.codes. This repository builds it.

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
