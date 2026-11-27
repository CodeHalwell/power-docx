# Page-Aware Layout

Word documents use **flow layout**: unlike PowerPoint's fixed canvas, content
reflows across pages based on each section's **text column** (page dimensions
minus margins and gutter) and pagination rules.

Designing programmatically without checking the text column produces the most
common agent-generated `.docx` bugs: tables spilling into the right margin,
images clipped at the page edge, orphan headings stranded at the bottom of a
page, and awkward whitespace before large tables.

## 1. Always compute the section's text column first

```python
from power_docx import Document
from power_docx.shared import Emu, Inches

def text_column_width(section) -> Emu:
    """Usable horizontal width inside a section's margins and gutter."""
    return Emu(
        (section.page_width or 0)
        - (section.left_margin or 0)
        - (section.right_margin or 0)
        - (section.gutter or 0)
    )

def text_column_height(section) -> Emu:
    """Usable vertical body height inside a section's top and bottom margins."""
    return Emu(
        (section.page_height or 0)
        - (section.top_margin or 0)
        - (section.bottom_margin or 0)
    )

doc = Document()
sec = doc.sections[0]
# default.docx starts with 1.25" L/R margins (6.0" column). Normalize explicitly:
sec.left_margin = Inches(1.0)
sec.right_margin = Inches(1.0)
sec.top_margin = Inches(1.0)
sec.bottom_margin = Inches(1.0)

col_w = text_column_width(sec)   # 6.5" on US Letter
col_h = text_column_height(sec)  # 9.0" on US Letter
```

### Standard page sizes at a glance

| Paper | Size | With `1.0"` margins | With `0.75"` margins |
|---|---|---|---|
| US Letter (portrait) | `8.5" x 11.0"` | `6.5" x 9.0"` | `7.0" x 9.5"` |
| US Letter (landscape) | `11.0" x 8.5"` | `9.0" x 6.5"` | `9.5" x 7.0"` |
| A4 (portrait) | `210 mm x 297 mm` (`8.27" x 11.69"`) | `159 mm x 246 mm` | `172 mm x 259 mm` |
| A4 (landscape) | `297 mm x 210 mm` | `246 mm x 159 mm` | `259 mm x 172 mm` |

## 2. Size tables strictly to the text column

Compute column widths as proportions of `text_column_width(section)` so they
never overflow, and apply them to both `table.columns[i].width` and every
`cell.width` with `table.autofit = False`:

```python
from power_docx import Document
from power_docx.shared import Emu

def add_fitted_table(doc, section, col_weights, style="Table Grid"):
    """Create a 1-row table whose columns sum to the section's text column."""
    total_weight = sum(col_weights)
    col_w = Emu(
        section.page_width
        - section.left_margin
        - section.right_margin
        - (section.gutter or 0)
    )
    widths = [Emu(int(col_w * (w / total_weight))) for w in col_weights]
    # Give any integer-rounding remainder to the last column
    widths[-1] = Emu(col_w - sum(widths[:-1]))

    table = doc.add_table(rows=1, cols=len(widths), style=style)
    table.autofit = False
    for idx, width in enumerate(widths):
        table.columns[idx].width = width
        table.rows[0].cells[idx].width = width
    return table, widths
```

For wide tables with 6+ columns, switch to a **landscape section** rather than
cramming tiny columns onto a portrait page:

```python
from power_docx import Document
from power_docx.enum.section import WD_ORIENT, WD_SECTION

doc = Document()
sec = doc.add_section(WD_SECTION.NEW_PAGE)
sec.orientation = WD_ORIENT.LANDSCAPE
sec.page_width, sec.page_height = sec.page_height, sec.page_width
sec.header.is_linked_to_previous = False
```

## 3. Clamp images to the text column

Always bound picture width by `text_column_width(section)` (and leave extra
margin when placing inside a table cell):

```python
from power_docx import Document
from power_docx.shared import Emu, Inches

doc = Document()
sec = doc.sections[0]
max_w = Emu(sec.page_width - sec.left_margin - sec.right_margin - (sec.gutter or 0))
desired_w = Inches(6.0)
doc.add_picture("chart.png", width=min(desired_w, max_w))
```

## 4. Pagination hygiene

Apply these rules globally on your styles so Word lays out pages cleanly:

- **No orphan headings:** Set `keep_with_next = True` on `Heading 1`–`Heading 3`
  and on figure/table lead-in paragraphs.
- **No single-line widows/orphans:** Set `widow_control = True` on `Normal` and
  body text styles.
- **Keep short callouts/blocks intact:** Set `keep_together = True` on callout
  boxes, quotes, and code blocks so they don't split awkwardly across a page
  boundary.
- **Deliberate chapter starts:** Use `paragraph_format.page_break_before = True`
  on major section headings instead of inserting stray blank paragraphs.

```python
from power_docx import Document

doc = Document()
doc.styles["Normal"].paragraph_format.widow_control = True
for level in (1, 2, 3):
    doc.styles[f"Heading {level}"].paragraph_format.keep_with_next = True
```

## 5. Round-trip verification

Before declaring a generated `.docx` done, reload it from disk (or `BytesIO`)
and verify the structure and dimensions:

```python
from io import BytesIO
from power_docx import Document

def verify_round_trip(doc) -> Document:
    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return Document(buf)
```

## Roadmap note

`power-docx` is actively building first-class page-aware primitives on top of
this core API (see `ROADMAP.md`):

- **Phase 2 (`2.2.0`)**: `layout.py` section content box,
  `Document.content_width`, column-safe `add_picture`, table column-width
  helpers.
- **Phase 3 (`2.3.0`)**: `document.lint()`, `tidy()`, `audit()`, and
  `power-docx lint` CLI.
- **Phase 4 (`2.4.0`)**: Pillow-backed font registry and line/page estimator.
- **Phase 5–7 (`2.5.0`–`2.7.0`)**: declarative `compose.from_spec`,
  `DesignTokens`, and `render.py` / `power-docx review`.

Until those phases ship, use the verified helpers above against the current
`power_docx` API.
