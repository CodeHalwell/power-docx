# power-docx

**Word documents from Python — a native agentic library.**

*power-docx* is the actively-maintained fork of
[`python-docx`](https://github.com/python-openxml/python-docx) by Steve Canny.
It is a pure-Python library for creating, reading, and updating Microsoft Word
2007+ (`.docx`) files without needing Microsoft Word installed.

- Distributed on PyPI as **`power-docx`** but imported as **`import power_docx`**
  (the 2.0 release renamed the top-level package from `docx` to `power_docx` so
  it can be installed side-by-side with upstream `python-docx`). When migrating
  code, replace `docx` with `power_docx` in imports.
- Current version is defined in `src/power_docx/__init__.py` (`__version__`).
- Python 3.9+ supported. Runtime deps: `lxml`, `typing_extensions`.
- See [ROADMAP.md](ROADMAP.md) for where the fork is headed: page-aware
  authoring, a bundled agent skill, declarative specs, lint/audit, and a
  render-and-review loop — the power-pptx learnings applied to Word documents.

## Installation

```
pip install power-docx
```

To install the bundled coding-agent skill (Claude Code / Agent Skills) into
`~/.claude/skills/power-docx`:

```
power-docx-skill install
# or: python -m power_docx.skill install
```

## Example

```python
>>> from power_docx import Document

>>> document = Document()
>>> document.add_paragraph("It was a dark and stormy night.")
<power_docx.text.paragraph.Paragraph object at 0x10f19e760>
>>> document.save("dark-and-stormy.docx")

>>> document = Document("dark-and-stormy.docx")
>>> document.paragraphs[0].text
'It was a dark and stormy night.'
```

More information is available in the [power-docx documentation](https://codehalwell.github.io/power-docx/).
