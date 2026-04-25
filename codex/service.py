from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from codex.tasks import Toml
from codex.tasks.result import ComboResult
from codex.tools import MyPy, Pip, Poetry, Program, Ruff


@dataclass(frozen=True)
class Codex:
    target: Path

    def sync(self, dry_run: bool = False) -> ComboResult:
        return ComboResult().attach(Toml(dry_run=dry_run).sync(self.target))

    def install(self) -> ComboResult:
        return (
            ComboResult()
            .attach(Pip().install("pip", "poetry"))
            .attach(Poetry().install())
        )

    def lock(self) -> ComboResult:
        return ComboResult().attach(Poetry().lock())

    def update(self) -> ComboResult:
        return ComboResult().attach(Poetry().update())

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
        )


@dataclass(frozen=True)
class Git:
    def amend(self) -> ComboResult:
        return ComboResult().attach(
            amend=(
                Program("git commit")
                .flag(all=True)
                .flag(amend=True)
                .flag(edit=False)
                .run()
            )
        )
