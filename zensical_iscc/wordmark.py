"""Compose the brand kit's product wordmark lockup for a site's product name.

A port of the signed-before lockup from the brand kit's `source/products.py`: the ISCC primary signature, a
hairline 1 h tall and 0.04 h wide in the word colour at 50 % opacity, 0.3 h of space on each side, then the
product name in Readex Pro Bold with a tracking of -10/1000 em and a coral point. h is the height of the ISCC
symbol, which equals the ascender height of the word. Clear space is the ISCC logo's own, 0.25 x.

The signature masters and the Bold font are the theme's copies of the kit files, so the output matches the
kit's `build/products/` files byte for byte; `tests/test_wordmark.py` guards that. Keep the arithmetic in the
same order as the kit's, since coordinates are rounded to two decimals.
"""

import re
import xml.etree.ElementTree as ET
from functools import cache
from pathlib import Path  # noqa: F401 (used in type comments)
from typing import Any  # noqa: F401 (used in type comments)

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont

from zensical_iscc import THEME_DIR

ASSETS = THEME_DIR / "assets" / "iscc"
FONT = ASSETS / "fonts" / "readex-pro-700.woff2"
TREATMENTS = {"black-coral": ("#212529", "#F56169"), "white-coral": ("#FFFFFF", "#F56169")}
TRACKING = -0.01  # em
POINT = 1.24  # stem widths
RULE_GAP, RULE_WIDTH = 0.3, 0.04  # h
NAME_RE = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
NS = {"s": "http://www.w3.org/2000/svg"}
OUTPUT = "assets/iscc/product.svg"
HEADER_H = 30  # CSS px of 1 h in the header; the brand minimum is 14


def fmt(value):
    # type: (float) -> str
    """Format a coordinate with at most two decimals, as the kit does."""
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


def is_valid(name):
    # type: (str) -> bool
    """Tell whether the wordmark rule covers a name: lowercase words joined by hyphens, without iscc."""
    return bool(NAME_RE.fullmatch(name)) and not name.startswith("iscc")


def product_name(config):
    # type: (dict) -> str | None
    """Return the site's product name: `[project.extra.iscc] product`, else `repo_name` without iscc-."""
    explicit = config.get("extra", {}).get("iscc", {}).get("product")
    if explicit is not None:
        return explicit
    derived = (config.get("repo_name") or "").rsplit("/", 1)[-1].lower().removeprefix("iscc-")
    return derived if is_valid(derived) else None


def master(treatment):
    # type: (str) -> Path
    """Return the path of a signature master."""
    return ASSETS / "logos" / f"iscc-logo-{treatment}.svg"


def path_bounds(d):
    # type: (str) -> tuple[float, float, float, float]
    """Return the ink bounds of path data."""
    pen = BoundsPen(None)
    parse_path(d, pen)
    return pen.bounds


def attr(root, path, key):
    # type: (ET.Element, str, str) -> str
    """Return an attribute of the first element at a path in a master."""
    return root.findall(path, NS)[0].attrib[key]


@cache
def signature_geometry():
    # type: () -> dict[str, float]
    """Read the symbol and wordmark bounds of the primary signature master, in master units."""
    root = ET.parse(master("black-coral")).getroot()  # noqa: S314 (the theme's own master, not untrusted input)
    sx0, sy0, sx1, sy1 = path_bounds(attr(root, "s:g/s:path", "d"))
    cx, cy, r = (float(attr(root, "s:g/s:circle", k)) for k in ("cx", "cy", "r"))
    _, _, wx1, _ = path_bounds(attr(root, "s:path", "d"))
    left, top, bottom = min(sx0, cx - r), min(sy0, cy - r), max(sy1, cy + r)
    return {"left": left, "top": top, "bottom": bottom, "right": wx1, "clear": (sx1 - sx0) / 4}


def signature_body(treatment):
    # type: (str) -> str
    """Return the drawing elements of a signature master, without its title, description or ids."""
    text = master(treatment).read_text(encoding="utf-8")
    body = text[text.index(">", text.index("<svg")) + 1 : text.rindex("</svg>")]
    body = re.sub(r"<title.*?</title>|<desc.*?</desc>|<!--.*?-->", "", body, flags=re.S)
    return re.sub(r'\s(id|aria-[a-z]+)="[^"]*"', "", body).strip()


@cache
def face():
    # type: () -> tuple
    """Load the Bold face: glyph set, character map, cap height and em size in font units."""
    font = TTFont(FONT)
    cap_units = font["OS/2"].sCapHeight  # pyright: ignore[reportAttributeAccessIssue]
    em = font["head"].unitsPerEm  # pyright: ignore[reportAttributeAccessIssue]
    return font.getGlyphSet(), font.getBestCmap(), cap_units, em


def glyph(char):
    # type: (str) -> Any
    """Return the glyph of one character."""
    glyphs, cmap, _, _ = face()
    return glyphs[cmap[ord(char)]]


def box(char):
    # type: (str) -> tuple[float, float, float, float]
    """Return the font-unit ink bounds of one character."""
    pen = BoundsPen(face()[0])
    glyph(char).draw(pen)
    return pen.bounds


def outline(char, cap, x):
    # type: (str, float, float) -> str
    """Return path data for a character at a cap height with its baseline origin at (x, 0)."""
    s = cap / face()[2]
    pen = SVGPathPen(face()[0], fmt)
    glyph(char).draw(TransformPen(pen, (s, 0.0, 0.0, -s, x, 0)))
    return pen.getCommands()


def word_metrics(h):
    # type: (float) -> dict[str, float]
    """Return the cap height, unit, tracking, point size and point gap that give the word an ascender of h."""
    _, _, cap_units, em = face()
    cap = h * cap_units / box("l")[3]
    unit = cap / cap_units
    stem = box("l")
    return {
        "cap": cap,
        "unit": unit,
        "tracking": TRACKING * (cap * em / cap_units),
        "point": POINT * (stem[2] - stem[0]) * unit,
        "point_gap": box(".")[0] * unit,
    }


def draw_word(name, x, h, ink, point):
    # type: (str, float, float, str, str) -> tuple[str, float]
    """Return the outlined name and its coral point with the baseline at y 0, and the ink width."""
    m, cap_units = word_metrics(h), face()[2]
    d, advance = [], x
    for ch in name:
        d.append(outline(ch, m["cap"], advance))
        advance += glyph(ch).width * m["cap"] / cap_units + m["tracking"]
    end = advance - m["tracking"] + m["point_gap"]
    r = m["point"] / 2
    drawn = (
        f'<path fill="{ink}" d="{"".join(d)}"/><circle cx="{fmt(end + r)}" cy="{fmt(-r)}" r="{fmt(r)}" fill="{point}"/>'
    )
    return drawn, end + m["point"] - x


def descent(name, h):
    # type: (str, float) -> float
    """Return how far the name's ink reaches below the baseline."""
    return max(0.0, -min(box(ch)[1] for ch in name) * word_metrics(h)["unit"])


def compose(name, treatment="white-coral", display_h=None):
    # type: (str, str, float | None) -> str
    """Return the signed-before lockup SVG; with `display_h`, sized so that 1 h is that many CSS px."""
    if not is_valid(name):
        raise ValueError(f"expected a lowercase repository name without the iscc- prefix, got {name!r}")
    g = signature_geometry()
    h = g["bottom"] - g["top"]
    ink, point = TREATMENTS[treatment]
    rule_x = g["right"] - g["left"] + RULE_GAP * h
    x = rule_x + RULE_WIDTH * h + RULE_GAP * h
    drawn, width = draw_word(name, x, h, ink, point)
    signature = f'<g transform="translate({fmt(-g["left"])} {fmt(-g["bottom"])})">{signature_body(treatment)}</g>'
    rule = (
        f'<rect x="{fmt(rule_x)}" y="{fmt(-h)}" width="{fmt(RULE_WIDTH * h)}" height="{fmt(h)}" '
        f'fill="{ink}" fill-opacity="0.5"/>'
    )
    pad = g["clear"]
    w, ht = x + width + 2 * pad, descent(name, h) + h + 2 * pad
    scale = display_h / h if display_h else 1
    label = f"ISCC {name}"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(w * scale)}" height="{fmt(ht * scale)}" '
        f'viewBox="{fmt(-pad)} {fmt(-h - pad)} {fmt(w)} {fmt(ht)}" role="img" aria-label="{label}">'
        f"<title>{label}</title>{signature + rule + drawn}</svg>\n"
    )


def write(site_dir, name):
    # type: (Path, str) -> Path
    """Write the header lockup for a product name into a built site and return its path."""
    path = site_dir / OUTPUT
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(compose(name, "white-coral", HEADER_H), encoding="utf-8")
    return path
