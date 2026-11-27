# Documents and Sections

## Creating, opening, and saving

`Document()` accepts a filesystem path, a binary file-like object (`BytesIO`,
open file handle), or `None` (loads the bundled `default.docx` template).

```python
from io import BytesIO
from power_docx import Document

# Blank document from bundled default.docx
doc = Document()

# Open from disk or in-memory stream
doc_from_file = Document("template.docx")
buf = BytesIO()
doc.save(buf)
buf.seek(0)
reloaded = Document(buf)
```

Using a branded `.docx` template as the starting point (`Document("brand.docx")`)
is the cleanest way to inherit corporate theme colors, fonts, styles, and
headers/footers — clear any placeholder paragraphs you don't need and append
your content.

## Core properties and document settings

```python
from datetime import datetime, timezone
from power_docx import Document

doc = Document()
props = doc.core_properties
props.title = "Architecture Decision Record"
props.subject = "Storage Migration"
props.author = "Platform Engineering"
props.keywords = "architecture, storage, adr"
props.comments = "Generated programmatically with power-docx"
props.created = datetime(2026, 1, 15, 9, 0, tzinfo=timezone.utc)

# Enable odd/even distinct headers and footers across the document
doc.settings.odd_and_even_pages_header_footer = True
```

## Traversing document content in order

`doc.paragraphs` and `doc.tables` return separate lists, losing their relative
order. Use `iter_inner_content()` on `Document`, `Section`, or `_Cell` to visit
paragraphs and tables in exact document order:

```python
from power_docx import Document
from power_docx.table import Table
from power_docx.text.paragraph import Paragraph

doc = Document()
doc.add_heading("Summary", level=1)
doc.add_table(rows=2, cols=2, style="Table Grid")
doc.add_paragraph("Closing remarks.")

for item in doc.iter_inner_content():
    if isinstance(item, Paragraph):
        print("P:", item.text)
    elif isinstance(item, Table):
        print("T:", len(item.rows), "x", len(item.columns))
```

## Sections and page setup

Every document has at least one `Section` (`doc.sections[0]`). Each section
owns its own page size, orientation, margins, gutter, and header/footer
definitions.

```python
from power_docx import Document
from power_docx.enum.section import WD_ORIENT, WD_SECTION
from power_docx.shared import Inches

doc = Document()
sec = doc.sections[0]

# Standard US Letter with 1.0" margins (usable text column = 6.5")
sec.page_width = Inches(8.5)
sec.page_height = Inches(11.0)
sec.top_margin = Inches(1.0)
sec.bottom_margin = Inches(1.0)
sec.left_margin = Inches(1.0)
sec.right_margin = Inches(1.0)
sec.gutter = Inches(0.0)
sec.header_distance = Inches(0.5)
sec.footer_distance = Inches(0.5)
```

> **Default template trap:** A brand-new `Document()` starts with US Letter
> (`8.5" x 11.0"`), `1.0"` top/bottom margins, and **`1.25"`** left/right
> margins — giving a **`6.0"`** text column unless you adjust the margins.

### Adding a new section and switching orientation

`doc.add_section(start_type=WD_SECTION.NEW_PAGE)` starts a new section. Valid
`WD_SECTION` start types are `NEW_PAGE`, `CONTINUOUS`, `EVEN_PAGE`, `ODD_PAGE`,
and `NEW_COLUMN`.

Setting `section.orientation = WD_ORIENT.LANDSCAPE` **does not** automatically
swap `page_width` and `page_height` — you must swap them yourself:

```python
from power_docx import Document
from power_docx.enum.section import WD_ORIENT, WD_SECTION

doc = Document()
doc.add_paragraph("Portrait section content.")

# Start a landscape section on a new page
wide = doc.add_section(WD_SECTION.NEW_PAGE)
wide.orientation = WD_ORIENT.LANDSCAPE
wide.page_width, wide.page_height = wide.page_height, wide.page_width
doc.add_paragraph("Wide table goes here.")

# Return to portrait on the next page
back = doc.add_section(WD_SECTION.NEW_PAGE)
back.orientation = WD_ORIENT.PORTRAIT
back.page_width, back.page_height = back.page_height, back.page_width
```

### Section-scoped content iteration

`section.iter_inner_content()` yields only the paragraphs and tables belonging
to that specific section, which is handy when auditing or summarizing a
multi-section document.
