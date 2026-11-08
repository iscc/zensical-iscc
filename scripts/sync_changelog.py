"""Copy CHANGELOG.md into the documentation as docs/changelog.md, with the front matter every page carries.

Run by the `changelog` git hook. Exits 1 when it changed the copy, so the commit stops for the copy to be staged.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "CHANGELOG.md"
TARGET = ROOT / "docs" / "changelog.md"
FRONT_MATTER = """---
icon: lucide/history
description: What changed in each release of the ISCC theme
---

"""


def page(changelog):
    # type: (str) -> str
    """Return the documentation page for the text of CHANGELOG.md."""
    return FRONT_MATTER + changelog


def main():
    # type: () -> int
    """Write the copy if it differs and return 1 when it did."""
    expected = page(SOURCE.read_text(encoding="utf-8"))
    if TARGET.is_file() and TARGET.read_text(encoding="utf-8") == expected:
        return 0
    TARGET.write_bytes(expected.encode("utf-8"))
    print(f"wrote {TARGET.relative_to(ROOT).as_posix()} from CHANGELOG.md")
    return 1


if __name__ == "__main__":
    sys.exit(main())
