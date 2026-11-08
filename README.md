# zensical-iscc

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/iscc/zensical-iscc)

The ISCC theme for [Zensical](https://zensical.org/) documentation sites. The package contains:

- the theme, with the ISCC brand and the page tools that all ISCC sites share
- the `zensical-iscc` command, which builds and checks a site
- agent skills that set up the theme in a project and write its page for coding agents

**Documentation: <https://theme.iscc.codes/>**. This repository builds it with the theme. Its
[`zensical.toml`](zensical.toml) is the reference configuration for all ISCC sites.

## Use the theme in a site

```toml
[dependency-groups]
docs = ["zensical-iscc"]

[tool.uv.sources]
zensical-iscc = { git = "https://github.com/iscc/zensical-iscc", tag = "vX.Y.Z" }
```

```bash
uv run zensical-iscc build             # zensical build, then Markdown copies, llms.txt, project logo
uv run zensical-iscc check --strict    # check configuration and built site; exit 1 on findings
```

[Get started](https://theme.iscc.codes/get-started/) tells you how to configure the site, write pages and deploy
them.

## For coding agents

This repository is a Claude Code plugin marketplace. Its plugin has two skills:

- `iscc-docs-theme` sets up, migrates, upgrades and checks the theme in an ISCC project.
- `docs-for-agents` writes the "For Coding Agents" page of an ISCC site.

```
/plugin marketplace add iscc/zensical-iscc
/plugin install zensical-iscc@zensical-iscc
```

Other agents can follow [`skills/iscc-docs-theme/SKILL.md`](skills/iscc-docs-theme/SKILL.md) or start at
<https://theme.iscc.codes/llms.txt>.

## Development

```bash
uv sync                  # install the dev dependencies
uv run prek install      # install the git hooks, one time for each clone
uv run poe all           # format, type check, test
uv run poe ci            # run all gates without changes to files, with the docs site check
uv run poe docs          # build the docs site and serve it on 127.0.0.1:45472
```

[Development](https://theme.iscc.codes/development/) describes the repository layout, the copied files, Zensical
upgrades and releases. [`CHANGELOG.md`](CHANGELOG.md) lists the releases.

## License

The code, templates and stylesheets are licensed under the Apache License 2.0. The bundled fonts are licensed under
the SIL Open Font License (notices in `fonts/`) and GLightbox under the MIT License. The ISCC logos and symbols are
brand assets of the ISCC Foundation for use on ISCC sites.
