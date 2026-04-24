from __future__ import annotations

import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from typing import Any

from codex.tasks import TaskResult


@dataclass(frozen=True, kw_only=True)
class ShellProgram:
    name: str

    def run(self, *args: Any, **kwargs: Any) -> TaskResult:
        return TaskResult.parse(
            subprocess.run(
                list(self._command_with([*args, *kwargs.values()])),
                text=True,
                encoding="utf-8",
                capture_output=True,
            )
        )

    def _command_with(self, args: Iterable[str]) -> Iterable[str]:
        yield from self.name.split()
        yield from chain.from_iterable(str(arg).split() for arg in args)


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
class MyPy:
    on: Path

    name: str = "mypy"

    def run(self) -> TaskResult:
        return ShellProgram(name=self.name).run(on=self.on)


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
