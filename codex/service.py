from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import time

from codex.tasks import ComboResult, DependabotYaml, PyProjectToml, TaskResult
from codex.tools import MyPy, Pip, Poetry, Program, Ruff


@dataclass(frozen=True)
class CiMode:
    codex: Codex

    def lint(self) -> TaskResult:
        return (
            ComboResult()
            .attach(install=self.codex.install())
            .attach(lint=self.codex.lint())
        )

    def test(self) -> TaskResult:
        return (
            ComboResult()
            .attach(install=self.codex.install())
            .attach(pytest=Poetry().run(Program("pytest").append(self.codex.target)))
        )


@dataclass(frozen=True)
class Codex:
    target: Path

    def ci(self, on: bool) -> CiMode | Codex:
        if on:
            return CiMode(self)

        return self

    def sync(self, dry_run: bool = False) -> TaskResult:
        return (
            ComboResult()
            .attach(pyproject=PyProjectToml(dry_run=dry_run).sync(self.target))
            .attach(dependabot=DependabotYaml(dry_run=dry_run).sync(self.target))
        )

    def install(self) -> TaskResult:
        return (
            ComboResult()
            .attach(tools=Pip().install("pip", "poetry"))
            .attach(dependencies=Poetry().install())
        )

    def lock(self) -> TaskResult:
        return ComboResult().attach(lock=Poetry().lock())

    def update(self) -> TaskResult:
        return ComboResult().attach(update=Poetry().update())

    def lint(self) -> TaskResult:
        return (
            ComboResult()
            .attach(poetry=Poetry().lint(self.target))
            .attach(black=Poetry().run(Ruff(on=self.target).format().flag(check=True)))
            .attach(ruff=Poetry().run(Ruff(on=self.target).lint()))
            .attach(mypy=Poetry().run(MyPy(on=self.target).check()))
        )

    def fix(self, unsafe: bool = False) -> TaskResult:
        return (
            ComboResult()
            .attach(black=Poetry().run(Ruff(on=self.target).format()))
            .attach(
                ruff=Poetry().run(
                    Ruff(on=self.target).lint().flag(fix=True).flag(unsafe_fixes=unsafe)
                )
            )
        )

    def test(self) -> TaskResult:
        return ComboResult().attach(
            pytest=Poetry().run(
                Program("pytest")
                .append(self.target)
                .flag(cov=True)
                .flag(last_failed=True)
            )
        )

    def build(self, tag: str) -> TaskResult:
        return (
            ComboResult()
            .attach(
                setup=(
                    ComboResult()
                    .attach(tools=Pip().install("poetry", "poetry-plugin-export"))
                    .attach(export=Poetry().export(self.target))
                )
            )
            .attach(
                docker=(
                    Program("docker build")
                    .flag(tag=True)
                    .append(tag)
                    .flag(build_arg=True)
                    .with_a(RELEASE=Git().revision() or str(int(time())))
                    .append(self.target)
                    .run()
                )
            )
            .attach(
                teardown=Program("rm").append(self.target / "requirements.txt").run()
            )
        )


@dataclass(frozen=True)
class Git:
    def revision(self, of: str = "HEAD", short: bool = True) -> str:
        return Program("git rev-parse").flag(short=short).append(of).run().stdout

    def amend(self) -> TaskResult:
        return ComboResult().attach(
            amend=(
                Program("git commit")
                .flag(all=True)
                .flag(amend=True)
                .flag(edit=False)
                .run()
            )
        )
