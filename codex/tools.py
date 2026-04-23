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


@dataclass(frozen=True, kw_only=True)
class Pip:
    def install(self, *packages: str) -> TaskResult:
        return RunPipInstall(args=packages).run()


@dataclass(frozen=True, kw_only=True)
class Poetry:
    on: Path

    def install(self) -> TaskResult:
        return RunPoetryInstallDependencies().run()

    def lock(self) -> TaskResult:
        return RunPoetryLock().run()

    def update(self) -> TaskResult:
        return RunPoetryUpdate().run()

    def lint(self) -> TaskResult:
        return RunPoetryCheck(on=self.on).run()


@dataclass(frozen=True, kw_only=True)
class Ruff:
    on: Path

    def lint(self, fix: bool, unsafe: bool) -> TaskResult:
        return RunRuffCheck(on=self.on, fix=fix, unsafe=unsafe).run()

    def format(self, check: bool = False) -> TaskResult:
        return RunRuffFormat(on=self.on, check=check).run()
