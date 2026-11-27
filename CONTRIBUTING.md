# Contributing

Thank you for considering a contribution to `power-docx`.

This document covers the basics: how to propose a change, what your PR
needs to look like, and how the test suite is laid out.

## Where to start

- Browse the [GitHub issues](https://github.com/CodeHalwell/power-docx/issues).
- Read the [`ROADMAP.md`](ROADMAP.md). Each phase lists concrete user-visible
  API surface that's planned; if you'd like to take on one of those items,
  please comment on the corresponding tracking issue first so we can avoid
  duplicate work.
- New ideas welcome — open a "feature proposal" issue before writing the
  patch so the design can be sanity-checked against the roadmap.

## Reporting bugs

Please use the bug-report issue template. The most useful bug reports include:

- A small, self-contained snippet that reproduces the issue.
- The output you got and the output you expected.
- The Python version, `power-docx` version, and platform.

If the bug touches an existing Word file, please attach a minimal redacted
`.docx` that still triggers the issue.

## Development environment

This project uses standard Python tooling — no exotic build steps. The repo
ships a `uv.lock`, so `uv` is the quickest path; plain `pip` works too.

```bash
# with uv (preferred; see the Makefile)
uv sync

# or with pip
git clone https://github.com/CodeHalwell/power-docx.git
cd power-docx
python -m venv .venv && source .venv/bin/activate
pip install -e .
pip install -r requirements-test.txt
```

## Tests

The test suite has two layers:

1. **Unit tests** under `tests/`, organized by source module
   (`tests/test_table.py` covers `src/power_docx/table.py`, etc.).
2. **Acceptance tests** under `features/`, written in Gherkin and run via
   `behave`.

Running everything:

```bash
uv run pytest -q tests     # or: make test
uv run behave --stop       # or: make accept
```

`pytest` is configured with `filterwarnings = ["error"]` — warnings fail the
suite. Test classes are named `Test`/`Describe`; test functions are prefixed
`test_`/`it_`/`they_`/`and_`/`but_` (see `pyproject.toml`).

## Lint and type-checking

```bash
uv run ruff check src tests features
uv run pyright                 # strict mode over src/power_docx + tests --
                               # configured but not yet CI-gated (typing debt,
                               # ROADMAP.md Phase 8); do not add new errors
```

CI (`.github/workflows/ci.yml`) runs the pytest + behave matrix on Python
3.9–3.13 plus ruff; keep them green.

The Sphinx documentation under `docs/` can be built with:

```bash
pip install -r requirements-docs.txt
make -C docs html
```

## Pull-request expectations

Per `ROADMAP.md`, PRs should be small. Each PR should carry:

- **Code** for the change itself.
- **Unit tests** covering the new behavior (mirroring the source layout), and
  a behave feature when the behavior is user-visible.
- **A `HISTORY.rst` entry** under the `Unreleased` section.
- **Doc updates** if the change is user-visible.
- If the change changes the public usage surface, update the bundled agent
  skill copy under `src/power_docx/skill/` and the mirror under
  `.claude/skills/` (from ROADMAP Phase 1 on).

## Commit messages

Follow the existing style. The first line is a short imperative summary
prefixed with one of:

- `fix:` — bug fix.
- `feat:` — new public API.
- `rfctr:` — internal refactor with no behavior change.
- `docs:` — documentation-only change.
- `build:` / `dev:` — build system, dev tooling.
- `test:` — test-only change.

Wrap the body at 72 characters. If the change relates to an issue, reference
it (`refs #123` / `fixes #123`).

## What we say no to

These are listed in `ROADMAP.md` under "Out of scope" and won't be accepted
without a strong new argument:

- A pixel-accurate layout/rendering engine.
- Live Word integration (COM, AppleScript, Office.js, Graph).
- `.doc` legacy binary format support.

We also tend to push back on:

- Features that require a non-trivial new dependency (Pillow for measurement
  in Phase 4 is the accepted exception).
- Changes that don't round-trip cleanly through Word.
- Read-time mutation of the underlying XML.
