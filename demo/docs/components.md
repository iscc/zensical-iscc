---
description: The page elements ISCC documentation uses, styled by the ISCC theme
---

# Components

Every element below is styled by the theme. Check this page in both colour schemes after a theme or Zensical change.

## Text

Body copy with **strong**, *emphasis*, `inline code`, a [link](index.md) and an abbreviation: ISCC.

*[ISCC]: International Standard Content Code

> A block quote with a single sentence.

Content-Code
:   A definition list entry, here for an ISCC-UNIT.

Footnotes render at the end of the page.[^1]

[^1]: The footnote text.

## ISCC-UNIT labels

<span class="iscc-unit--meta">Meta-Code</span>, <span class="iscc-unit--semantic">Semantic-Code</span>,
<span class="iscc-unit--content">Content-Code</span>, <span class="iscc-unit--data">Data-Code</span> and
<span class="iscc-unit--instance">Instance-Code</span>.

## Admonitions

!!! note

    Note and info are Sky Blue.

!!! tip

    Tip and success are Lime.

!!! warning

    Warning is Yellow.

!!! danger

    Danger is Coral.

??? info "Collapsible"

    Details collapse with `???`.

## Code

```python
import iscc_core as ic

code = ic.gen_meta_code("Title", "Description")
print(code["iscc"])
```

=== "Python"

    ```python
    print("tabbed code")
    ```

=== "Shell"

    ```bash
    echo "tabbed code"
    ```

## Tables

| Unit     | Header    | Bits |
| -------- | --------- | ---- |
| Meta     | `0000...` | 64   |
| Content  | `0010...` | 64   |
| Instance | `0100...` | 64   |

## Buttons

[Primary](index.md){ .md-button .md-button--primary }
[Secondary](index.md){ .md-button }
