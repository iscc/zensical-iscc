---
icon: lucide/house
description: Demo and reference site for the ISCC Zensical theme
---

# ISCC Theme Demo

This site shows the ISCC theme for [Zensical](https://zensical.org/) with the settings every ISCC documentation site
shares. Its configuration, `demo/zensical.toml`, is the reference that sites start from.

Preview it with `uv run poe demo` and compare both colour schemes after every theme or Zensical change. The
[components](components.md) page collects the elements that ISCC documentation uses.

The **Projects** menu in the header links the ISCC sites that work together. Every site should list its relatives
there, and itself, with `[[project.extra.iscc.related]]` tables in `zensical.toml`.

[Components](components.md){ .md-button .md-button--primary }
[Repository](https://github.com/iscc/zensical-iscc){ .md-button }
