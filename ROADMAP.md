# power-docx Roadmap

This roadmap describes the planned evolution of `power-docx` from its
1.2.0 fork point of [`python-docx`](https://github.com/python-openxml/python-docx).
It is a living document: priorities are listed in order, but ship dates are
deliberately not given, because each phase is gated on the previous one and
on community feedback.

## North star

**Make `power-docx` a native agentic library for Word documents.** A coding
agent should be able to *understand a document's layout* — page geometry,
the text column, margins and gutters, styles and their inheritance, tables
and their widths, headers/footers, pagination — well enough to design and
emit documents that are structurally correct and well-designed without
manual cleanup.

The learnings come from [`power-pptx`](https://github.com/CodeHalwell/power-pptx),
where *space-aware authoring* (measure text before save, lint after build,
render to verify, ship a bundled agent skill) made programmatically generated
decks physically correct. Slides are absolute-positioned canvases, so for
`power-pptx` "correct" is geometric. Documents are **flow layout**: the
"canvas" is the text column (page minus margins, per section) and pagination
is dynamic. The docx equivalent is therefore *page-aware authoring* — content
that stays inside the text column, tables and images sized to fit it, page
breaks where the author intends them, and a style system agents can reason
about — plus the same agent-facing machinery: a bundled skill, a declarative
spec format, a linter, and a render-and-review loop.

## Guiding principles

1. **Drop-in compatibility within 2.x.** `import power_docx` keeps working and
   existing scripts produce identical output. Breaking changes are batched into
   a clearly-flagged major version (the 2.0 rename has already happened).
2. **OOXML faithful by default.** Every new feature maps to a real WML element
   in the schema; we do not invent semantics Word won't render.
3. **Round-trip safety is a release blocker.** A document authored in Word,
   opened, mutated, and saved must not lose data. Every phase that emits new
   XML ships with a round-trip regression test.
4. **High-level helpers are additive.** They sit on top of the low-level API;
   they never replace it.
5. **Minimal dependencies.** Pure Python on top of `lxml` and
   `typing_extensions`; `Pillow` is added only for text measurement (Phase 4).
   No hosted services, no telemetry, no auth.
6. **Reads should never mutate.** Getter properties are idempotent and return
   `None` for unset values; assigning `None` clears.

## Versioning

| Range | Meaning |
|---|---|
| `2.0.0` | The rename: distribution `power-docx`, import package `power_docx`. |
| `2.1.x` – `2.9.x` | New features, additive only. No removals. |
| `3.0.0` | Reserved for breaking changes and deprecation removals. |

## Out of scope

Considered and explicitly deferred or rejected, so contributors don't burn
time prototyping them:

- **A pixel-accurate layout engine.** Phase 4's measurement uses Pillow font
  metrics for "good enough" line/page estimation; we do not replicate Word's
  renderer. Estimates are always flagged as estimates.
- **Live integration with the Word application** (COM, AppleScript, Office.js,
  Microsoft Graph). This library manipulates files on disk; it does not drive
  a running Word instance.
- **`.doc` (legacy binary format) support.** Out of scope, same as upstream.
- **Reimplementing the full OOXML surface.** The goal is the surface that
  agents and document generators actually need, not every exotic corner of
  ISO/IEC 29500.

---

Effort × impact tags use the convention `[low/high]` = small change, big
payoff; `[high/med]` = sizeable change, moderate payoff.

## Phase 0 — Foundations and rename (target: 2.0.0)

Make the fork a well-run, agent-readable repository before adding features.

- [ ] Rename distribution to `power-docx` and package to `power_docx`
  (side-by-side install with upstream `python-docx`). `[low/high]`
- [ ] `AGENTS.md` + `CLAUDE.md` repo guidance for coding agents. `[low/high]`
- [ ] `CONTRIBUTING.md`, PR template, commit-prefix and `HISTORY.rst`
  conventions. `[low/med]`
- [ ] GitHub Actions CI: pytest + behave matrix over Python 3.9–3.13, ruff,
  pyright; drop legacy `.travis.yml`. `[med/high]`
- [ ] This `ROADMAP.md`. `[low/med]`

## Phase 1 — Bundled agent skill (target: 2.1.0)

Ship the canonical usage guide *inside the package*, the power-pptx way.

- [ ] `src/power_docx/skill/` with `SKILL.md` (cheat sheet, house rules,
  anti-patterns, pitfalls) and `references/` per topic: documents/sections,
  styles, tables, text, headers/footers, comments, images, page-aware layout.
  `[med/high]`
- [ ] Packaging: `package-data` so the wheel ships the skill; a
  `power-docx-skill` console script; `python -m power_docx.skill install`
  copying into `~/.claude/skills/power-docx` with refuse-to-clobber guards.
  `[low/high]`
- [ ] Mirrored `.claude/skills/power-docx/` copy with a keep-in-sync rule in
  `AGENTS.md`. `[low/med]`
- [ ] "Coding agents" page in the user docs. `[low/med]`

## Phase 2 — Page and geometry model (target: 2.2.0)

The docx equivalent of power-pptx's `BBox`/`Grid`: let agents compute layout
from the document's real dimensions instead of guessing.

- [ ] `layout.py`: content box of a `Section` (page size − margins − gutter),
  `Document.content_width`, orientation-aware helpers. `[med/high]`
- [ ] Column-safe `add_picture(...)` (clamp/scale to the text column) and
  table helpers whose column widths sum to the content width. `[med/high]`
- [ ] Section management helpers (new page / continuous / orientation flip,
  header-footer inheritance control). `[low/med]`

## Phase 3 — Lint, audit, tidy (target: 2.3.0)

The docx `slide.lint()`: catch what slipped through, in a form agents and CI
can consume.

- [ ] `document.lint()` → report with docx issue types: `TableTooWide`,
  `ImageTooWide`, `EmptyHeading`, `UndefinedStyle`, orphan heading / widow
  line (via Phase 4 measurement), `InconsistentBaseStyle`. `[high/high]`
- [ ] Report output: human summary, `to_json()`, `to_sarif()`; `tidy()` one-call
  safe auto-fixes (clamp table/image widths, set keep-with-next); a single
  whole-document `audit()`. `[med/high]`
- [ ] `lint_on_save` on `Document`; `power-docx lint file.docx [--format
  json|sarif] [--fix]` CLI (exit 0 clean / 1 issues / 2 unreadable). `[med/high]`

## Phase 4 — Measurement engine (target: 2.4.0)

Port the reusable core of power-pptx's `text/fonts.py`, `text/measurement.py`
and `TextFitter`, adapted from boxes to flow.

- [ ] Font registry: `register_font_dir(...)`, `register_font_family(...)`,
  `POWER_DOCX_FONT_DIRS` env var, `font_is_installed(...)`; `Pillow`
  becomes a runtime dependency. `[med/high]`
- [ ] `measure_text`, line-wrap estimation, `estimate_lines()` /
  `estimate_pages()` on paragraphs and documents; explicit fallback-metrics
  warnings (`estimated=True`), `strict=True` to fail instead of guessing.
  `[high/high]`
- [ ] Pagination-aware knobs the estimator informs: widow/orphan control,
  `keep_with_next` on headings, deliberate page breaks. `[med/med]`

## Phase 5 — Declarative authoring (target: 2.5.0)

Let an LLM or user write a JSON/YAML spec; the library builds the document —
the power-pptx `compose.from_spec` pattern.

- [ ] `power_docx.compose.from_spec(spec, safe=True, base_dir=...)`:
  core properties, sections/page setup, headings/paragraphs/runs with inline
  marks, lists, tables with widths, images, page breaks, headers/footers,
  comments. `[high/high]`
- [ ] `SpecError.path` pinpointing the exact wrong field, did-you-mean hints
  for unknown keys; `safe=True` confines file paths to `base_dir` for
  untrusted specs; `from_yaml(...)`. `[med/high]`

## Phase 6 — Design layer (target: 2.6.0)

The docx analog of power-pptx's `DesignTokens`/recipes: tokens map to *named
styles and theme colors*, not shapes.

- [ ] `DesignTokens` from dict/YAML/seed color (harmony generation,
  color-blindness validation — ports directly from power-pptx). `[med/high]`
- [ ] Token → style mapping that creates/updates `Heading 1–3`, `Body`,
  `Caption`, `Quote`, `Code` styles; theme reader for `theme1.xml`
  (colors + fonts). `[med/high]`
- [ ] Document recipes: `report`, `memo`, `letter`, `article` skeletons that
  agents fill in. `[med/med]`

## Phase 7 — Render and review (target: 2.7.0)

Close the verify loop: render generated documents to images so agents (and
humans) can see the result.

- [ ] `render.py`: docx → PDF → PNG page images via LibreOffice/Poppler
  (optional dependency, clear `RendererUnavailable` error, `POWER_DOCX_SOFFICE`).
  `[med/high]`
- [ ] `power-docx review file.docx` CLI: page images + contact sheets +
  audit markdown + validation bundle, mirroring `power-pptx review`.
  `[med/med]`

## Phase 8 — Validation and round-trip gates (target: 2.8.0)

Harden against the "opens fine but Word offers to repair it" class of bug.

- [ ] Package the WML XSDs from `ref/xsd` into the wheel; `validation.py`
  validating document XML against them. `[med/high]`
- [ ] `tests/integration/` round-trip harness (save → open → save
  byte-clean) as a **release blocker** on `master`, plus a schema test
  whenever new XML is emitted. `[med/high]`
- [ ] Bring `pyright` strict green: start from a scoped entry-point config
  (`pyright-ci.json`, the power-pptx pattern), gate that in CI, then expand
  to all of `src` + `tests`. `[high/med]`

## Phase 9 — Examples and docs (continuous; feeds 3.0.0)

- [ ] `examples/`: starter pack (memo/report/letter builders), a
  `from_spec` report generator, and a stress suite exercising every Phase 2–7
  surface (mirrors `examples/stress_test/` in power-pptx). `[med/med]`
- [ ] User docs per phase (`agents.rst`, `layout.rst`, `lint.rst`,
  `compose.rst`, `design.rst`, `render.rst`); keep the bundled skill and
  docs in sync. `[med/med]`
- [ ] Site/docs hosting decision (GitHub Pages like power-pptx, or Read the
  Docs). `[low/low]`

---

This document is updated each release with what actually shipped and what
slipped. The order is the commitment; the dates are not.
