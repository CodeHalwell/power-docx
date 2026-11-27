# Headers and Footers

Each `Section` can define up to three pairs of headers and footers:

| Variant | Properties | Activation requirement |
|---|---|---|
| Primary (default / odd pages) | `section.header`, `section.footer` | Always active |
| First page | `section.first_page_header`, `section.first_page_footer` | `section.different_first_page_header_footer = True` |
| Even pages | `section.even_page_header`, `section.even_page_footer` | `doc.settings.odd_and_even_pages_header_footer = True` (document-wide) |

## Basic header and footer

Every header or footer is a `BlockItemContainer` that starts with one empty
paragraph (`header.paragraphs[0]`):

```python
from power_docx import Document
from power_docx.enum.text import WD_ALIGN_PARAGRAPH
from power_docx.shared import Inches, Pt, RGBColor

doc = Document()
section = doc.sections[0]
section.header_distance = Inches(0.5)
section.footer_distance = Inches(0.5)

header = section.header
hp = header.paragraphs[0]
hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
hrun = hp.add_run("ACME Corp — Internal Engineering Review")
hrun.font.size = Pt(9)
hrun.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

footer = section.footer
fp = footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
frun = fp.add_run("Confidential")
frun.font.size = Pt(9)
```

## Multi-section linking (`is_linked_to_previous`)

For sections after the first (`doc.sections[1:]`), `is_linked_to_previous`
defaults to **`True`**. Editing a linked header/footer silently edits the
*previous* section's header/footer instead of creating a new one!

Always unlink before customizing:

```python
from power_docx import Document
from power_docx.enum.section import WD_SECTION

doc = Document()
doc.sections[0].header.paragraphs[0].text = "Chapter 1"

sec2 = doc.add_section(WD_SECTION.NEW_PAGE)
sec2.header.is_linked_to_previous = False      # MUST unlink first
sec2.header.paragraphs[0].text = "Chapter 2"
```

Setting `is_linked_to_previous = True` removes that section's own header/footer
part so it inherits from the preceding section again.

## Distinct first-page and odd/even headers

```python
from power_docx import Document

doc = Document()
section = doc.sections[0]

# Suppress header on a cover page while showing it on page 2+
section.different_first_page_header_footer = True
section.first_page_header.paragraphs[0].text = ""
section.header.paragraphs[0].text = "Annual Technical Report"

# Document-wide odd/even headers (section.header becomes the odd-page header)
doc.settings.odd_and_even_pages_header_footer = True
section.even_page_header.paragraphs[0].text = "ACME Engineering"
```

## Multi-column header/footer layout

Use either right-aligned tab stops (recommended for simple left/right pairs) or
`header.add_table(rows, cols, width)` — note that `width` is **required** on
header and footer tables:

```python
from power_docx import Document
from power_docx.enum.text import WD_ALIGN_PARAGRAPH
from power_docx.shared import Emu

doc = Document()
sec = doc.sections[0]
col_w = Emu(sec.page_width - sec.left_margin - sec.right_margin - (sec.gutter or 0))

tbl = sec.header.add_table(rows=1, cols=2, width=col_w)
tbl.autofit = False
half = Emu(col_w // 2)
tbl.cell(0, 0).width = half
tbl.cell(0, 1).width = half
tbl.cell(0, 0).paragraphs[0].text = "Project Spec"
right_p = tbl.cell(0, 1).paragraphs[0]
right_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
right_p.text = "v2.1"
```
