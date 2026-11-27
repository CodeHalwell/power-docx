"""Step implementations for bundled coding-agent skill features."""

from __future__ import annotations

import tempfile
from pathlib import Path

from behave import given, then, when
from behave.runner import Context

from power_docx.skill import install_skill, skill_root
from power_docx.skill.__main__ import main

# given ====================================================


@given("a clean temporary skill destination")
def given_a_clean_temporary_skill_destination(context: Context):
    tmpdir = tempfile.TemporaryDirectory()
    context.add_cleanup(tmpdir.cleanup)
    context.skill_target = Path(tmpdir.name) / "power-docx"


@given("an unrelated non-empty directory")
def given_an_unrelated_non_empty_directory(context: Context):
    tmpdir = tempfile.TemporaryDirectory()
    context.add_cleanup(tmpdir.cleanup)
    target = Path(tmpdir.name) / "skills"
    other = target / "other-skill"
    other.mkdir(parents=True)
    (other / "SKILL.md").write_text("---\nname: other-skill\n---\n", encoding="utf-8")
    context.skill_target = target


@given("a destination already containing an installed power-docx skill")
def given_a_destination_already_containing_an_installed_skill(context: Context):
    tmpdir = tempfile.TemporaryDirectory()
    context.add_cleanup(tmpdir.cleanup)
    target = Path(tmpdir.name) / "power-docx"
    install_skill(target=target)
    context.skill_target = target


# when =====================================================


@when("I query the bundled skill root")
def when_I_query_the_bundled_skill_root(context: Context):
    context.skill_root_path = skill_root()


@when('I run the skill CLI with "{subcommand}" into that destination')
def when_I_run_the_skill_cli_into_that_destination(context: Context, subcommand: str):
    argv = [*subcommand.split(), str(context.skill_target)]
    context.cli_exit_code = main(argv)


# then =====================================================


@then("the skill root contains SKILL.md and topic references")
def then_the_skill_root_contains_skill_md_and_topic_references(context: Context):
    root: Path = context.skill_root_path
    assert (root / "SKILL.md").is_file()
    assert len(list((root / "references").glob("*.md"))) >= 8


@then("the skill CLI exits with code {code:d}")
def then_the_skill_cli_exits_with_code(context: Context, code: int):
    assert context.cli_exit_code == code, f"expected {code}, got {context.cli_exit_code}"


@then("the destination contains SKILL.md and topic references")
def then_the_destination_contains_skill_md_and_topic_references(context: Context):
    dest: Path = context.skill_target
    assert (dest / "SKILL.md").is_file()
    assert len(list((dest / "references").glob("*.md"))) >= 8
    assert not (dest / "__init__.py").exists()


@then("the unrelated directory contents remain intact")
def then_the_unrelated_directory_contents_remain_intact(context: Context):
    target: Path = context.skill_target
    assert (target / "other-skill" / "SKILL.md").is_file()
    assert not (target / "SKILL.md").exists()
