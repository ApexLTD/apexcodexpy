from dataclasses import dataclass
from pathlib import Path

from codex.reporters import Reporter
from codex.tasks import (
    RunGitAmend,
    RunMypy,
    RunRuffCheck,
    RunRuffFormat,
    SyncToml,
)
from codex.tools import Pip, Poetry


@dataclass(frozen=True)
class PyCodex:
    target: Path
    reporter: Reporter

    def sync(self, dry_run: bool = False) -> int:
        return self.reporter.report(
            sync=SyncToml(of=self.target, dry_run=dry_run).run()
        )

    def install(self) -> int:
        return self.reporter.report(
            tools=Pip().install("pip", "poetry"),
            dependencies=Poetry(on=self.target).install(),
        )

    def lock(self) -> int:
        return self.reporter.report(
            lock=Poetry(on=self.target).lock(),
        )

    def update(self) -> int:
        return self.reporter.report(
            update=Poetry(on=self.target).update(),
        )

    def lint(self) -> int:
        return self.reporter.report(
            poetry=Poetry(on=self.target).lint(),
            black=RunRuffFormat(on=self.target, check=True).run(),
            ruff=RunRuffCheck(on=self.target).run(),
            mypy=RunMypy(on=self.target).run(),
        )

    def fix(self, unsafe: bool = False) -> int:
        return self.reporter.report(
            black=RunRuffFormat(on=self.target).run(),
            ruff=RunRuffCheck(on=self.target, fix=True, unsafe=unsafe).run(),
        )

    def amend(self) -> int:
        return self.reporter.report(
            amend=RunGitAmend().run(),
        )
