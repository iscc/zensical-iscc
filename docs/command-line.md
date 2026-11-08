---
icon: lucide/terminal
description: The zensical-iscc command, the files that the build writes and all findings of the check
---

# Command line

The `zensical-iscc` command comes with the theme package. Each subcommand reads `zensical.toml` in the working
directory. To use a different file, add `--config-file` (`-f`).

| Command                         | Does                                                                                 |
| ------------------------------- | ------------------------------------------------------------------------------------ |
| `zensical-iscc build`           | Runs `zensical build --clean`, then writes the Markdown copies, `llms.txt` and the product wordmark |
| `zensical-iscc markdown`        | Writes the Markdown copies and `llms.txt` into a site that is already built          |
| `zensical-iscc check`           | Checks the configuration and the built site. Exits with 1 on errors                  |
| `zensical-iscc check --strict`  | Also exits with 1 on warnings. Use this mode in CI                                   |

Zensical has no plugins for steps after the build, so use `zensical-iscc build` instead of `zensical build`.

## What the build writes

| Output                         | From                                                       | Read by                                 |
| ------------------------------ | ---------------------------------------------------------- | --------------------------------------- |
| `site/**/index.html`           | Zensical                                                   | Browsers                                |
| `site/<page>/index.md`         | The Markdown of each page, without front matter            | "Copy page", "View as Markdown", agents |
| `site/llms-full.txt`           | All pages, in navigation order                             | Language models that read a full site   |
| `site/llms.txt`                | The title, link and description of each page, agent page first | Agents that look for a start page   |
| `site/assets/iscc/product.svg` | The product name and the ISCC wordmark construction rules    | The header                            |

## Findings

The check reads `zensical.toml` and the docs directory. Then it examines each HTML page and stylesheet of the built
site. It cannot see the requests that the Zensical bundle makes in the browser.
[Third-party requests](#third-party-requests) lists them.

### Errors

| Finding                                                    | Fix                                                                  |
| ---------------------------------------------------------- | -------------------------------------------------------------------- |
| `set name = "zensical_iscc" in [project.theme]`            | Set the theme                                                        |
| `remove font from [project.theme]`                         | Remove it. The theme supplies its fonts                              |
| `remove the navigation.instant feature`                    | Remove it. It makes lightbox pages load GLightbox from unpkg.com     |
| `custom_dir … holds a copy of the ISCC theme`              | Delete the copy. Add the package as a dependency                     |
| `main.html replaces the theme's main.html`                 | Delete it. Page templates can extend `main.html`                     |
| `product … use lowercase words and hyphens, without iscc-` | Correct `product` in `[project.extra.iscc]`                          |
| `related project … lacks …` or `… use an https:// URL`     | Add the missing field. Use an https link                             |
| `write related projects as [[project.extra.iscc.related]] tables` | Use double brackets                                           |
| `extra_css / extra_javascript loads …`                     | Put a copy in the docs directory                                     |
| `<page> loads <url>`                                       | Put the image, script or stylesheet in `docs/`                       |
| `<page> has a Mermaid diagram`                             | Replace the diagram with an SVG file                                 |
| `Markdown pages are missing from the site`                 | Build with `zensical-iscc build`, not with `zensical build`          |
| `the product wordmark is missing from the site`            | Build with `zensical-iscc build`                                     |

### Warnings

| Finding                                                    | Fix                                                                  |
| ---------------------------------------------------------- | -------------------------------------------------------------------- |
| `[project.theme] sets logo / favicon / palette`            | Remove it, unless the site needs a different logo                    |
| `set site_url`                                             | Link previews, canonical URLs and analytics need it                  |
| `set edit_uri`                                             | The Zensical default edit links point to a `master` branch           |
| `set tagline in [project.extra.iscc]`                      | It is the second part of the home page title                         |
| `set product in [project.extra.iscc] or repo_name`         | Without a name, the header has no product wordmark                   |
| `add docs/for-coding-agents.md`                            | Write it with the `docs-for-agents` skill. See [Writing pages](writing.md#for-coding-agents) |
| `list for-coding-agents.md in nav`                         | Add `{ "For Coding Agents" = "for-coding-agents.md" }` as the last entry |
| `[project.extra.analytics] replaces Plausible`             | All ISCC sites use Plausible                                         |
| `analytics domain … differs from the site_url host`        | Remove `domain`, unless the site must count visits under a different host |
| `the site is not built`                                    | Build the site. Until then, the check examines only the configuration |

## Third-party requests

Pages request nothing from third parties, except Plausible analytics and, if chat is on, iscc.ai. The theme
supplies the fonts and GLightbox. Without the theme copy, the Zensical bundle loads GLightbox from unpkg.com, and
privacy tools such as Privacy Badger flag unpkg.com as a tracker.

The check cannot see these requests:

- For a page with a Mermaid diagram, the bundle loads Mermaid from unpkg.com, so the check rejects these pages. To
    allow them, the theme must supply its own copy of Mermaid, as it does for GLightbox.
- The bundle loads GLightbox on each page that has lightbox links in its content. With `navigation.instant`, the
    bundle can open a lightbox page without a full page load. Then it loads GLightbox from unpkg.com, so the check
    rejects this feature.
- The chat widget loads the fonts that iscc.ai declares in its `public/theme.json`.
- If `repo_url` is set, the bundle gets the stars, forks and latest release of the repository from
    `api.github.com`. ISCC sites are on GitHub Pages, so GitHub is not a third party for them. This request stays.
