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
        return self.reporter.report(Toml(dry_run=dry_run).sync(self.target))

    def install(self) -> int:
        return self.reporter.report(
            Pip().install("pip", "poetry"),
            Poetry().install(),
        )

    def lock(self) -> int:
        return self.reporter.report(Poetry().lock())

    def update(self) -> int:
        return self.reporter.report(Poetry().update())

    def lint(self) -> int:
        return self.reporter.report(
            Poetry().lint(self.target),
            Poetry().run(black=Ruff().format(self.target, check=True)),
            Poetry().run(ruff=Ruff().lint(self.target)),
            Poetry().run(mypy=MyPy().check(self.target)),
        )

    def fix(self, unsafe: bool = False) -> int:
        return self.reporter.report(
            Poetry().run(black=Ruff().format(self.target)),
            Poetry().run(ruff=Ruff().lint(self.target, fix=True, unsafe=unsafe)),
        )


@dataclass(frozen=True)
class Git:
    reporter: Reporter

    def amend(self) -> int:
        return self.reporter.report(
            Program("git commit")
            .flag(all=True)
            .flag(amend=True)
            .flag(edit=False)
            .run()
            .named("amend")
        )
