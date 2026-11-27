.. _agents:

Coding agents
=============

``power-docx`` ships a bundled coding-agent skill inside the Python wheel so
that installing the library is enough for an AI coding assistant (Claude Code,
Codex, or any Agent Skills-compatible harness) to discover the canonical usage
guide, house rules, and topic references.

Installing the bundled skill
----------------------------

After installing ``power-docx``::

    pip install power-docx

Install the skill into your default Claude skills directory
(``~/.claude/skills/power-docx``) using either the console script or the module
entry point::

    power-docx-skill install
    # equivalent:
    python -m power_docx.skill install

You can also install into a custom directory (either positionally or with
``--target``)::

    power-docx-skill install /path/to/skills/power-docx
    power-docx-skill install --target /path/to/skills/power-docx

Pass ``--no-overwrite`` to fail instead of replacing an existing install::

    power-docx-skill install --no-overwrite

Finding the packaged skill without copying
------------------------------------------

To print the on-disk location of the bundled ``SKILL.md`` and ``references/``
inside your active Python environment::

    power-docx-skill path
    # equivalent:
    python -m power_docx.skill path

Or from Python::

    from power_docx.skill import install_skill, skill_root

    src = skill_root()          # Path inside the installed power_docx package
    dest = install_skill()      # Copies SKILL.md + references/ to ~/.claude/skills/power-docx

Safety guarantees (refuse-to-clobber)
-------------------------------------

``TARGET`` is the skill's own directory (the directory that holds ``SKILL.md``),
not the parent ``skills/`` directory. To protect unrelated files if you
accidentally pass ``~/.claude/skills`` instead of
``~/.claude/skills/power-docx``, ``install_skill()`` enforces strict guards:

- An existing target is replaced **only** if it is empty or contains a
  ``SKILL.md`` whose frontmatter declares ``name: power-docx``.
- Non-empty directories that are not a previous ``power-docx`` install raise
  ``FileExistsError`` (CLI exit code ``1``) without modifying anything.
- Files raise ``NotADirectoryError`` and symbolic links raise
  ``FileExistsError``.
- Copies are staged in a sibling temporary directory and swapped in atomically
  so a partial failure never leaves a half-written skill behind.

What the skill contains
-----------------------

- ``SKILL.md`` — page-aware authoring workflow, cheat sheet of the most common
  ``power_docx`` calls, house rules, and common OOXML/Word pitfalls.
- ``references/`` — focused topic guides:

  - ``documents-and-sections.md``
  - ``styles.md``
  - ``tables.md``
  - ``text.md``
  - ``headers-and-footers.md``
  - ``comments.md``
  - ``images.md``
  - ``page-aware-layout.md``

Repository mirror
-----------------

When working inside a clone of the ``power-docx`` repository itself, an
identical copy of the skill lives at ``.claude/skills/power-docx/`` so repo-aware
agents pick it up automatically. Automated tests keep the packaged copy and the
repository mirror byte-identical.
