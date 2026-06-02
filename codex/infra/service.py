from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import time

from codex.infra.dependabot import DependabotYaml
from codex.infra.program import Executable, MultiProgram, Program
from codex.infra.pyproject import PyProjectToml
from codex.infra.result import TaskResult
from codex.infra.tools import MyPy, Pip, Poetry, PoetryRun, Pytest, Ruff


@dataclass(frozen=True)
class CodexTest:
    target: Path

    def ci(self, on: bool) -> CodexTest:
        _ = on

        return self

    def unit(self) -> TaskResult:
        return CodexTools(self.target).unit().execute()

    def integration(self) -> TaskResult:
        return CodexTools(self.target).integration().execute()

    def behaviour(self) -> TaskResult:
        return CodexTools(self.target).behaviour().execute()


@dataclass(frozen=True)
class Codex:
    target: Path

    def ci(self, on: bool) -> Codex:
        _ = on

        return self

    def sync(self, dry_run: bool = False) -> TaskResult:
        return CodexTools(self.target).sync(dry_run=dry_run).execute()

    def lock(self) -> TaskResult:
        return Poetry().lock().execute().named("lock")

    def update(self) -> TaskResult:
        return Poetry().update().execute().named("update")

    def install(self) -> TaskResult:
        return CodexTools(self.target).install().execute()

    def lint(self) -> TaskResult:
        return CodexTools(self.target).lint().execute()

    def fix(self, unsafe: bool = False) -> TaskResult:
        return CodexTools(self.target).fix(unsafe=unsafe).execute()

    def build(self, tag: str) -> TaskResult:
        return CodexTools(self.target).build(tag).execute()


@dataclass(frozen=True)
class CodexTools:
    target: Path

    def sync(self, dry_run: bool = False) -> Executable:
        return (
            MultiProgram()
            .attach(pyproject=PyProjectToml(dry_run=dry_run).sync(self.target))
            .attach(dependabot=DependabotYaml(dry_run=dry_run).sync(self.target))
        )

    def install(self) -> Executable:
        return (
            MultiProgram()
            .attach(tools=Pip().install("pip", "poetry"))
            .attach(dependencies=Poetry().install())
        )

    def lint(self) -> Executable:
        return (
            PoetryRun()
            .attach(poetry=Poetry().lint(self.target))
            .attach(black=Ruff(on=self.target).format().flag(check=True))
            .attach(ruff=Ruff(on=self.target).lint())
            .attach(mypy=MyPy(on=self.target).check())
        )

    def fix(self, unsafe: bool = False) -> Executable:
        return (
            PoetryRun()
            .attach(black=Ruff(on=self.target).format())
            .attach(
                ruff=Ruff(on=self.target)
                .lint()
                .flag(fix=True)
                .flag(unsafe_fixes=unsafe)
            )
        )

    def unit(self) -> Executable:
        return PoetryRun().attach(
            pytest=Pytest.on(self.target).run().flag(cov=True).flag(last_failed=True)
        )

    def behaviour(self) -> Executable:
        return PoetryRun().attach(
            behave=Program("behave").append(self.target / "tests" / "features")
        )

    def integration(self) -> Executable:
        return (
            MultiProgram()
            .attach(install=Pip().install("poetry", "poetry-plugin-export"))
            .attach(export=Poetry().export(self.target))
            .attach(
                test=PoetryRun().attach(
                    pytest=Pytest.on(self.target / "tests" / "integration").run()
                )
            )
            .attach(teardown=Program("rm").append(self.target / "requirements.txt"))
        )

    def build(self, tag: str) -> Executable:
        return (
            MultiProgram()
            .attach(install=Pip().install("poetry", "poetry-plugin-export"))
            .attach(export=Poetry().export(self.target))
            .attach(
                build=(
                    Program("docker build")
                    .flag(tag=True)
                    .append(tag)
                    .flag(build_arg=True)
                    .with_a(RELEASE=Git().revision() or str(int(time())))
                    .append(self.target)
                )
            )
            .attach(teardown=Program("rm").append(self.target / "requirements.txt"))
        )


@dataclass(frozen=True)
class Git:
    def revision(self, of: str = "HEAD", short: bool = True) -> str:
        return Program("git rev-parse").flag(short=short).append(of).execute().stdout

    def amend(self) -> TaskResult:
        return (
            Program("git commit")
            .flag(all=True)
            .flag(amend=True)
            .flag(edit=False)
            .execute()
            .named("amend")
        )
