# Text, Paragraphs, Runs, and Formatting

Word separates **block-level** formatting (`Paragraph` / `ParagraphFormat`) from
**character-level** formatting (`Run` / `Font`). A paragraph contains one or
more runs (and optionally hyperlinks).

## Paragraphs and runs

```python
from power_docx import Document
from power_docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX, WD_UNDERLINE
from power_docx.shared import Pt, RGBColor

doc = Document()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.LEFT

r1 = p.add_run("Important: ")
r1.bold = True
r1.font.color.rgb = RGBColor(0xC0, 0x39, 0x2B)

r2 = p.add_run("review the updated SLA ")
r2.font.name = "Calibri"
r2.font.size = Pt(11)

r3 = p.add_run("before Friday")
r3.italic = True
r3.underline = WD_UNDERLINE.SINGLE
r3.font.highlight_color = WD_COLOR_INDEX.YELLOW
```

> **Pitfall:** Assigning `p.text = "new text"` replaces *all* runs in `p` with a
> single unformatted run, destroying any bold/italic/color runs. Edit `run.text`
> or call `p.clear()` and add runs explicitly instead.

### Inserting before an existing paragraph

```python
from power_docx import Document

doc = Document()
second = doc.add_paragraph("Second paragraph")
first = second.insert_paragraph_before("First paragraph", style="Normal")
```

## Tri-state properties

Most boolean formatting attributes (`bold`, `italic`, `all_caps`, `strike`,
`subscript`, `superscript`, `keep_with_next`, `keep_together`,
`widow_control`, `page_break_before`) are **tri-state**:

- `True` — explicitly turned on.
- `False` — explicitly turned off (overrides an inherited `True` from the style).
- `None` — inherited from the style hierarchy. Assign `None` to clear an
  explicit override.

## Paragraph spacing, indents, and pagination controls

```python
from power_docx import Document
from power_docx.enum.text import WD_LINE_SPACING
from power_docx.shared import Inches, Pt

doc = Document()
p = doc.add_paragraph("Well-spaced body paragraph.")
pf = p.paragraph_format

pf.space_before = Pt(0)
pf.space_after = Pt(6)
pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
pf.line_spacing = 1.15                # float -> multiple; Length (Pt(14)) -> exact/at-least
pf.left_indent = Inches(0.0)
pf.right_indent = Inches(0.0)
pf.first_line_indent = Inches(0.25)   # negative value creates a hanging indent

# Pagination controls
pf.widow_control = True               # avoid single orphan/widow lines across pages
pf.keep_together = True               # keep all lines of this paragraph on one page
pf.keep_with_next = False             # set True on headings & captions
pf.page_break_before = False          # set True to always start on a new page
```

## Tab stops

Use tab stops aligned to the text column width for clean right-aligned metadata
(e.g. title on left, date on right) without needing a borderless table:

```python
from power_docx import Document
from power_docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER
from power_docx.shared import Inches

doc = Document()
p = doc.add_paragraph()
p.paragraph_format.tab_stops.add_tab_stop(
    Inches(6.0),
    alignment=WD_TAB_ALIGNMENT.RIGHT,
    leader=WD_TAB_LEADER.DOTS,
)
r = p.add_run("Section 1: Overview")
r.add_tab()
p.add_run("Page 3")
```

## Breaks and rendered page breaks

```python
from power_docx import Document
from power_docx.enum.text import WD_BREAK

doc = Document()
p = doc.add_paragraph("Line one")
p.add_run().add_break(WD_BREAK.LINE)      # soft line break (<w:br/>)
p.add_run("Line two")
p.add_run().add_break(WD_BREAK.PAGE)      # hard page break inside this paragraph
```

When reading documents previously saved by Word, Word records where it broke
pages as `<w:lastRenderedPageBreak/>`. Inspect them with:

```python
from power_docx import Document

doc = Document()
for p in doc.paragraphs:
    if p.contains_page_break:
        for brk in p.rendered_page_breaks:
            print(brk.preceding_paragraph_fragment, brk.following_paragraph_fragment)
```

## Reading hyperlinks in paragraphs

`paragraph.hyperlinks` lists all `Hyperlink` objects in a paragraph, and
`paragraph.iter_inner_content()` yields `Run` and `Hyperlink` objects in their
exact reading order:

```python
from power_docx import Document
from power_docx.text.hyperlink import Hyperlink

doc = Document()
for p in doc.paragraphs:
    for item in p.iter_inner_content():
        if isinstance(item, Hyperlink):
            print(item.text, "->", item.url)
```
