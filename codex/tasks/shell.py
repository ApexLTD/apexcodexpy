from __future__ import annotations

import subprocess
from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from subprocess import CompletedProcess

from codex.tasks.result import TaskResult


class ShellTask(ABC):
    def run(self) -> TaskResult:
        return TaskResult.parse(self._execute())

    def _execute(self) -> CompletedProcess[str]:
        return subprocess.run(
            list(self._command),
            text=True,
            encoding="utf-8",
            capture_output=True,
        )

    @property
    @abstractmethod
    def _command(self) -> Iterable[str]:
        pass


@dataclass(frozen=True)
class RunPoetryInstallTools(ShellTask):
    @property
    def _command(self) -> Iterable[str]:
        yield "python"
        yield "-m"
        yield "pip"
        yield "install"
        yield "--upgrade"
        yield "pip"
        yield "poetry"


@dataclass(frozen=True)
class RunPoetryInstallDependencies(ShellTask):
    @property
    def _command(self) -> Iterable[str]:
        yield "poetry"
        yield "install"


@dataclass(frozen=True)
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


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class RunMypy(ShellTask):
    on: Path

    @property
    def _command(self) -> Iterable[str]:
        yield "mypy"
        yield str(self.on)


@dataclass(frozen=True)
class RunPoetryCheck(ShellTask):
    on: Path

    @property
    def _command(self) -> Iterable[str]:
        yield "poetry"
        yield "check"
        yield "--strict"
        yield f"--project={self.on}"


@dataclass(frozen=True)
class RunPoetryLock(ShellTask):
    @property
    def _command(self) -> Iterable[str]:
        yield "poetry"
        yield "lock"


@dataclass(frozen=True)
class RunPoetryUpdate(ShellTask):
    @property
    def _command(self) -> Iterable[str]:
        yield "poetry"
        yield "update"


@dataclass(frozen=True)
class RunGitAmend(ShellTask):
    @property
    def _command(self) -> Iterable[str]:
        yield "git"
        yield "commit"
        yield "--amend"
        yield "--no-edit"
        yield "-a"
