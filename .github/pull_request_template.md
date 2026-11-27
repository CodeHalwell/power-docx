## Summary

<!--
  One paragraph describing what this PR changes and why.
  Link to the relevant issue or ROADMAP.md phase/item.
-->

refs #

## Checklist

- [ ] Code for the change itself.
- [ ] Unit tests covering the new behavior (mirroring the source layout under `tests/`).
- [ ] Behave acceptance feature under `features/` if the behavior is user-visible.
- [ ] `HISTORY.rst` entry under the `Unreleased` section.
- [ ] Doc updates if the change is user-visible.
- [ ] If the public usage surface changed: bundled skill copy
  (`src/power_docx/skill/`) and `.claude/skills/` mirror updated in sync.
- [ ] `uv run pytest -q tests` passes locally.
- [ ] `uv run behave --stop` passes locally.
- [ ] `uv run ruff check src tests features` passes locally.
- [ ] No new `pyright` errors.

## Test notes

<!--
  Briefly describe how to exercise the new behavior manually,
  or why automated tests are sufficient.
-->
