---
icon: lucide/palette
description: How the theme applies the ISCC brand to Zensical, and why
---

# Design

The theme applies the ISCC brand to the modern Material design of Zensical. The colors, fonts and logos come from
the ISCC brand assets.

## Schemes

| Scheme | Canvas     | Text       | Fields and code                | Links    |
| ------ | ---------- | ---------- | ------------------------------ | -------- |
| Light  | Paper      | Near-black | White, with thin rules         | Blue     |
| Dark   | Near-black | Paper      | Graphite, with thin rules      | Sky Blue |

Readers change the scheme with the sun and moon button. On the first visit, the site uses the scheme of the
operating system.

## Header

The header is the same in both schemes: Deep Navy with a grain texture, 72px high, with controls in 78% white.

- The header starts with the project logo in white and coral, at a symbol height of 24px.
- The page title, which replaces the site name when the page scrolls, sits on the baseline of the logo letters.
- The header content aligns with the columns below. The logo starts at the coral marker of the navigation. The
    search field ends at the right edge of the content column. The repository icon is above the text of the table
    of contents.
- Without a project logo, the header shows the plain ISCC logo and the site name in spaced Light capitals. On
    phones, it shows only the logo.

## Footer

The footer bar is one row, Deep Navy with a grain texture like the header, and 52px high. Its ends align with the
ends of the header.

- On the left: the white ISCC logo, the `copyright` text of the site and "Made with Zensical".
- On the right: the links that all ISCC sites share (ISCC Foundation, Privacy Policy, Imprint, CC BY 4.0), then the
    social links of the site from `[[project.extra.social]]` and the LinkedIn and X pages of the ISCC Foundation.
- Links and icons are 78% white. On hover and focus, they are white.
- On narrow screens, the row wraps.

## Color roles

- Blue is the link color.
- Coral marks the chevron of the primary button, the current page in the navigation, the current site in the
    "Projects" menu, selected text and the circle in the logo.
- Text is never on a coral background. The only exception is the iscc.ai chat button.
- Each admonition type has a color: note and info are Sky Blue, tip and success are Lime, warning is Yellow, danger
    is Coral. In the dark scheme, admonitions have a colored left line and title, not a colored background.
- An ISCC-UNIT label always shows the unit name with its color.

## Type

- Body text is Readex Pro Light at 16px on all screen widths.
- The lead paragraph has the same weight and a larger size, 1.2em.
- Lines of running text stop at about 75 characters. Tables, code and cards use the full width of the column.
- Table headers, section labels and the previous and next labels in the footer use small JetBrains Mono capitals.

## Buttons

The buttons follow the ISCC button design: JetBrains Mono capitals, 46px high.

- **Primary:** a near-black block with a pointed end, a white label and a coral chevron. The chevron moves on hover.
    In the dark scheme, the block is white with a near-black label.
- **Secondary:** an outline of 1.5px in the text color.

[Components](components.md#calls-to-action) shows both.

## Motion

Transitions take 160 ms, with ease-out. They are off when the reader sets `prefers-reduced-motion`.
