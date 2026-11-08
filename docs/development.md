---
icon: lucide/wrench
description: Commands, layout, copied files, upgrades and releases for work on the theme
---

# Development

The theme is in [iscc/zensical-iscc](https://github.com/iscc/zensical-iscc). This site comes from the same
repository, so each theme change shows here first.

## Commands

```bash
uv sync                  # install the dev dependencies
uv run prek install      # install the git hooks, one time for each clone
uv run poe all           # format, type check, test
uv run poe ci            # run all gates without changes to files, with the check of this site
uv run poe docs          # build this site and serve it on 127.0.0.1:45472
```

The tests build copies of this site with Zensical. They need 100% branch coverage. After each change to the theme
or to the Zensical version, look at this site in both color schemes.

## Layout

| Path                                                     | Contents                                                                         |
| -------------------------------------------------------- | -------------------------------------------------------------------------------- |
| `zensical_iscc/theme/mkdocs_theme.yml`                   | Theme defaults: fonts off, favicon, features, palette                            |
| `zensical_iscc/theme/main.html`                          | Brand stylesheets, social metadata, Markdown link, redirects, widget settings    |
| `zensical_iscc/theme/partials/logo.html`                 | The project logo and the ISCC logo in both color versions                        |
| `zensical_iscc/theme/partials/header.html`               | The Zensical header plus the "Projects" menu. A test compares it with the Zensical header |
| `zensical_iscc/theme/partials/projects.html`             | The "Projects" menu, from `[[project.extra.iscc.related]]`                       |
| `zensical_iscc/theme/partials/copyright.html`            | The footer content: ISCC logo, `copyright` text, shared ISCC links, social links |
| `zensical_iscc/theme/partials/social.html`               | Empty. `copyright.html` shows the social links, also without `extra.social`      |
| `zensical_iscc/theme/partials/integrations/analytics*`   | Plausible as the default analytics provider                                      |
| `zensical_iscc/theme/assets/iscc/theme.css`              | Maps the tokens to the Zensical variables and styles the components              |
| `zensical_iscc/theme/assets/iscc/tokens/`, `fonts/`, `logos/` | Copies of the ISCC brand assets: tokens, Readex Pro and JetBrains Mono, logos    |
| `zensical_iscc/theme/assets/iscc/vendor/glightbox/`      | GLightbox 3.3.1, not changed                                                     |
| `zensical_iscc/theme/assets/iscc/copypage.js`            | "Copy page", "View as Markdown", "Edit on GitHub"                                |
| `zensical_iscc/theme/assets/iscc/copilot.js`, `copilot.css` | The loader and styles of the iscc.ai chat widget                                 |
| `zensical_iscc/cli.py`, `markdown.py`, `check.py`, `project.py` | The `zensical-iscc` command                                                      |
| `zensical_iscc/project_logo.py`                          | Draws the project logo                                                           |
| `zensical.toml`, `docs/`                                 | This site and the reference configuration                                        |
| `CHANGELOG.md`                                           | Release notes. A git hook copies them to `docs/changelog.md`                     |
| `skills/iscc-docs-theme/`                                | The setup skill and the docs workflow template for sites                         |
| `skills/docs-for-agents/`                                | The skill for the "For Coding Agents" page                                       |
| `.claude-plugin/marketplace.json`                        | The plugin marketplace. Its one entry points to `skills/`                        |
| `skills/.claude-plugin/`                                 | The plugin manifest and its icon. The plugin version is the package version      |
| `tests/fixtures/project-logos/`                          | Reference project logos. `project_logo.py` must make the same files, byte for byte |

Zensical copies all files of the theme directory that are not templates into the built site, so `theme/` contains
no Python code. The `mkdocs.themes` entry point names an object whose `__file__` is in `theme/`.

## Copied files

Some files are copies. Update them from their source. Do not edit them here.

| Files                                         | Source                                                                    |
| --------------------------------------------- | ------------------------------------------------------------------------- |
| Tokens, fonts, logos, favicons, `grain.png`, the app tile, the plugin icon | ISCC sources that are not public                                          |
| `tests/fixtures/project-logos/`               | The ISCC brand assets. Port changes of the project logo construction to `project_logo.py` |
| `skills/docs-for-agents/SKILL.md`             | `plugins/docs-for-agents/` in [titusz/skills](https://github.com/titusz/skills) |
| `docs/changelog.md`                           | `CHANGELOG.md`, written by the `changelog` git hook                       |

## Upgrade Zensical

`pyproject.toml` pins one Zensical version, because the theme overrides Zensical templates. To upgrade:

1. Change the pin.
1. Build this site. Compare both color schemes with the previous version in a browser.
1. Run the tests.
1. Release.

A test compares `partials/header.html` with the Zensical header. If Zensical changes its header, the test fails.

## Release

1. In `CHANGELOG.md`, change "Unreleased" to the version and the date. Commit the copy that the hook writes.
1. Set `version` in `pyproject.toml` and in `skills/.claude-plugin/plugin.json`. A test makes sure that both
    versions are equal. Users get skill changes only when the plugin version changes, which is at each release.
1. Merge to `main`.
1. Tag and publish the release. In the release notes, give the Zensical version that the release pins:

```bash
git tag vX.Y.Z && git push origin vX.Y.Z
gh release create vX.Y.Z --title vX.Y.Z --notes "..."
```

Sites change to the release with the `tag` in their `[tool.uv.sources]`. This site deploys from `main` to GitHub
Pages on each push that changes it.

## License

The code, templates and stylesheets are licensed under the Apache License 2.0. The bundled fonts are licensed under
the SIL Open Font License and GLightbox under the MIT License. The ISCC logos and symbols are brand assets of the
ISCC Foundation for use on ISCC sites.
