# AGENTS.md

Guidance for AI coding agents (Claude Code, Codex, and other harnesses that
read `AGENTS.md`) working in this repository. `CLAUDE.md` imports this file.

## What this project is

**power-docx** is the actively-maintained fork of
[`python-docx`](https://github.com/python-openxml/python-docx) by Steve Canny.
It is a pure-Python library for creating, reading, and updating Word 2007+
(`.docx`) files without needing Microsoft Word installed.

- Distributed on PyPI as **`power-docx`** but imported as **`import power_docx`**
  (the 2.0 release renamed the top-level package from `docx` to `power_docx` so
  it can be installed side-by-side with upstream `python-docx`). When migrating
  code, replace `docx` with `power_docx` in imports.
- Current version is defined in `src/power_docx/__init__.py` (`__version__`).
- Python 3.9+ supported. Runtime deps: `lxml`, `typing_extensions`. The minimum
  versions in `pyproject.toml` are the oldest the suite passes on.

### Why the fork exists: a native agentic library

The goal (see `ROADMAP.md`) is that coding agents can **understand document
layout** — page geometry, the text column, styles, tables, pagination — and
therefore design and output better documents. The learnings come from
[`power-pptx`](https://github.com/CodeHalwell/power-pptx), whose headline was
space-aware authoring for slides. Because Word documents are flow layout, not
an absolute canvas, the docx equivalent is **page-aware authoring**, layered
the same way:

1. Measure text with font metrics before save (Phase 4) and estimate
   lines/pages.
2. Lint and auto-fix what slipped through — tables/images wider than the text
   column, broken style references, orphan headings (Phase 3).
3. Ship a bundled agent skill inside the package so `pip install power-docx`
   is enough for an agent to find the canonical guide (Phase 1), and support
   declarative JSON/YAML document specs (Phase 5).

## Repository layout

```
src/power_docx/        # the library (importable package)
  __init__.py          # public exports + __version__ + content-type -> Part map
  api.py               # Document() factory entry point
  package.py           # OpcPackage graph
  document.py          # Document object
  blkcntnr.py          # BlockItemContainer (paragraphs + tables in a story)
  section.py           # Section/Sections: page size, margins, headers/footers
  table.py             # Table, rows, columns, cells, merge
  shape.py             # InlineShape
  comments.py          # Comments / Comment (post-fork additions)
  settings.py          # Settings
  styles/              # Styles, style objects, latent styles
  text/                # Paragraph, Run, Font, Hyperlink, breaks, tabs
  drawing/ dml/        # DrawingML (inline shapes, color, fills, lines)
  oxml/                # lxml-backed OOXML element classes (the XML layer)
  opc/                 # Open Packaging Conventions (zip/part/relationship plumbing)
  parts/               # package parts (document, styles, numbering, image, ...)
  enum/                # WD_* enumerations
  image/               # image characterization (PNG/JPEG/GIF/BMP/TIFF)
  templates/           # default.docx used by Document()

tests/                 # pytest unit tests, mirroring the src module layout
features/              # Gherkin acceptance tests (run via behave)
docs/                  # Sphinx documentation (user/, dev/, api/)
ref/                   # ISO/IEC 29500 spec PDFs + XSD schemas (reference material)
typings/               # type stubs (behave), used by pyright strict mode
```

`ref/` is reference material only — never imported. Packaged XSDs (Phase 8 of
the roadmap) will live under `src/power_docx/schemas/` and must stay identical
to `ref/xsd/`.

## Development workflows

Standard Python tooling — no exotic build steps. The repo uses `uv` (see the
`Makefile` and `uv.lock`), but plain `pip` works too.

```bash
# setup (editable install + test deps)
uv sync                 # or: pip install -e . && pip install -r requirements-test.txt

# tests — two layers
uv run pytest -q tests          # unit tests, organized by source module
uv run behave --stop            # Gherkin acceptance tests under features/

# lint + type-check
uv run ruff check src tests features
uv run pyright                 # strict mode, configured in pyproject.toml --
                               # not yet CI-gated: inherited typing debt, see
                               # ROADMAP.md Phase 8; do not add new errors
```

- pytest discovers test classes named `Test`/`Describe` and functions prefixed
  `test_`/`it_`/`its_`/`they_`/`and_`/`but_` (see `[tool.pytest.ini_options]` in
  `pyproject.toml`). `filterwarnings = ["error"]` — warnings fail the suite.
- `behave` runs from the repo root; scratch output goes to `features/_scratch/`.

## CI gates (`.github/workflows/ci.yml`)

A PR must keep all of these green:

1. **test** — `pytest` and `behave` across Python 3.9–3.13.
2. **quality** — `ruff check` over `src`, `tests`, and `features`.

`pyright` strict is configured (`[tool.pyright]` in `pyproject.toml`) but not
yet CI-gated: the inherited code carries typing debt (ROADMAP Phase 8 brings
it green via a scoped entry-point config first, the power-pptx pattern).

## Conventions

- **Line length 100** (ruff config in `pyproject.toml`).
- **`known-first-party = ["power_docx"]`** for isort import ordering.
- **No raw EMU integers in API usage** — use `Inches(...)`, `Pt(...)`, `Cm(...)`,
  `Emu(...)` from `power_docx.shared`.
- **Commit message prefixes** (imperative summary, body wrapped at 72 chars):
  `fix:`, `feat:`, `rfctr:`, `docs:`, `build:`/`dev:`, `test:`. Reference issues
  with `refs #123` / `fixes #123`.
- **Every PR carries** its code, unit tests (mirroring the source module layout),
  behave features when user-visible, a `HISTORY.rst` entry under the
  `Unreleased` section, and doc updates if user-visible.

## When making changes

- Public API additions: add unit tests mirroring the source module layout, and
  an acceptance feature if the behavior is user-facing.
- Update `HISTORY.rst` (unreleased section) for any user-visible change.
- If you change the library's public usage surface, update the bundled skill
  under `src/power_docx/skill/` **and** the mirror under `.claude/skills/`
  (both land in ROADMAP Phase 1; keep the two copies in sync from then on).
- The version is the `__version__` string in `src/power_docx/__init__.py`
  (setuptools reads it dynamically).

## Useful references in-tree

- `README.md` — overview, install, example.
- `ROADMAP.md` — the phased plan (north star, out-of-scope list, Phase 0–9).
- `CONTRIBUTING.md` — dev environment, test layout, PR expectations, commit style.
- `HISTORY.rst` — changelog (`Unreleased` section on top).
- `docs/dev/analysis/` — per-feature OOXML analysis of the document model.
- `ref/` — the ISO/IEC 29500 specification and XSD schemas.
