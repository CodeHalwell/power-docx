# Tables

## Creating a table that fits the text column

`doc.add_table(rows, cols, style=None)` defaults to `Normal Table` (no visible
borders). Pass `style="Table Grid"` (or a template table style) and compute
column widths from the active section's text column.

**Critical Word quirk:** Setting `table.columns[i].width` alone updates
`<w:tblGrid>`, which Word often ignores when rendering. To make column widths
stick in Word and LibreOffice, set `table.autofit = False` **and** assign
`cell.width` on every cell in each column:

```python
from power_docx import Document
from power_docx.enum.table import WD_ALIGN_VERTICAL, WD_ROW_HEIGHT_RULE, WD_TABLE_ALIGNMENT
from power_docx.shared import Emu, Inches, Pt

doc = Document()
sec = doc.sections[0]
sec.left_margin = Inches(1.0)
sec.right_margin = Inches(1.0)
col_w = Emu(sec.page_width - sec.left_margin - sec.right_margin - (sec.gutter or 0))

# Allocate proportional column widths that sum exactly to the text column
fractions = (0.25, 0.25, 0.50)
widths = [Emu(int(col_w * f)) for f in fractions]

table = doc.add_table(rows=1, cols=3, style="Table Grid")
table.autofit = False
table.alignment = WD_TABLE_ALIGNMENT.CENTER

headers = ("Component", "Owner", "Status")
hdr_row = table.rows[0]
hdr_row.height = Pt(24)
hdr_row.height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST

for idx, title in enumerate(headers):
    table.columns[idx].width = widths[idx]
    cell = hdr_row.cells[idx]
    cell.width = widths[idx]
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p = cell.paragraphs[0]
    run = p.add_run(title)
    run.bold = True

records = [
    ("Parser", "Core", "Shipped"),
    ("Layout", "Agents", "In progress"),
]
for record in records:
    row = table.add_row()
    for idx, value in enumerate(record):
        cell = row.cells[idx]
        cell.width = widths[idx]
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        cell.text = value
```

## Accessing cells and building formatted cell content

- `table.cell(row_idx, col_idx)` returns a `_Cell`.
- Every `_Cell` is a `BlockItemContainer` (just like `Document`): it always
  starts with one empty paragraph at `cell.paragraphs[0]`.
- Assigning `cell.text = "..."` sets the text of `cell.paragraphs[0]` and
  removes any extra paragraphs/runs. To apply formatting, write into
  `cell.paragraphs[0].add_run(...)` instead of assigning `cell.text` after
  formatting.

```python
from power_docx import Document
from power_docx.enum.text import WD_ALIGN_PARAGRAPH
from power_docx.shared import Pt

doc = Document()
table = doc.add_table(rows=1, cols=2, style="Table Grid")

cell = table.cell(0, 1)
p = cell.paragraphs[0]
p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
run = p.add_run("$1,250.00")
run.bold = True
run.font.size = Pt(10)
```

## Merging cells

`cell_a.merge(cell_b)` merges the rectangular span bounded by `cell_a` and
`cell_b` (either horizontally, vertically, or both). Text from merged cells is
concatenated with newlines unless cleared first.

```python
from power_docx import Document

doc = Document()
table = doc.add_table(rows=3, cols=3, style="Table Grid")

# Horizontal banner across row 0
banner = table.cell(0, 0).merge(table.cell(0, 2))
banner.text = "Regional Breakdown"

# Vertical merge down column 0 across rows 1 and 2
group = table.cell(1, 0).merge(table.cell(2, 0))
group.text = "EMEA"
```

## Reading tables safely (merged cells & irregular rows)

When reading existing Word documents, rows may contain merged spans or omitted
leading/trailing grid columns:

- `cell.grid_span` tells you how many grid columns a cell spans.
- `row.grid_cols_before` and `row.grid_cols_after` report omitted grid columns
  at the start or end of a row.
- `table.row_cells(row_idx)` and `table.column_cells(col_idx)` return the
  effective grid sequence (repeating merged `_Cell` proxies across their span).
  Deduplicate by `cell._tc` if you want each physical cell only once.

## Adding columns and nested tables

```python
from power_docx import Document
from power_docx.shared import Inches

doc = Document()
table = doc.add_table(rows=2, cols=2, style="Table Grid")

# Adding a column requires an explicit width
new_col = table.add_column(Inches(1.5))
for cell in new_col.cells:
    cell.width = Inches(1.5)

# Nested table inside a cell
inner = table.cell(1, 1).add_table(rows=2, cols=2)
inner.style = "Table Grid"
inner.cell(0, 0).text = "Nested"
```

## Tables inside headers, footers, and comments

Unlike `Document.add_table(rows, cols)` and `_Cell.add_table(rows, cols)`,
`_Header.add_table`, `_Footer.add_table`, and `Comment.add_table` require an
explicit `width` parameter:

```python
from power_docx import Document
from power_docx.shared import Inches

doc = Document()
hdr_table = doc.sections[0].header.add_table(rows=1, cols=2, width=Inches(6.0))
hdr_table.cell(0, 0).text = "Left Title"
hdr_table.cell(0, 1).text = "Right Date"
```
