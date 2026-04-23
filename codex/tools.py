from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from codex.tasks import (
    RunPipInstall,
    RunPoetryCheck,
    RunPoetryInstallDependencies,
    RunPoetryLock,
    RunPoetryUpdate,
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
