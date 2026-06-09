from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import time

from codex.infra.dependabot import DependabotYaml
from codex.infra.program import (
    Command,
    Executable,
    MultiProgram,
    Program,
)
from codex.infra.pyproject import PyProjectToml
from codex.infra.result import TaskResult
from codex.infra.tools import MyPy, Pip, Poetry, PoetryRun, Pytest, Ruff


@dataclass(frozen=True)
class Codex:
    tools: CodexTools

    @classmethod
    def target(cls, target: Path) -> Codex:
        return cls(CodexTools(target))

    def ci(self, on: bool) -> Codex | CiCodex:
        if on:
            return CiCodex(tools=self.tools)

        return self

    def sync(self, dry_run: bool = False) -> TaskResult:
        return self.tools.sync(dry_run=dry_run).execute()

    def lock(self) -> TaskResult:
        return self.tools.lock().execute()

    def update(self) -> TaskResult:
        return self.tools.update().execute()

    def install(self) -> TaskResult:
        return self.tools.install().execute()

    def lint(self) -> TaskResult:
        return self.tools.lint().execute()

    def fix(self, unsafe: bool = False) -> TaskResult:
        return self.tools.fix(unsafe=unsafe).execute()

    def unit(self) -> TaskResult:
        return self.tools.unit().execute()

    def integration(self) -> TaskResult:
        return self.tools.integration().execute()

    def behaviour(self) -> TaskResult:
        return self.tools.behaviour().execute()

    def build(self, tag: str) -> TaskResult:
        return self.tools.build(tag).execute()


@dataclass(frozen=True)
class CiCodex:
    tools: CodexTools

    def lint(self) -> TaskResult:
        return (
            MultiProgram()
            .attach(self.tools.install())
            .attach(self.tools.lint())
            .execute()
        )

    def unit(self) -> TaskResult:
        return (
            MultiProgram()
            .attach(self.tools.install())
            .attach(self.tools.unit(in_ci=True))
            .execute()
        )

    def integration(self) -> TaskResult:
        return (
            MultiProgram()
            .attach(self.tools.install())
            .attach(self.tools.integration())
            .execute()
        )

    def behaviour(self) -> TaskResult:
        return (
            MultiProgram()
            .attach(self.tools.install())
            .attach(self.tools.behaviour(in_ci=True))
            .execute()
        )


@dataclass(frozen=True)
class CodexTools:
    target: Path

    def sync(self, dry_run: bool = False) -> Executable:
        return (
            MultiProgram()
            .attach(PyProjectToml(dry_run=dry_run).sync(self.target))
            .attach(DependabotYaml(dry_run=dry_run).sync(self.target))
        )

    def lock(self) -> Executable:
        return Program(name="lock", command=Poetry().lock())

    def update(self) -> Executable:
        return Program(name="update", command=Poetry().update())

    def install(self) -> Executable:
        return (
            MultiProgram()
            .attach(
                Program(
                    name="tools",
                    command=Pip().install("pip", "poetry"),
                )
            )
            .attach(
                Program(
                    name="dependencies",
                    command=Poetry().install(),
                )
            )
        )

    def lint(self) -> Executable:
        return (
            PoetryRun()
            .attach(
                Program(
                    name="poetry",
                    command=Poetry().lint(self.target),
                )
            )
            .attach(
                Program(
                    name="black",
                    command=Ruff(on=self.target).format().flag(check=True),
                )
            )
            .attach(
                Program(
                    name="ruff",
                    command=Ruff(on=self.target).lint(),
                )
            )
            .attach(
                Program(
                    name="mypy",
                    command=MyPy(on=self.target).check(),
                )
            )
        )

    def fix(self, unsafe: bool = False) -> Executable:
        return (
            PoetryRun()
            .attach(
                Program(
                    name="black",
                    command=Ruff(on=self.target).format(),
                )
            )
            .attach(
                Program(
                    name="ruff",
                    command=(
                        Ruff(on=self.target)
                        .lint()
                        .flag(fix=True)
                        .flag(unsafe_fixes=unsafe)
                    ),
                ),
            )
        )

    def unit(self, in_ci: bool = False) -> Executable:
        return PoetryRun().attach(
            Program(
                name="test",
                command=(
                    Pytest.on(self.target)
                    .run()
                    .flag(cov=not in_ci or None)
                    .flag(last_failed=not in_ci or None)
                ),
            )
        )

    def behaviour(self, in_ci: bool = False) -> Executable:
        return PoetryRun().attach(
            Program(
                name="behave",
                command=(
                    Command("behave")
                    .append(self.target / "tests" / "features")
                    .with_a(format="progress" if in_ci else "pretty")
                    .flag(summary=not in_ci)
                ),
            )
        )

    def integration(self) -> Executable:
        return (
            Poetry()
            .export(self.target)
            .attach(
                PoetryRun().attach(
                    Program(
                        name="test",
                        command=Pytest.on(self.target / "tests" / "integration").run(),
                    )
                )
            )
        )

    def build(self, tag: str) -> Executable:
        return (
            Poetry()
            .export(self.target)
            .attach(
                Program(
                    name="build",
                    command=(
                        Command("docker build")
                        .flag(tag=True)
                        .append(tag)
                        .flag(build_arg=True)
                        .with_a(RELEASE=Git().revision() or str(int(time())))
                        .append(self.target)
                    ),
                )
            )
        )


@dataclass(frozen=True)
class Git:
    def revision(self, of: str = "HEAD", short: bool = True) -> str:
        return (
            Program(Command("git rev-parse").flag(short=short).append(of))
            .execute()
            .stdout
        )

    def amend(self) -> TaskResult:
        return Program(
            name="amend",
            command=Command("git commit")
            .flag(all=True)
            .flag(amend=True)
            .flag(edit=False),
        ).execute()
