from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import time

from codex.infra.dependabot import DependabotYaml
from codex.infra.program import MultiProgram, Program
from codex.infra.pyproject import PyProjectToml
from codex.infra.result import TaskResult
from codex.infra.tools import MyPy, Pip, Poetry, PoetryRun, Pytest, Ruff


@dataclass(frozen=True)
class Codex:
    target: Path

    def ci(self, on: bool) -> Codex:
        _ = on

        return self

    def sync(self, dry_run: bool = False) -> TaskResult:
        return (
            MultiProgram()
            .attach(pyproject=PyProjectToml(dry_run=dry_run).sync(self.target))
            .attach(dependabot=DependabotYaml(dry_run=dry_run).sync(self.target))
            .execute()
        )

    def lock(self) -> TaskResult:
        return Poetry().lock().execute().named("lock")

    def update(self) -> TaskResult:
        return Poetry().update().execute().named("update")

    def install(self) -> TaskResult:
        return (
            MultiProgram()
            .attach(tools=Pip().install("pip", "poetry"))
            .attach(dependencies=Poetry().install())
            .execute()
        )

    def lint(self) -> TaskResult:
        return (
            PoetryRun()
            .attach(poetry=Poetry().lint(self.target))
            .attach(black=Ruff(on=self.target).format().flag(check=True))
            .attach(ruff=Ruff(on=self.target).lint())
            .attach(mypy=MyPy(on=self.target).check())
            .execute()
        )

    def fix(self, unsafe: bool = False) -> TaskResult:
        return (
            PoetryRun()
            .attach(black=Ruff(on=self.target).format())
            .attach(
                ruff=Ruff(on=self.target)
                .lint()
                .flag(fix=True)
                .flag(unsafe_fixes=unsafe)
            )
            .execute()
        )

    def test(self) -> TaskResult:
        return self.test_unit()

    def test_unit(self) -> TaskResult:
        return CodexTest(self.target).unit()

    def test_integration(self) -> TaskResult:
        return CodexTest(self.target).integration()

    def test_behaviour(self) -> TaskResult:
        return CodexTest(self.target).behaviour()

    def build(self, tag: str) -> TaskResult:
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
            .execute()
        )


@dataclass(frozen=True)
class CodexTest:
    target: Path

    def unit(self) -> TaskResult:
        return (
            PoetryRun()
            .attach(
                pytest=Pytest.on(self.target)
                .run()
                .flag(cov=True)
                .flag(last_failed=True)
            )
            .execute()
        )

    def integration(self) -> TaskResult:
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
            .execute()
        )

    def behaviour(self) -> TaskResult:
        return (
            PoetryRun()
            .attach(behave=Program("behave").append(self.target / "tests" / "features"))
            .execute()
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
