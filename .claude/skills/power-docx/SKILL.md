---
name: power-docx
description: Create, read, and update Microsoft Word (.docx) files from Python using power-docx — the actively-maintained fork of python-docx. Use this skill whenever the user wants to generate, inspect, mutate, or format Word documents programmatically with page-aware layout: computing the text column, sizing tables and images to fit, managing styles and sections, adding headers/footers, and working with comments.
---

# power-docx

`power-docx` is the actively-maintained fork of `python-docx`, distributed on
PyPI as **`power-docx`** and imported as **`import power_docx`** (side-by-side
installable with upstream `python-docx`). When migrating older snippets, replace
`docx` with `power_docx` in imports.

## The headline: page-aware authoring

Unlike slides (fixed canvas), Word documents are **flow layout**. The "canvas"
for every section is its **text column**:

```python
from power_docx.shared import Emu

def content_width(section) -> Emu:
    """Usable text-column width for a section (page minus margins and gutter)."""
    page_w = section.page_width or 0
    left = section.left_margin or 0
    right = section.right_margin or 0
    gutter = section.gutter or 0
    return Emu(page_w - left - right - gutter)
```

Every table, image, and tab stop you place should be computed from the active
section's text column rather than hard-coded guesses. Read
**`references/page-aware-layout.md`** before building multi-section reports or
data-driven documents.

## Cheat sheet (most common operations)

```python
from power_docx import Document
from power_docx.enum.section import WD_ORIENT, WD_SECTION
from power_docx.enum.style import WD_STYLE_TYPE
from power_docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from power_docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from power_docx.shared import Emu, Inches, Pt, RGBColor

# --- open / create / save ---
doc = Document()                           # blank doc from bundled default.docx
doc = Document("existing.docx")            # open from path or binary file-like object
doc.save("output.docx")                    # save to path or binary file-like object

# --- core properties ---
doc.core_properties.title = "Quarterly Report"
doc.core_properties.author = "Analytics Team"

# --- page geometry (default.docx is 8.5" x 11" with 1.25" L/R margins -> 6.0" column) ---
section = doc.sections[0]
section.left_margin = Inches(1.0)
section.right_margin = Inches(1.0)
col_w = Emu(
    section.page_width - section.left_margin - section.right_margin - (section.gutter or 0)
)

# --- headings & paragraphs ---
doc.add_heading("Executive Summary", level=0)        # Title style
h1 = doc.add_heading("1. Overview", level=1)         # Heading 1
h1.paragraph_format.keep_with_next = True            # prevent orphan headings

p = doc.add_paragraph("Key findings include ")
r = p.add_run("24% YoY growth")
r.bold = True
r.font.color.rgb = RGBColor(0x1B, 0x4F, 0x72)
p.add_run(" across all regions.")

# --- lists (via built-in paragraph styles) ---
doc.add_paragraph("First bullet", style="List Bullet")
doc.add_paragraph("First numbered item", style="List Number")

# --- page break ---
doc.add_page_break()                                 # adds a new paragraph containing a break
# Or inline inside an existing paragraph:
p.add_run().add_break(WD_BREAK.PAGE)

# --- tables sized to the text column ---
table = doc.add_table(rows=1, cols=3, style="Table Grid")
table.autofit = False
table.alignment = WD_TABLE_ALIGNMENT.CENTER
col_widths = [Inches(1.5), Inches(2.5), Inches(2.5)]
for i, heading in enumerate(("Metric", "Actual", "Notes")):
    cell = table.rows[0].cells[i]
    cell.text = heading
    cell.width = col_widths[i]
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

row = table.add_row()
for i, value in enumerate(("Revenue", "$4.2M", "Above forecast")):
    row.cells[i].text = value
    row.cells[i].width = col_widths[i]

# --- images fitted to the text column ---
doc.add_picture("chart.png", width=min(Inches(5.5), col_w))

# --- headers & footers ---
header = section.header
header.paragraphs[0].text = "Quarterly Report — Confidential"
header.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

# --- comments attached to a run ---
target_run = p.runs[1]
doc.add_comment(target_run, text="Verify against Q4 ledger.", author="Reviewer", initials="RV")

# --- traverse paragraphs and tables in document order ---
for block in doc.iter_inner_content():
    print(type(block).__name__)

# --- new landscape section (must swap page_width and page_height too) ---
landscape = doc.add_section(WD_SECTION.NEW_PAGE)
landscape.orientation = WD_ORIENT.LANDSCAPE
landscape.page_width, landscape.page_height = landscape.page_height, landscape.page_width
landscape.header.is_linked_to_previous = False       # unlink before editing
```

## House rules

1. **Always use unit helpers from `power_docx.shared`** — `Inches(...)`,
   `Cm(...)`, `Mm(...)`, `Pt(...)`, `Twips(...)`, `Emu(...)`. Never pass raw
   EMU integers directly.
2. **Always import `power_docx`, never `docx`.** The two packages can be
   installed side-by-side; importing `docx` hits upstream `python-docx` if it is
   present.
3. **Compute sizes from the active section's text column.** Never hard-code a
   `6.5"` table or image without checking the section's margins — the bundled
   `default.docx` template has **`1.25"` left and right margins**, leaving only
   **`6.0"`** of text column until you change them.
4. **Use styles for document hierarchy, runs for inline emphasis.** Configure
   `Heading 1`–`Heading 3`, `Normal`, and custom paragraph styles once rather
   than repeating font/size/spacing on every paragraph.
5. **Keep headings attached to their body copy.** Set
   `paragraph_format.keep_with_next = True` on headings (and caption/intro
   lines) and `widow_control = True` on body paragraphs.
6. **Never mutate XML on read.** Getter properties return `None` when inherited
   or unset; assigning `None` clears the explicit override and restores
   inheritance.
7. **Always verify round-trip.** After generating or editing a `.docx`, reload
   it with `Document(path)` (or `BytesIO`) and inspect paragraphs, tables, and
   sections to confirm the saved package opens cleanly.

## Common pitfalls and anti-patterns

| Pitfall | Why it bites | What to do instead |
|---|---|---|
| Assuming `6.5"` usable width on a fresh `Document()` | Default template is `8.5" x 11"` with **`1.25"`** left/right margins (`6.0"` text column) | Read `section.page_width - section.left_margin - section.right_margin - (section.gutter or 0)`, or set `1.0"` margins explicitly |
| Setting only `table.columns[i].width` | Word ignores `<w:tblGrid>` column widths unless each cell's `<w:tcW>` is also set (and `table.autofit = False`) | Set `table.autofit = False` and set `cell.width` on every cell in the column (plus `table.columns[i].width`) |
| Assigning `paragraph.text = "..."` on a formatted paragraph | Replaces all existing runs and wipes character-level formatting | Mutate individual `run.text`, or call `paragraph.clear()` and rebuild with `add_run(...)` |
| Setting `section.orientation = WD_ORIENT.LANDSCAPE` alone | Word requires explicit swapped dimensions; setting `orientation` alone does not rotate the page | Also swap `section.page_width, section.page_height = section.page_height, section.page_width` |
| Editing `section.header` on section 2+ without unlinking | `is_linked_to_previous` defaults to `True`, so edits overwrite the previous section's header | Set `section.header.is_linked_to_previous = False` before modifying |
| Calling `header.add_table(rows, cols)` without `width` | Unlike `Document.add_table`, `_Header.add_table`, `_Footer.add_table`, and `Comment.add_table` require a third `width` argument | Pass `width=content_width(section)` |
| Using `doc.paragraphs` and `doc.tables` separately to reconstruct order | `doc.paragraphs` and `doc.tables` are separate flat lists and lose interleaving | Use `doc.iter_inner_content()` (or `section.iter_inner_content()` / `cell.iter_inner_content()`) |
| Checking `font.bold` expecting `True`/`False` | Tri-state OOXML property: `True`, `False`, or `None` (inherited from style) | Test explicitly (`is True`, `is False`, `is None`) |
| Passing `width` and `height` together to `add_picture` | Distorts image aspect ratio unless the ratio matches the source image | Pass only `width=...` OR `height=...` to scale proportionally |
| Calling `doc.add_table(...)` without a style | Default `Normal Table` has no visible borders | Pass `style="Table Grid"` (or a template table style) |

## Topic references

Read the focused reference file for the subsystem you are working on:

- **`references/documents-and-sections.md`** — opening/saving, streams, core
  properties, settings, sections, page size/margins/orientation, iterating body
  content in order.
- **`references/styles.md`** — built-in styles, paragraph/character/table/list
  styles, inheritance (`base_style`, `next_paragraph_style`), creating and
  deleting custom styles, latent styles.
- **`references/tables.md`** — creating tables, reliable column/cell widths,
  row heights, vertical alignment, cell merging, nested tables, handling
  irregular rows (`grid_span`, `grid_cols_before`).
- **`references/text.md`** — paragraphs, runs, fonts, colors, paragraph
  formatting, spacing/indents, tab stops, hyperlinks, breaks, rendered page
  breaks.
- **`references/headers-and-footers.md`** — primary, first-page, and even-page
  headers/footers, `is_linked_to_previous`, distances, tables inside headers.
- **`references/comments.md`** — reading and adding Word review comments,
  attaching comments to single or multiple runs, multi-paragraph comment bodies.
- **`references/images.md`** — inserting inline pictures at document or run
  level, aspect-ratio scaling, inspecting `inline_shapes`, supported formats.
- **`references/page-aware-layout.md`** — computing the text column, fitting
  tables and images to column widths, pagination hygiene (`keep_with_next`,
  `keep_together`, `widow_control`), multi-section orientation flips, and what
  is planned in upcoming `power-docx` phases.
