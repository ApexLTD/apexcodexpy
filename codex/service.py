from dataclasses import dataclass
from pathlib import Path

from codex.reporters import Reporter
from codex.tasks import (
    RunGitAmend,
    RunMypy,
    SyncToml,
)
from codex.tasks.program import Program
from codex.tools import Pip, Poetry, Ruff


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
            black=Ruff(on=self.target).format(check=True),
            ruff=Ruff(on=self.target).lint(fix=False),
            mypy=Program().run(RunMypy(on=self.target)),
        )

    def fix(self, unsafe: bool = False) -> int:
        return self.reporter.report(
            black=Ruff(on=self.target).format(),
            ruff=Ruff(on=self.target).lint(fix=True, unsafe=unsafe),
        )

    def amend(self) -> int:
        return self.reporter.report(
            amend=Program().run(RunGitAmend()),
        )
