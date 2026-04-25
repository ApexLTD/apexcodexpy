from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from codex.reporters import Reporter
from codex.tasks import Toml
from codex.tasks.result import ComboResult
from codex.tools import MyPy, Pip, Poetry, Program, Ruff


@dataclass(frozen=True)
class Codex:
    target: Path
    reporter: Reporter

    def sync(self, dry_run: bool = False) -> ComboResult:
        return (
            ComboResult()
            .attach(Toml(dry_run=dry_run).sync(self.target))
            .report(self.reporter)
        )

    def install(self) -> ComboResult:
        return (
            ComboResult()
            .attach(Pip().install("pip", "poetry"))
            .attach(Poetry().install())
            .report(self.reporter)
        )

    def lock(self) -> ComboResult:
        return ComboResult().attach(Poetry().lock()).report(self.reporter)

    def update(self) -> ComboResult:
        return ComboResult().attach(Poetry().update()).report(self.reporter)

    def lint(self) -> ComboResult:
        return (
            ComboResult()
            .attach(Poetry().lint(self.target))
            .attach(
                Poetry(session="black").run(
                    Ruff(on=self.target).format().flag(check=True)
                )
            )
            .attach(Poetry(session="ruff").run(Ruff(on=self.target).lint()))
            .attach(Poetry(session="mypy").run(MyPy(on=self.target).check()))
            .report(self.reporter)
        )

    def fix(self, unsafe: bool = False) -> ComboResult:
        return (
            ComboResult()
            .attach(Poetry(session="black").run(Ruff(on=self.target).format()))
            .attach(
                Poetry(session="ruff").run(
                    Ruff(on=self.target).lint().flag(fix=True).flag(unsafe_fixes=unsafe)
                )
            )
            .report(self.reporter)
        )


@dataclass(frozen=True)
class Git:
    reporter: Reporter

    def amend(self) -> ComboResult:
        return (
            ComboResult()
            .attach(
                amend=(
                    Program("git commit")
                    .flag(all=True)
                    .flag(amend=True)
                    .flag(edit=False)
                    .run()
                )
            )
            .report(self.reporter)
        )
