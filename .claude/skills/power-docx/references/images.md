# Images and Inline Shapes

`power-docx` inserts images as **inline shapes** (`InlineShape`), meaning they
flow inline with text inside a paragraph run. Supported image formats: **PNG,
JPEG, GIF, BMP, and TIFF**.

## Adding pictures at document level vs. run level

- `doc.add_picture(image_path_or_stream, width=None, height=None)` creates a
  new paragraph containing a single run with the image.
- `run.add_picture(image_path_or_stream, width=None, height=None)` embeds an
  image inside an existing paragraph (for captions, inline icons, or table
  cells).

Pass **either** `width` **or** `height` (never both unless you computed the
exact aspect ratio) so `power-docx` scales the other dimension proportionally:

```python
from io import BytesIO
from power_docx import Document
from power_docx.enum.text import WD_ALIGN_PARAGRAPH
from power_docx.shared import Emu, Inches

doc = Document()
sec = doc.sections[0]
col_w = Emu(sec.page_width - sec.left_margin - sec.right_margin - (sec.gutter or 0))

# Document-level image clamped to the text column width
doc.add_picture("diagram.png", width=min(Inches(5.5), col_w))

# Centered image inside a paragraph with a caption kept attached
img_p = doc.add_paragraph()
img_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
img_p.paragraph_format.keep_with_next = True
img_p.add_run().add_picture("diagram.png", width=Inches(4.5))

cap = doc.add_paragraph("Figure 1: System architecture.", style="Caption")
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER

# From an in-memory byte stream
image_bytes = BytesIO(b"...")
doc.add_picture(image_bytes, width=Inches(3.0))
```

## Placing images inside table cells

To put an image in a table cell, call `add_picture` on a run inside the cell
and size it slightly narrower than the cell's width to leave cell padding room:

```python
from power_docx import Document
from power_docx.shared import Inches

doc = Document()
table = doc.add_table(rows=1, cols=2, style="Table Grid")
table.autofit = False
cell_w = Inches(3.0)
table.cell(0, 0).width = cell_w
table.cell(0, 1).width = cell_w

run = table.cell(0, 0).paragraphs[0].add_run()
run.add_picture("thumbnail.png", width=Inches(2.6))
table.cell(0, 1).text = "Figure description"
```

## Inspecting and resizing existing inline shapes

`doc.inline_shapes` lists all inline shapes in the document body. Check
`shape.type` against `WD_INLINE_SHAPE` (`PICTURE`, `LINKED_PICTURE`, `CHART`,
`SMART_ART`, `NOT_IMPLEMENTED`):

```python
from power_docx import Document
from power_docx.enum.shape import WD_INLINE_SHAPE
from power_docx.shared import Emu

doc = Document()
sec = doc.sections[0]
col_w = Emu(sec.page_width - sec.left_margin - sec.right_margin - (sec.gutter or 0))

for shape in doc.inline_shapes:
    if shape.type == WD_INLINE_SHAPE.PICTURE and shape.width > col_w:
        scale = col_w / shape.width
        shape.width = col_w
        shape.height = Emu(int(shape.height * scale))
```

> **Note:** Floating / text-wrapped anchor shapes (`<wp:anchor>`) are not
> exposed in `doc.inline_shapes`. Use inline pictures (or a borderless 2-column
> table for side-by-side image + text) when generating documents
> programmatically.
