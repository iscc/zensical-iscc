"""ISCC theme for Zensical documentation sites.

The theme files live in `theme/`. Zensical finds an installed theme through the
`mkdocs.themes` entry point and uses the directory of the loaded object's
`__file__`. It also copies every non-template file of that directory into the
built site, Python files included, so the entry point names `THEME` instead of
a module and `theme/` stays free of Python code.
"""

from pathlib import Path
from types import SimpleNamespace

THEME_DIR = Path(__file__).parent / "theme"
THEME = SimpleNamespace(__file__=str(THEME_DIR / "mkdocs_theme.yml"))
