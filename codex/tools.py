from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from codex.tasks import (
    RunPipInstall,
    RunPoetryCheck,
    RunPoetryInstallDependencies,
    RunPoetryLock,
    RunPoetryUpdate,
    RunRuffCheck,
    RunRuffFormat,
    TaskResult,
)
from codex.tasks.program import Program


@dataclass(frozen=True, kw_only=True)
class Pip:
    def install(self, *packages: str) -> TaskResult:
        return Program().run(RunPipInstall(args=packages))


@dataclass(frozen=True, kw_only=True)
class Poetry:
    on: Path

    def install(self) -> TaskResult:
        return Program().run(RunPoetryInstallDependencies())

    def lock(self) -> TaskResult:
        return Program().run(RunPoetryLock())

    def update(self) -> TaskResult:
        return Program().run(RunPoetryUpdate())

    def lint(self) -> TaskResult:
        return Program().run(RunPoetryCheck(on=self.on))


@dataclass(frozen=True, kw_only=True)
class Ruff:
    on: Path

    def lint(self, fix: bool = True, unsafe: bool = False) -> TaskResult:
        return Program().run(RunRuffCheck(on=self.on, fix=fix, unsafe=unsafe))

    def format(self, check: bool = False) -> TaskResult:
        return Program().run(RunRuffFormat(on=self.on, check=check))
