from __future__ import annotations

import subprocess
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from itertools import chain
from pathlib import Path

from codex.tasks.result import TaskResult


@dataclass(frozen=True, kw_only=True)
class Program:
    def run(self, args: Iterable[str]) -> TaskResult:
        return TaskResult.parse(
            subprocess.run(
                list(chain.from_iterable(arg.split() for arg in args)),
                text=True,
                encoding="utf-8",
                capture_output=True,
            )
        )


@dataclass(frozen=True, kw_only=True)
class ShellProgram:
    name: str

    def run(self, args: Iterable[str]) -> TaskResult:
        return TaskResult.parse(
            subprocess.run(
                list(self._command_with(args)),
                text=True,
                encoding="utf-8",
                capture_output=True,
            )
        )

    def _command_with(self, args: Iterable[str]) -> Iterable[str]:
        yield self.name
        yield from chain.from_iterable(arg.split() for arg in args)


@dataclass(frozen=True, kw_only=True)
class RunPipInstall:
    args: Iterable[str] = ()
    upgrade: bool = True

    def __iter__(self) -> Iterator[str]:
        yield "python"
        yield "-m"
        yield "pip"
        yield "install"

        if self.upgrade:
            yield "--upgrade"

        yield from self.args


@dataclass(frozen=True, kw_only=True)
class RunPoetryInstallDependencies:
    def __iter__(self) -> Iterator[str]:
        yield "poetry"
        yield "install"


@dataclass(frozen=True, kw_only=True)
class RunRuffCheck:
    on: Path

    fix: bool = False
    unsafe: bool = False

    def __iter__(self) -> Iterator[str]:
        yield "check"
        yield str(self.on)

        if self.fix:
            yield "--fix"

        if self.unsafe:
            yield "--unsafe-fixes"


@dataclass(frozen=True, kw_only=True)
class RunRuffFormat:
    on: Path

    check: bool = False

    def __iter__(self) -> Iterator[str]:
        yield "ruff"
        yield "format"
        yield str(self.on)

        if self.check:
            yield "--check"


@dataclass(frozen=True, kw_only=True)
class RunMypy:
    on: Path

    def __iter__(self) -> Iterator[str]:
        yield "mypy"
        yield str(self.on)


@dataclass(frozen=True, kw_only=True)
class RunPoetryCheck:
    on: Path

    def __iter__(self) -> Iterator[str]:
        yield "poetry"
        yield "check"
        yield "--strict"
        yield f"--project={self.on}"


@dataclass(frozen=True, kw_only=True)
class RunPoetryLock:
    def __iter__(self) -> Iterator[str]:
        yield "poetry"
        yield "lock"


@dataclass(frozen=True, kw_only=True)
class RunPoetryUpdate:
    def __iter__(self) -> Iterator[str]:
        yield "poetry"
        yield "update"


@dataclass(frozen=True, kw_only=True)
class RunGitAmend:
    def __iter__(self) -> Iterator[str]:
        yield "git"
        yield "commit"
        yield "--amend"
        yield "--no-edit"
        yield "-a"
