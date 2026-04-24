from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from codex.reporters import Reporter
from codex.tasks import Toml
from codex.tools import MyPy, Pip, Poetry, Program, Ruff


@dataclass(frozen=True)
class Codex:
    target: Path
    reporter: Reporter

    def sync(self, dry_run: bool = False) -> int:
        return self.reporter.report(
            sync=Toml(of=self.target, dry_run=dry_run).sync(),
        )

    def install(self) -> int:
        return self.reporter.report(
            tools=Pip().install("pip", "poetry").run(),
            dependencies=Poetry().install(),
        )

    def lock(self) -> int:
        return self.reporter.report(lock=Poetry().lock())

    def update(self) -> int:
        return self.reporter.report(update=Poetry().update())

    def lint(self) -> int:
        return self.reporter.report(
            poetry=Poetry().lint(self.target),
            black=Poetry().run(Ruff().format(self.target, check=True)),
            ruff=Poetry().run(Ruff().lint(self.target)),
            mypy=Poetry().run(MyPy().check(self.target)),
        )

    def fix(self, unsafe: bool = False) -> int:
        return self.reporter.report(
            black=Poetry().run(Ruff().format(self.target)),
            ruff=Poetry().run(Ruff().lint(self.target, fix=True, unsafe=unsafe)),
        )


@dataclass(frozen=True)
class Git:
    reporter: Reporter

    def amend(self) -> int:
        return self.reporter.report(
            amend=(
                Program("git commit")
                .flag(all=True)
                .flag(amend=True)
                .flag(edit=False)
                .run()
            )
        )
