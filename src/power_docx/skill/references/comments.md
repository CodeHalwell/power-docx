# Comments

`power-docx` supports reading existing Word comments and adding new comments
anchored to one or more runs in the document body.

## Adding comments

Attach a comment to a single `Run` or a contiguous `Sequence[Run]` with
`doc.add_comment(runs, text=..., author=..., initials=...)`:

```python
from power_docx import Document

doc = Document()
p = doc.add_paragraph("Projected revenue is ")
highlight = p.add_run("$4.2M")
p.add_run(" for Q4.")

comment = doc.add_comment(
    runs=highlight,
    text="Confirm whether this includes recurring renewals.",
    author="Alex Rivera",
    initials="AR",
)
print(comment.comment_id, comment.author, comment.timestamp)
```

To span multiple consecutive runs, pass a list or tuple of runs in document
order:

```python
from power_docx import Document

doc = Document()
p = doc.add_paragraph()
r1 = p.add_run("Service availability ")
r2 = p.add_run("99.95%")
r3 = p.add_run(" measured monthly.")

doc.add_comment(
    runs=[r1, r2],
    text="Does this exclude scheduled maintenance windows?",
    author="SRE Review",
    initials="SR",
)
```

## Multi-paragraph and structured comment bodies

A `Comment` is a `BlockItemContainer`: you can inspect and add multiple
paragraphs, runs, or tables inside a comment (note that `comment.add_table`
requires an explicit `width`):

```python
from power_docx import Document
from power_docx.shared import Inches

doc = Document()
p = doc.add_paragraph("Target launch date: ")
r = p.add_run("October 15")

c = doc.add_comment(runs=r, text="Checklist before launch:", author="PM", initials="PM")
c.add_paragraph("1. Security sign-off complete.")
c.add_paragraph("2. Rollback plan verified.")
tbl = c.add_table(rows=1, cols=2, width=Inches(2.5))
tbl.cell(0, 0).text = "Owner"
tbl.cell(0, 1).text = "Status"
```

## Reading existing comments

Iterate `doc.comments` or look up a comment by its integer `comment_id` with
`doc.comments.get(comment_id)`:

```python
from power_docx import Document

doc = Document()
for comment in doc.comments:
    print(f"[{comment.comment_id}] {comment.author} ({comment.initials}): {comment.text}")
    for para in comment.paragraphs:
        print("  ", para.text)

specific = doc.comments.get(0)
if specific is not None:
    print("Found comment 0:", specific.text)
```

## Limitations to keep in mind

- Comments cannot be nested inside another comment.
- Comment ranges are anchored to `Run` objects (`mark_comment_range` wraps the
  first and last run in `<w:commentRangeStart>` / `<w:commentRangeEnd>` and
  inserts `<w:commentReference>`).
- Deleting comments or threaded comment replies (`commentsExtended.xml`) is not
  yet exposed in the high-level API.
