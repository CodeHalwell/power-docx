# Styles

Using named styles instead of inline run formatting produces smaller, cleaner
Word documents whose hierarchy works with Word's Navigation Pane, Table of
Contents, and global theme updates.

## Style types

`WD_STYLE_TYPE` defines four style kinds:

- `WD_STYLE_TYPE.PARAGRAPH` — applies to paragraphs (`ParagraphStyle`), carries
  both `.font` and `.paragraph_format`.
- `WD_STYLE_TYPE.CHARACTER` — applies to runs (`CharacterStyle`), carries
  `.font`.
- `WD_STYLE_TYPE.TABLE` — applies to tables (`_TableStyle`), carries `.font`
  and `.paragraph_format`.
- `WD_STYLE_TYPE.LIST` — numbering/list styles (`_NumberingStyle`).

## Inspecting and modifying existing styles

Look up styles by their **UI name** (the name Word displays, e.g. `"Normal"`,
`"Heading 1"`, `"Table Grid"`, `"List Bullet"`), not their XML `style_id`
(`"Heading1"`):

```python
from power_docx import Document
from power_docx.shared import Pt, RGBColor

doc = Document()

normal = doc.styles["Normal"]
normal.font.name = "Calibri"
normal.font.size = Pt(10.5)
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.line_spacing = 1.15
normal.paragraph_format.widow_control = True

h1 = doc.styles["Heading 1"]
h1.font.name = "Calibri"
h1.font.size = Pt(16)
h1.font.bold = True
h1.font.color.rgb = RGBColor(0x1B, 0x4F, 0x72)
h1.paragraph_format.space_before = Pt(14)
h1.paragraph_format.space_after = Pt(4)
h1.paragraph_format.keep_with_next = True
```

To fetch a style by XML `style_id` instead of UI name, use
`doc.styles.get_by_id(style_id, style_type)`.

## Creating custom styles and inheritance

Always set `base_style` so your custom style inherits sensible defaults, and
set `next_paragraph_style` on heading/caption styles so pressing Enter in Word
returns to body text:

```python
from power_docx import Document
from power_docx.enum.style import WD_STYLE_TYPE
from power_docx.shared import Inches, Pt, RGBColor

doc = Document()

callout = doc.styles.add_style("Callout", WD_STYLE_TYPE.PARAGRAPH)
callout.base_style = doc.styles["Normal"]
callout.next_paragraph_style = doc.styles["Normal"]
callout.quick_style = True
callout.priority = 20
callout.font.italic = True
callout.font.color.rgb = RGBColor(0x2C, 0x3E, 0x50)
callout.paragraph_format.left_indent = Inches(0.35)
callout.paragraph_format.right_indent = Inches(0.35)
callout.paragraph_format.space_before = Pt(6)
callout.paragraph_format.space_after = Pt(6)

code_inline = doc.styles.add_style("Inline Code", WD_STYLE_TYPE.CHARACTER)
code_inline.font.name = "Consolas"
code_inline.font.size = Pt(9.5)

p = doc.add_paragraph("Run ", style="Callout")
p.add_run("power-docx-skill install", style="Inline Code")
p.add_run(" to install the bundled skill.")
```

## Deleting styles and checking availability

```python
from power_docx import Document
from power_docx.enum.style import WD_STYLE_TYPE

doc = Document()
tmp = doc.styles.add_style("Temporary", WD_STYLE_TYPE.PARAGRAPH)
tmp.delete()

# Check before referencing a style by name to avoid KeyError
style_names = {s.name for s in doc.styles}
if "Quote" in style_names:
    doc.add_paragraph("Simplicity is prerequisite for reliability.", style="Quote")
```

## Latent styles

Word ships hundreds of built-in styles as *latent* definitions (present in
`latent_styles` until first used, at which point Word materializes them into
`styles.xml`). You can inspect or configure their gallery visibility via
`doc.styles.latent_styles`:

```python
from power_docx import Document

doc = Document()
latent = doc.styles.latent_styles
latent.default_to_hidden = True
if "Heading 1" in latent:
    latent["Heading 1"].hidden = False
    latent["Heading 1"].quick_style = True
```

## Built-in styles in `default.docx`

The bundled `default.docx` template includes 164 materialized styles, including:

- **Headings / structure**: `Title`, `Subtitle`, `Heading 1`–`Heading 9`,
  `Normal`, `No Spacing`, `Body Text`, `Quote`, `Intense Quote`, `Caption`.
- **Lists**: `List Bullet`, `List Bullet 2`, `List Bullet 3`, `List Number`,
  `List Number 2`, `List Number 3`, `List Paragraph`.
- **Tables**: `Normal Table` (borderless default), `Table Grid`,
  `Light Shading`, `Light List`, `Medium Shading 1`, `Medium Grid 1`, and
  `Accent 1`–`Accent 6` variants.
