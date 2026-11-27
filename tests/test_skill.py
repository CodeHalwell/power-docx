"""Unit tests for the bundled coding-agent skill (`power_docx.skill`)."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest


class DescribeSkillRoot:
    def it_returns_a_directory_containing_skill_md_and_references(self):
        from power_docx.skill import skill_root

        root = skill_root()
        assert root.is_dir()
        assert (root / "SKILL.md").is_file()
        assert (root / "references").is_dir()
        refs = sorted(p.name for p in (root / "references").glob("*.md"))
        assert refs == [
            "comments.md",
            "documents-and-sections.md",
            "headers-and-footers.md",
            "images.md",
            "page-aware-layout.md",
            "styles.md",
            "tables.md",
            "text.md",
        ]


class DescribeInstallSkill:
    def it_copies_skill_md_and_references_into_target(self, tmp_path: Path):
        from power_docx.skill import install_skill

        target = tmp_path / "skills" / "power-docx"
        dest = install_skill(target=target)

        assert dest == target
        assert (dest / "SKILL.md").is_file()
        assert (dest / "references").is_dir()
        assert not (dest / "__init__.py").exists()
        assert not (dest / "__main__.py").exists()
        refs = list((dest / "references").glob("*.md"))
        assert len(refs) == 8

    def it_overwrites_an_existing_install_by_default(self, tmp_path: Path):
        from power_docx.skill import install_skill

        target = tmp_path / "power-docx"
        install_skill(target=target)
        stray = target / "stray.md"
        stray.write_text("from an older version", encoding="utf-8")

        install_skill(target=target)

        assert not stray.exists()
        assert (target / "SKILL.md").is_file()

    def it_refuses_to_overwrite_when_overwrite_is_false(self, tmp_path: Path):
        from power_docx.skill import install_skill

        target = tmp_path / "power-docx"
        install_skill(target=target)

        with pytest.raises(FileExistsError, match="refusing to overwrite"):
            install_skill(target=target, overwrite=False)

    def it_accepts_a_str_target(self, tmp_path: Path):
        from power_docx.skill import install_skill

        dest = install_skill(target=str(tmp_path / "power-docx"))

        assert (dest / "SKILL.md").is_file()

    def it_installs_into_an_existing_empty_directory(self, tmp_path: Path):
        from power_docx.skill import install_skill

        target = tmp_path / "power-docx"
        target.mkdir()

        install_skill(target=target)

        assert (target / "SKILL.md").is_file()
        assert (target / "references").is_dir()

    def but_it_refuses_to_replace_a_directory_that_is_not_this_skill(self, tmp_path: Path):
        """`install ~/.claude/skills` must never wipe the user's other skills."""
        from power_docx.skill import install_skill

        skills_dir = tmp_path / "skills"
        other = skills_dir / "another-skill"
        other.mkdir(parents=True)
        (other / "SKILL.md").write_text("---\nname: another-skill\n---\n", encoding="utf-8")
        (skills_dir / "notes.txt").write_text("keep me", encoding="utf-8")

        with pytest.raises(FileExistsError, match="not a power-docx skill install"):
            install_skill(target=skills_dir)

        assert (other / "SKILL.md").read_text(encoding="utf-8") == "---\nname: another-skill\n---\n"
        assert (skills_dir / "notes.txt").read_text(encoding="utf-8") == "keep me"
        assert sorted(p.name for p in skills_dir.iterdir()) == ["another-skill", "notes.txt"]

    def and_it_refuses_to_replace_a_different_skill(self, tmp_path: Path):
        from power_docx.skill import install_skill

        target = tmp_path / "some-skill"
        target.mkdir()
        (target / "SKILL.md").write_text(
            "---\nname: some-skill\ndescription: x\n---\n# body\n", encoding="utf-8"
        )

        with pytest.raises(FileExistsError, match="not a power-docx skill install"):
            install_skill(target=target)

        assert (target / "SKILL.md").read_text(encoding="utf-8").startswith("---\nname: some-skill")

    def and_it_reports_a_file_target_as_not_a_directory(self, tmp_path: Path):
        from power_docx.skill import install_skill

        target = tmp_path / "power-docx"
        target.write_text("I am a file", encoding="utf-8")

        with pytest.raises(NotADirectoryError, match="is a file, not a directory"):
            install_skill(target=target)

        assert target.read_text(encoding="utf-8") == "I am a file"

    def and_it_refuses_to_replace_a_symlink(self, tmp_path: Path):
        from power_docx.skill import install_skill

        real = tmp_path / "real"
        install_skill(target=real)
        link = tmp_path / "link"
        try:
            link.symlink_to(real, target_is_directory=True)
        except (OSError, NotImplementedError):  # pragma: no cover
            pytest.skip("symbolic links are not available here")

        with pytest.raises(FileExistsError, match="symbolic link"):
            install_skill(target=link)

        assert link.is_symlink()
        assert (real / "SKILL.md").is_file()

    def it_keeps_the_previous_install_when_the_copy_fails(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        from power_docx.skill import install_skill

        target = tmp_path / "power-docx"
        install_skill(target=target)
        (target / "SKILL.md").write_text(
            "---\nname: power-docx\n---\nprevious version\n", encoding="utf-8"
        )

        def failing_copytree(*args: object, **kwargs: object) -> None:
            raise OSError("disk full")

        monkeypatch.setattr(shutil, "copytree", failing_copytree)

        with pytest.raises(OSError, match="disk full"):
            install_skill(target=target)

        assert "previous version" in (target / "SKILL.md").read_text(encoding="utf-8")
        assert [p.name for p in tmp_path.iterdir()] == ["power-docx"]


class DescribeSkillCli:
    def it_prints_the_skill_root_by_default_and_for_path(
        self, capsys: pytest.CaptureFixture[str]
    ):
        from power_docx.skill import skill_root
        from power_docx.skill.__main__ import main

        assert main([]) == 0
        assert capsys.readouterr().out.strip() == str(skill_root())

        assert main(["path"]) == 0
        assert capsys.readouterr().out.strip() == str(skill_root())

    def it_installs_into_a_positional_target(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ):
        from power_docx.skill.__main__ import main

        target = tmp_path / "power-docx"

        assert main(["install", str(target)]) == 0
        assert (target / "SKILL.md").is_file()
        assert str(target) in capsys.readouterr().out

    def it_installs_into_a_target_given_as_an_option(self, tmp_path: Path):
        from power_docx.skill.__main__ import main

        target = tmp_path / "skills" / "power-docx"

        assert main(["install", "--target", str(target)]) == 0
        assert (target / "SKILL.md").is_file()

    def but_it_rejects_a_target_given_both_ways(self, tmp_path: Path):
        from power_docx.skill.__main__ import main

        with pytest.raises(SystemExit) as excinfo:
            main(["install", str(tmp_path / "a"), "--target", str(tmp_path / "b")])

        assert excinfo.value.code == 2
        assert not (tmp_path / "a").exists()
        assert not (tmp_path / "b").exists()

    def it_exits_non_zero_without_deleting_an_unrelated_directory(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ):
        from power_docx.skill.__main__ import main

        skills_dir = tmp_path / "skills"
        (skills_dir / "another-skill").mkdir(parents=True)
        (skills_dir / "another-skill" / "SKILL.md").write_text(
            "---\nname: another-skill\n---\n", encoding="utf-8"
        )

        assert main(["install", str(skills_dir)]) == 1

        assert (skills_dir / "another-skill" / "SKILL.md").is_file()
        assert not (skills_dir / "SKILL.md").exists()
        err = capsys.readouterr().err
        assert "refusing to replace" in err
        assert str(skills_dir / "power-docx") in err

    def it_reports_a_file_target_cleanly(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ):
        from power_docx.skill.__main__ import main

        target = tmp_path / "a-file"
        target.write_text("x", encoding="utf-8")

        assert main(["install", "--target", str(target)]) == 1

        assert target.read_text(encoding="utf-8") == "x"
        assert "is a file, not a directory" in capsys.readouterr().err

    def it_honours_no_overwrite(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ):
        from power_docx.skill.__main__ import main

        target = tmp_path / "power-docx"
        assert main(["install", str(target)]) == 0

        assert main(["install", str(target), "--no-overwrite"]) == 1
        assert "refusing to overwrite" in capsys.readouterr().err


class DescribeRepoSkillMirror:
    def it_stays_in_sync_with_the_packaged_skill(self):
        from power_docx.skill import skill_root

        repo_root = Path(__file__).resolve().parent.parent
        mirror = repo_root / ".claude" / "skills" / "power-docx"
        if not mirror.is_dir():  # pragma: no cover - e.g. sdist installed without .claude
            pytest.skip(".claude/skills/power-docx mirror not present")

        src = skill_root()
        src_files = sorted(
            p.relative_to(src)
            for p in src.rglob("*.md")
            if p.is_file()
        )
        mirror_files = sorted(
            p.relative_to(mirror)
            for p in mirror.rglob("*.md")
            if p.is_file()
        )
        assert mirror_files == src_files
        for rel in src_files:
            assert (mirror / rel).read_bytes() == (src / rel).read_bytes(), (
                f"{rel} drifted between src/power_docx/skill and .claude/skills/power-docx"
            )
