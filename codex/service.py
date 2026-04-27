from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from codex.tasks import ComboResult, TaskResult, Toml
from codex.tools import MyPy, Pip, Poetry, Program, Ruff


@dataclass(frozen=True)
class Codex:
    target: Path

    def sync(self, dry_run: bool = False) -> TaskResult:
        return ComboResult().attach(sync=Toml(dry_run=dry_run).sync(self.target))

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


@dataclass(frozen=True)
class Git:
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
