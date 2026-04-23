from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from codex.tasks import (
    PipInstall,
    PoetryCheck,
    PoetryInstall,
    PoetryLock,
    PoetryUpdate,
    RuffCheck,
    RuffFormat,
    TaskResult,
)
from codex.tasks.program import ShellProgram


@dataclass(frozen=True, kw_only=True)
class Pip(ShellProgram):
    name: str = "pip"

    def install(self, *packages: str) -> TaskResult:
        return self.run(PipInstall(args=packages))


@dataclass(frozen=True, kw_only=True)
class Poetry(ShellProgram):
    on: Path

    name: str = "poetry"

    def install(self) -> TaskResult:
        return self.run(PoetryInstall())

    def lock(self) -> TaskResult:
        return self.run(PoetryLock())

    def update(self) -> TaskResult:
        return self.run(PoetryUpdate())

    def lint(self) -> TaskResult:
        return self.run(PoetryCheck(on=self.on))


@dataclass(frozen=True, kw_only=True)
class Ruff(ShellProgram):
    on: Path

    name: str = "ruff"

    def lint(self, fix: bool = True, unsafe: bool = False) -> TaskResult:
        return self.run(RuffCheck(on=self.on, fix=fix, unsafe=unsafe))

    def format(self, check: bool = False) -> TaskResult:
        return self.run(RuffFormat(on=self.on, check=check))
