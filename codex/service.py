from dataclasses import dataclass
from pathlib import Path

from codex.reporters import Reporter
from codex.tasks import Toml
from codex.tools import Git, MyPy, Pip, Poetry, Ruff


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
            dependencies=Poetry().install().run(),
        )

    def lock(self) -> int:
        return self.reporter.report(
            lock=Poetry().lock().run(),
        )

    def update(self) -> int:
        return self.reporter.report(
            update=Poetry().update().run(),
        )

    def lint(self) -> int:
        return self.reporter.report(
            poetry=Poetry().lint(self.target),
            black=Poetry().run(Ruff().format(self.target, check=True)),
            ruff=Poetry().run(Ruff().lint(self.target, fix=False)),
            mypy=Poetry().run(MyPy().check(self.target)),
        )

    def fix(self, unsafe: bool = False) -> int:
        return self.reporter.report(
            black=Poetry().run(Ruff().format(self.target)),
            ruff=Poetry().run(Ruff().lint(self.target, fix=True, unsafe=unsafe)),
        )

    def amend(self) -> int:
        return self.reporter.report(
            amend=Git().amend().run(),
        )
