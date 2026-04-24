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
            dependencies=Poetry(on=self.target).install().run(),
        )

    def lock(self) -> int:
        return self.reporter.report(
            lock=Poetry(on=self.target).lock().run(),
        )

    def update(self) -> int:
        return self.reporter.report(
            update=Poetry(on=self.target).update().run(),
        )

    def lint(self) -> int:
        return self.reporter.report(
            poetry=Poetry(on=self.target).lint().run(),
            black=Ruff(on=self.target).format(check=True).run(),
            ruff=Ruff(on=self.target).lint(fix=False).run(),
            mypy=MyPy(on=self.target).run().run(),
        )

    def fix(self, unsafe: bool = False) -> int:
        return self.reporter.report(
            black=Ruff(on=self.target).format().run(),
            ruff=Ruff(on=self.target).lint(fix=True, unsafe=unsafe).run(),
        )

    def amend(self) -> int:
        return self.reporter.report(
            amend=Git().amend().run(),
        )
