---
icon: lucide/rocket
description: Set up the theme for the documentation of an ISCC project, with an agent or by hand
---

# Get started

A site on the theme has three parts:

- A `zensical.toml` file.
- A `docs/` directory with the Markdown pages.
- The `zensical-iscc` package in the docs dependencies of the project.

You need Python 3.11 or newer.

## With a coding agent

The repository is also a Claude Code plugin marketplace. Its plugin has two skills:

| Skill                            | Does                                                                                      |
| -------------------------------- | ----------------------------------------------------------------------------------------- |
| `zensical-iscc:iscc-docs-theme`  | Sets up, migrates, upgrades or checks the theme in a project, also from MkDocs Material   |
| `zensical-iscc:docs-for-agents`  | Writes and updates the [For Coding Agents](writing.md#for-coding-agents) page of the site |

Install the plugin:

```
/plugin marketplace add iscc/zensical-iscc
/plugin install zensical-iscc@zensical-iscc
```

Then, in the project, tell the agent: "Put the docs on the ISCC theme". The skill examines the project. It asks you
for the information that only you have, for example the tagline and whether the site uses the chat widget. When it
is done, the site passes `zensical-iscc check --strict`.

Other agents can follow the steps in
[`skills/iscc-docs-theme/SKILL.md`](https://github.com/iscc/zensical-iscc/blob/main/skills/iscc-docs-theme/SKILL.md).

## By hand

### 1. Add the dependency

Get the latest release tag:

```bash
git ls-remote --tags --refs --sort=-v:refname https://github.com/iscc/zensical-iscc | head -1
```

Add the theme to the dependency group of your docs tools:

```toml
[dependency-groups]
docs = ["zensical-iscc"]

[tool.uv.sources]
zensical-iscc = { git = "https://github.com/iscc/zensical-iscc", tag = "vX.Y.Z" }
```

The theme pins the Zensical version that it is tested with. Remove all direct requirements on `zensical`, `mkdocs`
and `mkdocs-material`. Then run `uv lock` and `uv sync`.

If you do not use uv, install the theme with pip:

```bash
pip install "zensical-iscc @ git+https://github.com/iscc/zensical-iscc@vX.Y.Z"
```

### 2. Configure the site

1. Copy [`zensical.toml`](https://github.com/iscc/zensical-iscc/blob/main/zensical.toml) from the theme
    repository.
1. Replace each value that has the comment `# site`.
1. Add the `nav`, the Markdown extensions and the plugins of your project.

[Configuration](configuration.md) explains each setting. Read its [TOML traps](configuration.md#toml-traps) first.

### 3. Write the pages

Give each page a navigation icon in its front matter. Put the "For Coding Agents" page last in the navigation.
[Writing pages](writing.md) has all conventions. [Components](components.md) shows the elements that the theme
styles.

### 4. Build, check and preview

| Task    | Command                                                                     |
| ------- | --------------------------------------------------------------------------- |
| Build   | `uv run zensical-iscc build`                                                |
| Check   | `uv run zensical-iscc check --strict`                                       |
| Preview | `python -m http.server <port> --directory site` after a build               |
| Draft   | `uv run zensical serve --dev-addr 127.0.0.1:<port>` for live reload         |

`zensical serve` does not run the build steps of the theme. Its preview has no project logo, no "Copy page"
content and no `llms.txt`. To see the real site, serve the built `site/` directory.

### 5. Deploy

1. Copy
    [`docs-workflow.yml`](https://github.com/iscc/zensical-iscc/blob/main/skills/iscc-docs-theme/docs-workflow.yml)
    to `.github/workflows/docs.yml`. The workflow builds and checks the site for each pull request. It deploys
    `main` to GitHub Pages.
1. For a custom domain, put the domain in `docs/CNAME`.
1. Add the host name of the site at stats.iscc.codes. Plausible does not count visits to a host that is not
    registered.

## Upgrade

1. Change the `tag` in `[tool.uv.sources]`.
1. Run `uv lock --upgrade-package zensical-iscc`.
1. Build and check the site.

The [changelog](changelog.md) tells what changed in each release and which Zensical version the release pins.
