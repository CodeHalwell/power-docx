Feature: Bundled coding-agent skill
  In order to use power-docx effectively from an AI coding agent
  As a developer using power-docx
  I need to locate and safely install the bundled skill


  Scenario: Locate the bundled skill root inside the package
     When I query the bundled skill root
     Then the skill root contains SKILL.md and topic references


  Scenario: Install the bundled skill into a fresh directory
    Given a clean temporary skill destination
     When I run the skill CLI with "install" into that destination
     Then the skill CLI exits with code 0
      And the destination contains SKILL.md and topic references


  Scenario: Refuse to clobber an unrelated non-empty directory
    Given an unrelated non-empty directory
     When I run the skill CLI with "install" into that destination
     Then the skill CLI exits with code 1
      And the unrelated directory contents remain intact


  Scenario: Honour --no-overwrite on an existing install
    Given a destination already containing an installed power-docx skill
     When I run the skill CLI with "install --no-overwrite" into that destination
     Then the skill CLI exits with code 1
