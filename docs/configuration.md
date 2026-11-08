---
icon: lucide/settings
description: All settings of an ISCC site in zensical.toml, and the settings that it leaves to the theme
---

# Configuration

A site sets up the theme in `zensical.toml`. The
[`zensical.toml`](https://github.com/iscc/zensical-iscc/blob/main/zensical.toml) of the theme repository builds
this site. It is also the full reference:

- Values with the comment `# site` are different for each site.
- All other values are the shared ISCC setup.

## TOML traps

- Put `nav = [...]` directly below `[project]`, before all subtables such as `[project.extra.iscc]`. In TOML, a key
    after a table header goes into that table.
- Write related projects with double brackets: `[[project.extra.iscc.related]]`. Single brackets make one table,
    not a list. `zensical-iscc check` reports this error.

## Site settings

| Setting                       | Rule                                                                                     |
| ----------------------------- | ---------------------------------------------------------------------------------------- |
| `site_name`                   | The name of the project. It is the first part of the home page title and link previews   |
| `site_description`            | One sentence. Pages without a description of their own use it                            |
| `site_url`                    | The published URL, with a trailing slash. Link previews, canonical URLs and analytics need it |
| `repo_url`, `repo_name`       | The GitHub repository. `repo_name` also gives the name in the project logo           |
| `edit_uri`                    | `"edit/main/<docs dir>/"`. The Zensical default points to a `master` branch              |
| `copyright`                   | Plain text with the years, such as `"Copyright © 2026 The Authors"`. The theme adds the ISCC links |
| `nav`                         | All pages. The last entry is `{ "For Coding Agents" = "for-coding-agents.md" }`          |

## `[project.extra.iscc]`

The theme reads these options:

| Option      | Default                             | Use                                                                    |
| ----------- | ----------------------------------- | ---------------------------------------------------------------------- |
| `tagline`   | International Standard Content Code | The second part of the home page title: "ISCC Theme - Zensical theme for ISCC documentation" |
| `copy_page` | `true`                              | Shows the "Copy page" button. Its content needs `zensical-iscc build`  |
| `chat`      | `false`                             | Shows the iscc.ai chat widget. Set it only for domains that iscc.ai serves |
| `og_image`  | `assets/iscc/social-share.png`      | The path of the link preview image, relative to the site root          |
| `project`   | `repo_name` without `iscc-`         | The name in the project logo of the header                         |
| `related`   | none                                | The entries of the "Projects" menu, as `[[project.extra.iscc.related]]` tables |

```toml
[project.extra.iscc]
tagline = "Zensical theme for ISCC documentation"
copy_page = true
chat = false
project = "theme"
```

The chat widget starts only on domains that the iscc.ai token endpoint allows. It does not work on localhost.

## Project logo

The header starts with the ISCC project logo: the ISCC logo, a thin vertical line and the project
name in Readex Pro Bold with a coral period. On this site, it reads "ISCC | theme.".

- The name comes from `project`. If `project` is not set, the theme uses `repo_name` without the owner and without
    the prefix `iscc-`. For example, `iscc/iscc-monitor` gives `monitor`.
- Set `project` if this rule gives the wrong name. This site sets it, because `iscc/zensical-iscc` gives
    `zensical-iscc`, which is not a valid name.
- A valid name has lowercase words with hyphens between them. It does not contain `iscc`.
- `zensical-iscc build` draws the project logo with the font and logo copies of the theme. It writes the project logo to
    `assets/iscc/project-logo.svg`, in white and coral, at a symbol height of 24px.
- The header shows the plain ISCC logo and the site name instead of the project logo:
    - under `zensical serve`
    - on screens narrower than 720px
    - on sites without a project name

## Related projects menu

ISCC has many sites that work together, for example the specification, the hub, search, the web generator and the
monitor. Readers go from one site to the next, so each site lists its related sites in the "Projects" menu of the
header:

- the sites that it connects to
- the specification at iscc.codes
- the site itself

```toml
[[project.extra.iscc.related]]
name = "ISCC Monitor"                                                   # this site; marked as the current one
link = "https://monitor.iscc.codes/"
description = "Verifies and mirrors the transparency logs of ISCC hubs"

[[project.extra.iscc.related]]
name = "ISCC Specification"
link = "https://iscc.codes/"
description = "The International Standard Content Code, ISO 24138"
```

- Each table adds one menu entry, in the order of the file. An entry has a `name`, an https `link` and a one-line
    `description`.
- Write the description for the readers of this site. Tell them what the other site does for them, in less than
    60 characters.
- The entry that links to the `site_url` of the site gets the coral marker for the current site. When all sites of
    a group list themselves, the menu is the same on each site and readers see where they are.
- A site without entries has no menu.
- The menu button is a grid icon. From 960px up, it also shows the label "Projects". The menu opens on hover, focus
    or tap, without JavaScript. On phones, it fills the width of the screen below the header.

## Analytics

All ISCC sites count visits with Plausible at stats.iscc.codes, under the host name of `site_url`. Register that
host name at stats.iscc.codes. A site without `site_url` has no analytics.

You need the `[project.extra.analytics]` table only to change the defaults:

```toml
[project.extra.analytics]
domain = "iscc.codes"                             # default: the host name of site_url
src = "https://stats.iscc.codes/js/plausible.js"  # default
```

## `[project.theme]`

```toml
[project.theme]
name = "zensical_iscc"
# custom_dir = "docs/overrides"  # templates for this site only, on top of the theme
# features = [...]               # replaces the default features of the theme
```

| Setting                              | Rule                                                                            |
| ------------------------------------ | ------------------------------------------------------------------------------- |
| `name`                               | `"zensical_iscc"`                                                               |
| `font`, `logo`, `favicon`, `palette` | Do not set. The theme supplies the fonts and the ISCC logos and colors          |
| `features`                           | Do not set, to get the theme defaults. Never add `navigation.instant`           |
| `custom_dir`                         | Only for templates of this site. Never put a copy of the theme or a `main.html` there |

The default features are `content.code.annotate`, `content.code.copy`, `content.tooltips`, `navigation.expand`,
`navigation.footer`, `navigation.indexes`, `navigation.sections`, `navigation.top`, `navigation.tracking`,
`search.highlight` and `toc.follow`. A `features` list replaces all of them. Copy the defaults that the site needs
into the list.

A page template in `custom_dir` can extend the theme with `{% extends "main.html" %}`. Do not put a `main.html` in
`custom_dir`. It replaces the `main.html` of the theme and removes its styles, metadata and widgets.

## Markdown extensions

A list of Markdown extensions replaces the Zensical default set, so the list must be complete. Start from the list
in the reference configuration: `abbr`, `admonition`, `attr_list`, `def_list`, `footnotes`, `md_in_html`, `toc`
with permalinks, and the pymdownx extensions `details`, `highlight`, `superfences` and `tabbed`. Add the extensions
of your project to it.
