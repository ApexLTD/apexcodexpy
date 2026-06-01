from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import time

from codex.infra.dependabot import DependabotYaml
from codex.infra.program import MultiProgram, Program
from codex.infra.pyproject import PyProjectToml
from codex.infra.result import ComboResult, TaskResult
from codex.infra.tools import MyPy, Pip, Poetry, Pytest, Ruff


@dataclass(frozen=True)
class Codex:
    target: Path

    in_ci: bool = False

    def ci(self, on: bool) -> Codex:
        return Codex(self.target, in_ci=on)

    def sync(self, dry_run: bool = False) -> TaskResult:
        return (
            ComboResult()
            .attach(pyproject=PyProjectToml(dry_run=dry_run).sync(self.target))
            .attach(dependabot=DependabotYaml(dry_run=dry_run).sync(self.target))
        )

    def install(self) -> TaskResult:
        return self._install(when=True).execute()

    def _install(self, when: bool) -> MultiProgram:
        return (
            (
                MultiProgram()
                .attach(tools=Pip().install("pip", "poetry"))
                .attach(dependencies=Poetry().install())
            )
            if when
            else MultiProgram()
        )

    def lock(self) -> TaskResult:
        return MultiProgram().attach(lock=Poetry().lock()).execute()

    def update(self) -> TaskResult:
        return MultiProgram().attach(update=Poetry().update()).execute()

    def lint(self) -> TaskResult:
        return (
            self._install(when=self.in_ci)
            .attach(poetry=Poetry().lint(self.target))
            .attach(black=Poetry().run(Ruff(on=self.target).format().flag(check=True)))
            .attach(ruff=Poetry().run(Ruff(on=self.target).lint()))
            .attach(mypy=Poetry().run(MyPy(on=self.target).check()))
            .execute()
        )

    def fix(self, unsafe: bool = False) -> TaskResult:
        return (
            MultiProgram()
            .attach(black=Poetry().run(Ruff(on=self.target).format()))
            .attach(
                ruff=Poetry().run(
                    Ruff(on=self.target).lint().flag(fix=True).flag(unsafe_fixes=unsafe)
                )
            )
            .execute()
        )

    def test(self) -> TaskResult:
        return self._install(when=self.in_ci).execute().attach(self.test_unit())

    def test_unit(self) -> TaskResult:
        return CodexTest(self.target).ci(on=self.in_ci).unit()

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

    in_ci: bool = False

    def ci(self, on: bool = False) -> CodexTest:
        return CodexTest(self.target, in_ci=on)

    def unit(self) -> TaskResult:
        return (
            MultiProgram()
            .attach(
                pytest=Poetry().run(
                    Pytest.on(self.target).run(
                        with_coverage=self._when_not_in_ci(),
                        last_failed=self._when_not_in_ci(),
                    )
                )
            )
            .execute()
        )

    def _when_not_in_ci(self) -> bool | None:
        return None if self.in_ci else True

    def integration(self) -> TaskResult:
        return (
            MultiProgram()
            .attach(install=Pip().install("poetry", "poetry-plugin-export"))
            .attach(export=Poetry().export(self.target))
            .attach(
                test=Poetry().run(
                    Pytest.on(self.target / "tests" / "integration").run()
                )
            )
            .attach(teardown=Program("rm").append(self.target / "requirements.txt"))
            .execute()
        )

    def behaviour(self) -> TaskResult:
        return (
            MultiProgram()
            .attach(
                behave=Poetry().run(
                    Program("behave").append(self.target / "tests" / "features")
                )
            )
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
