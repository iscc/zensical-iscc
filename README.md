# zensical-iscc

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/iscc/zensical-iscc)

ISCC theme for [Zensical](https://zensical.org/) documentation sites. It applies the ISCC identity (Edition 01,
September 2026) on top of Zensical's modern Material variant and carries the widgets the ISCC sites share: the "Copy
page" split button, a "Projects" menu that links related ISCC sites, the iscc.ai chat widget and Plausible
analytics. The `zensical-iscc` command builds a site with
the Markdown copies that "Copy page" reads and checks that the site uses the theme as intended.

## Using the theme in a site

Install it from GitHub into the dependency group that holds the docs tools. The theme pins the Zensical version it
is tested with, so the site does not require Zensical itself.

```toml
[dependency-groups]
docs = ["zensical-iscc"]

[tool.uv.sources]
zensical-iscc = { git = "https://github.com/iscc/zensical-iscc", tag = "v0.2.0" }
```

Select the theme in `zensical.toml`. [`demo/zensical.toml`](demo/zensical.toml) is the complete reference
configuration, with the per-site values marked `# site`.

```toml
[project.extra.iscc]
tagline = "International Standard Content Code" # home page title suffix
copy_page = true                                # default true
chat = true                                     # default false
# og_image = "assets/iscc/social-share.png"       # default
# product = "monitor"                             # default: repo_name without "iscc/" and "iscc-"

# Related ISCC sites for the header's "Projects" menu, recommended; see "Related projects menu"
[[project.extra.iscc.related]]
name = "ISCC Search"
link = "https://search.iscc.codes/"
description = "Similarity search engine for ISCC codes"

# Plausible analytics are on by default; this table is only needed to change them
# [project.extra.analytics]
# domain = "iscc.codes"                             # default: the host name of site_url
# src = "https://stats.iscc.codes/js/plausible.js"  # default

[project.theme]
name = "zensical_iscc"
# custom_dir = "docs/overrides"  # optional site-specific overrides on top of the theme
# features = [...]               # optional; replaces the theme's default feature list
```

The theme sets `font = false` and serves the brand fonts itself. Do not set `theme.logo`, `theme.favicon` or
`theme.palette` unless a site needs a different mark. A site's `custom_dir` must not contain `main.html`: that file
would replace the theme's own; page templates can extend it with `{% extends "main.html" %}`.

Every ISCC site counts visits with Plausible under the host name of its `site_url`; register that host at
stats.iscc.codes. A site without `site_url` gets no analytics.

The header leads with the brand kit's product wordmark lockup: the ISCC signature, a hairline and the product name
in Readex Pro Bold with a coral point, such as "ISCC | monitor." The name is `product`, or else `repo_name` without
its owner and the `iscc-` prefix, so `iscc/iscc-monitor` gives `monitor`; it must be lowercase words joined by
hyphens. `zensical-iscc build` draws the lockup from the theme's copies of the kit's font and signature, the same
construction as the kit's `source/products.py`, and writes it to `assets/iscc/product.svg`. Under `zensical serve`,
which skips that step, on screens narrower than 720px and on sites without a product name, the header shows the
plain ISCC signature and the site name instead.

Build and check:

```bash
uv run zensical-iscc build             # zensical build, then the Markdown copies of every page
uv run zensical-iscc check --strict    # configuration and built site; non-zero exit on findings
```

`zensical-iscc markdown` writes the Markdown copies into an already built site. "Copy page" and "View as Markdown"
read `index.md` next to each rendered page, and `llms-full.txt` at the site root holds all pages in navigation
order. The chat widget mounts only on origins that the iscc.ai token endpoint allows, so it stays silent on
localhost.

## Related projects menu

ISCC is a family of sites that work together: the specification, the hub, search, the web generator, the monitor
and more. Readers move between them, so every site should list its relatives in the header's "Projects" menu: the
sites it talks to, the specification at iscc.codes, and the site itself.

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

- Each table adds one entry, in order, with its `name`, an https `link` and a one-line `description`. Write the
    description for this site's readers: what the other site does for them, in under 60 characters.
- An entry whose link is the site's own `site_url` carries the coral current-site marker. Listing the site itself
    keeps the menu the same on every site of a group and shows readers where they are.
- A site without entries has no menu.
- The menu is a grid icon, labelled "Projects" from 960px up. It opens on hover, focus or tap and needs no
    JavaScript; on phones it spans the screen below the header bar.
- `zensical-iscc check` reports entries that lack a field, links that are not https and `[project.extra.iscc.related]`
    written with single brackets.

## Page components

Besides restyling Zensical's own elements, the theme styles a few ISCC page components:

| Class                                                                 | Use                                                                                                                                   |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `.iscc-lead`                                                          | Opening paragraph set apart by size: `{ .iscc-lead }` on the line after the paragraph                                                 |
| `.iscc-btn`, `.iscc-btn--primary`                                     | Calls to action on a link, styled like Zensical's `.md-button`, spaced for a row: `[Start](start.md){ .iscc-btn .iscc-btn--primary }` |
| `.iscc-cards`, `.iscc-card`                                           | Grid of audience cards, three across on wide screens; each card holds an `h3`, text and a closing paragraph with one link             |
| `.iscc-unit--meta`, `--semantic`, `--content`, `--data`, `--instance` | ISCC-UNIT labels in their unit colours                                                                                                |

Cards need `md_in_html`:

```html
<div class="iscc-cards" markdown="">
 <div class="iscc-card" markdown="">
  ### Developers

Generate ISCC codes from your own code.

[Get started →](start.md)
 </div>
</div>
```

The demo's [components page](demo/docs/components.md) shows all of them.

## Navigation icons

Every page carries an icon in front of its navigation entry, set in its front matter:

```markdown
---
icon: lucide/rocket
---
```

Use names from the [Lucide](https://lucide.dev/icons/) set. Zensical inlines the icon as SVG, so it adds no
request. Section labels in `nav` carry no icon; only pages do.

## For coding agents

[`skills/iscc-docs-theme/SKILL.md`](skills/iscc-docs-theme/SKILL.md) is the procedure for setting up, migrating,
upgrading and checking the theme in an ISCC project, with a GitHub Actions template next to it. Install it in
Claude Code:

```
/plugin install zensical-iscc --marketplace iscc/zensical-iscc
```

Other agents can be pointed at the file directly.

## Third-party requests

Pages request nothing from third parties except Plausible analytics and, with chat enabled, iscc.ai. Fonts and GLightbox are served by the theme; Zensical's bundle would otherwise load GLightbox
from unpkg.com, which privacy tools such as Privacy Badger flag as a tracker. `zensical-iscc check` reports
resources from other origins in the built HTML and CSS. Keep it that way when adding content:

- Store images and badges under the site's `docs/` tree instead of hot-linking them.
- The bundle fetches Mermaid from unpkg.com when a page contains a Mermaid diagram. The check rejects such pages;
    vendor Mermaid the same way as GLightbox before allowing them.
- GLightbox is loaded per page, keyed on lightbox anchors in the content. Do not enable `navigation.instant`: the
    bundle would then reach a lightbox page without a full load and fall back to unpkg.com.
- The chat widget loads the fonts declared in iscc.ai's `public/theme.json`.

When `repo_url` is set, the bundle also asks `api.github.com` for the repository's stars, forks and latest release
to show them in the header. ISCC sites are hosted on GitHub Pages, so GitHub is not a third party to them, and the
request stays.

## Layout

| Path                                                                 | Purpose                                                                                                            |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `zensical_iscc/theme/mkdocs_theme.yml`                               | Theme defaults: fonts off (self-hosted), favicon, features, palette                                                |
| `zensical_iscc/theme/main.html`                                      | Brand stylesheets, social metadata, redirects, widget configuration                                                |
| `zensical_iscc/theme/partials/logo.html`                             | Primary signature in both colourways, switched by scheme                                                           |
| `zensical_iscc/theme/partials/header.html`                           | Zensical's header verbatim plus the related projects menu; a test compares it with Zensical's copy                 |
| `zensical_iscc/theme/partials/projects.html`                         | Related projects menu, from `[[project.extra.iscc.related]]`                                                       |
| `zensical_iscc/theme/partials/integrations/analytics.html`           | Makes Plausible the default analytics provider                                                                     |
| `zensical_iscc/theme/partials/integrations/analytics/plausible.html` | Plausible analytics provider                                                                                       |
| `zensical_iscc/theme/assets/iscc/tokens/iscc.css`                    | Identity tokens, verbatim from the brand kit (`build/tokens/iscc.css`)                                             |
| `zensical_iscc/theme/assets/iscc/theme.css`                          | Maps tokens onto Zensical variables and styles components                                                          |
| `zensical_iscc/theme/assets/iscc/fonts/`                             | Readex Pro and JetBrains Mono WOFF2 subsets with OFL notices                                                       |
| `zensical_iscc/theme/assets/iscc/vendor/glightbox/`                  | GLightbox 3.3.1 (MIT), loaded on pages with lightbox anchors so Zensical's bundle does not fetch it from unpkg.com |
| `zensical_iscc/theme/assets/iscc/logos/`                             | Signature and symbol SVGs from the brand kit                                                                       |
| `zensical_iscc/theme/assets/iscc/favicon.svg`, `favicon.ico`         | Favicon as on iscc.io: the near-black symbol with its coral circle on a transparent ground                         |
| `zensical_iscc/theme/assets/iscc/apple-touch-icon.png`               | App tile from the brand kit: white symbol, coral circle, near-black ground                                         |
| `zensical_iscc/theme/assets/iscc/social-share.png`                   | Default Open Graph image                                                                                           |
| `zensical_iscc/theme/assets/iscc/circle-rhythm-*.svg`                | Decorative pattern for landing or footer bands                                                                     |
| `zensical_iscc/theme/assets/iscc/grain.png`                          | Grain texture of the header bar, from iscc-web                                                                     |
| `zensical_iscc/theme/assets/iscc/copypage.js`                        | "Copy page", "View as Markdown", "Edit on GitHub"                                                                  |
| `zensical_iscc/theme/assets/iscc/copilot.js`, `copilot.css`          | iscc.ai chat widget loader and shadow-DOM styles                                                                   |
| `zensical_iscc/*.py`                                                 | The `zensical-iscc` command and the theme entry point                                                              |
| `zensical_iscc/wordmark.py`                                          | Product wordmark lockup, ported from the brand kit's `source/products.py`                                          |
| `tests/fixtures/products/`                                           | The kit's lockups for web, hub, search and monitor, which the port must reproduce byte for byte                    |
| `demo/`                                                              | Demo and reference site                                                                                            |
| `skills/iscc-docs-theme/`                                            | Agent skill and docs workflow template                                                                             |

Zensical copies every file of the theme directory that is not a template into the built site, so `theme/` holds no
Python code; the `mkdocs.themes` entry point names an object whose `__file__` lies in `theme/`. Zensical still
copies `mkdocs_theme.yml` to the site root.

Brand assets are copied from the private ISCC brand kit (`../iscc-brand`). Refresh them from there rather than
editing the copies. The favicon is the one exception: ISCC websites use the transparent near-black/coral symbol
instead of the kit's framed white/coral tile, so refresh `favicon.svg` and `favicon.ico` from
`../iscc-io/public/`. The header's `grain.png` comes from `../iscc-web/frontend/assets/`. The wordmark fixtures
come from the kit's `build/products/`; when the kit's font, signature or `products.py` changes, refresh them and
port the change to `wordmark.py`.

## Design decisions

- Light scheme: paper canvas, near-black text, white fields and code blocks with thin rules. Dark scheme:
    near-black canvas, navy code blocks, Sky Blue links.
- Header, after the iscc-web top bar and the same in both schemes: Deep Navy with a grain texture, 64px high, the
    product wordmark lockup in white/coral with 1 h at 30px (the brand minimum is 14px), controls in 78% white. Its
    content shares the body's edges: the logo starts at the navigation, the repository widget ends with the content
    column. Where the lockup is absent, the plain signature and the site name in spaced Light capitals stand in; on
    phones the signature stands alone.
- Blue is the link colour. Coral marks the chevron of the primary button, the current-page marker in navigation,
    text selection and the logo circle. Text does not sit on coral; the iscc.ai chat button is the one exception.
- Type: body copy in Readex Pro Light at 16px on every screen width, as the theme holds Zensical's root size at
    125%; the lead paragraph in the same weight at 1.2em; running text stops at about 75 characters per line, while tables,
    code and cards use the full column.
- Buttons follow the brand kit's button system: JetBrains Mono capitals, 46px high. The primary button is a pointed
    near-black block with a white label and a coral chevron, white with a near-black label in the dark scheme; the
    secondary button is a 1.5px outline in the text colour.
- Admonitions are labelled and coloured by role: note and info Sky Blue, tip and success Lime, warning Yellow,
    danger Coral. The dark scheme uses a left rule and coloured title instead of a filled field.
- Table headers, section labels and the footer directions use small JetBrains Mono capitals.
- ISCC-UNIT labels (`.iscc-unit--*`) always pair the colour with the unit name.
- Motion: 160 ms ease-out, disabled under `prefers-reduced-motion`.

## Development

```bash
uv sync                  # dev dependencies
uv run prek install      # git hooks (once per clone)
uv run poe all           # format, type check, test
uv run poe ci            # all gates without modifying files, including the demo site check
uv run poe demo          # build the demo site and serve it on 127.0.0.1:45472
```

Check the demo site in both colour schemes after every change to the theme or to the Zensical version.

To release, set `version` in `pyproject.toml`, merge to `main`, then tag and publish the release with notes that
name the pinned Zensical version:

```bash
git tag vX.Y.Z && git push origin vX.Y.Z
gh release create vX.Y.Z --title vX.Y.Z --notes "..."
```

Sites move to the release by changing the `tag` in their `[tool.uv.sources]`.

## License

The code, templates and stylesheets are licensed under the Apache License 2.0. The bundled fonts are licensed under
the SIL Open Font License (notices in `fonts/`) and GLightbox under the MIT License. The ISCC logos and symbols are
brand assets of the ISCC Foundation for use on ISCC sites.
