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
from codex.tasks.shell import ShellRunner


@dataclass(frozen=True, kw_only=True)
class Pip:
    def install(self, *packages: str) -> TaskResult:
        return ShellRunner(args=(RunPipInstall(args=packages))).run()


@dataclass(frozen=True, kw_only=True)
class Poetry:
    on: Path

    def install(self) -> TaskResult:
        return ShellRunner(args=(RunPoetryInstallDependencies())).run()

    def lock(self) -> TaskResult:
        return ShellRunner(args=(RunPoetryLock())).run()

    def update(self) -> TaskResult:
        return ShellRunner(args=(RunPoetryUpdate())).run()

    def lint(self) -> TaskResult:
        return ShellRunner(args=(RunPoetryCheck(on=self.on))).run()


@dataclass(frozen=True, kw_only=True)
class Ruff:
    on: Path

    def lint(self, fix: bool, unsafe: bool) -> TaskResult:
        return ShellRunner(
            args=(RunRuffCheck(on=self.on, fix=fix, unsafe=unsafe))
        ).run()

    def format(self, check: bool = False) -> TaskResult:
        return ShellRunner(args=(RunRuffFormat(on=self.on, check=check))).run()
