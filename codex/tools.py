from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from codex.tasks import TaskResult
from codex.tasks.program import ShellProgram


@dataclass(frozen=True, kw_only=True)
class Pip(ShellProgram):
    name: str = "pip"

    def install(self, *packages: str) -> TaskResult:
        return self.run("install", "--upgrade", *packages)


@dataclass(frozen=True, kw_only=True)
class Poetry(ShellProgram):
    on: Path

    name: str = "poetry"

    def install(self) -> TaskResult:
        return self.run("install")

    def lock(self) -> TaskResult:
        return self.run("lock")

    def update(self) -> TaskResult:
        return self.run("update")

    def lint(self) -> TaskResult:
        return self.run(f"check --strict --project={self.on}")


@dataclass(frozen=True, kw_only=True)
class Ruff(ShellProgram):
    on: Path

    name: str = "ruff"

    def lint(self, fix: bool = True, unsafe: bool = False) -> TaskResult:
        return self.run(
            "check",
            self.on,
            "--fix" if fix else "--no-fix",
            "--unsafe-fixes" if unsafe else "--no-unsafe-fixes",
        )

    def format(self, check: bool = False) -> TaskResult:
        return self.run(
            "format",
            self.on,
            "--check" if check else "",
        )


@dataclass(frozen=True, kw_only=True)
class Git:
    name: str = "git"

    def amend(self) -> TaskResult:
        return ShellProgram(name=self.name).run(
            "commit",
            "--amend",
            "--no-edit",
            "-a",
        )
