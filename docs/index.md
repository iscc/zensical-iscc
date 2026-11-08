---
icon: lucide/house
description: Zensical theme, command and agent skills for ISCC documentation sites
---

# ISCC Theme

A [Zensical](https://zensical.org/) theme that gives all ISCC documentation sites the same brand, the same page
tools and the same privacy rules.
{ .iscc-lead }

The `zensical-iscc` Python package has three parts:

- The theme.
- The `zensical-iscc` command. It builds a site and checks it.
- Two agent skills. One sets up the theme in a project. The other writes the page for coding agents.

This site uses the theme. Its [`zensical.toml`](https://github.com/iscc/zensical-iscc/blob/main/zensical.toml) is
the reference configuration for all ISCC sites.

[Get started](get-started.md){ .iscc-btn .iscc-btn--primary }
[Repository](https://github.com/iscc/zensical-iscc){ .iscc-btn }

## Features

<div class="iscc-cards" markdown>

<div class="iscc-card" markdown>

### Brand

The ISCC fonts, colors and logos on the modern Zensical design. The header shows the project name next to the ISCC
logo.

[Design →](design.md)

</div>

<div class="iscc-card" markdown>

### Shared tools

A "Copy page" button, a "Projects" menu that links the ISCC sites, the iscc.ai chat and Plausible analytics. One
table in `zensical.toml` sets them all.

[Configuration →](configuration.md)

</div>

<div class="iscc-card" markdown>

### Checks

`zensical-iscc check` makes sure that a site uses the theme, loads nothing from third parties and has a page for
coding agents.

[Command line →](command-line.md)

</div>

</div>

## Where to go next

| To                                               | Read                                      |
| ------------------------------------------------ | ----------------------------------------- |
| Put the documentation of a project on the theme  | [Get started](get-started.md)             |
| Find a setting                                   | [Configuration](configuration.md)         |
| Write pages: front matter, icons, images, agents | [Writing pages](writing.md)               |
| See all styled elements                          | [Components](components.md)               |
| Fix a `zensical-iscc check` finding              | [Command line](command-line.md)           |
| Learn about the colors, type and header          | [Design](design.md)                       |
| Change the theme                                 | [Development](development.md)             |
| Work on a site or on the theme as an agent       | [For Coding Agents](for-coding-agents.md) |
