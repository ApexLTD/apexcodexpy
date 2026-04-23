from __future__ import annotations

import subprocess
from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from typing import Any

from codex.tasks.result import TaskResult


@dataclass(frozen=True, kw_only=True)
class ShellRunner:
    args: Iterable[Any]

    def run(self) -> TaskResult:
        raw_result = subprocess.run(
            self._command,
            text=True,
            encoding="utf-8",
            capture_output=True,
        )

        return TaskResult.parse(raw_result)

    @property
    def _command(self) -> list[str]:
        return list(chain.from_iterable(str(arg).split() for arg in self.args))


@dataclass(frozen=True, kw_only=True)
class ShellTask(ABC):
    args: Iterable[str] = ()

    def run(self) -> TaskResult:
        return ShellRunner(args=self._command).run()

    @property
    @abstractmethod
    def _command(self) -> Iterable[str]:
        pass


@dataclass(frozen=True, kw_only=True)
class RunPipInstall(ShellTask):
    upgrade: bool = True

    @property
    def _command(self) -> Iterable[str]:
        yield "python"
        yield "-m"
        yield "pip"
        yield "install"

        if self.upgrade:
            yield "--upgrade"

        yield from self.args


@dataclass(frozen=True, kw_only=True)
class RunPoetryInstallDependencies(ShellTask):
    @property
    def _command(self) -> Iterable[str]:
        yield "poetry"
        yield "install"


@dataclass(frozen=True, kw_only=True)
class RunRuffCheck(ShellTask):
    on: Path

    fix: bool = False
    unsafe: bool = False

    @property
    def _command(self) -> Iterable[str]:
        yield "ruff"
        yield "check"
        yield str(self.on)

        if self.fix:
            yield "--fix"

        if self.unsafe:
            yield "--unsafe-fixes"


@dataclass(frozen=True, kw_only=True)
class RunRuffFormat(ShellTask):
    on: Path

    check: bool = False

    @property
    def _command(self) -> Iterable[str]:
        yield "ruff"
        yield "format"
        yield str(self.on)

        if self.check:
            yield "--check"


@dataclass(frozen=True, kw_only=True)
class RunMypy(ShellTask):
    on: Path

    @property
    def _command(self) -> Iterable[str]:
        yield "mypy"
        yield str(self.on)


@dataclass(frozen=True, kw_only=True)
class RunPoetryCheck(ShellTask):
    on: Path

    @property
    def _command(self) -> Iterable[str]:
        yield "poetry"
        yield "check"
        yield "--strict"
        yield f"--project={self.on}"


@dataclass(frozen=True, kw_only=True)
class RunPoetryLock(ShellTask):
    @property
    def _command(self) -> Iterable[str]:
        yield "poetry"
        yield "lock"


@dataclass(frozen=True, kw_only=True)
class RunPoetryUpdate(ShellTask):
    @property
    def _command(self) -> Iterable[str]:
        yield "poetry"
        yield "update"


@dataclass(frozen=True, kw_only=True)
class RunGitAmend(ShellTask):
    @property
    def _command(self) -> Iterable[str]:
        yield "git"
        yield "commit"
        yield "--amend"
        yield "--no-edit"
        yield "-a"
