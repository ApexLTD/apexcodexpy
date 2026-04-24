from __future__ import annotations

import subprocess
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from codex.tasks import TaskResult


@dataclass(frozen=True)
class Program:
    name: str

    _arguments: list[str] = field(init=False, default_factory=list)

    def with_a(self, **kwargs: Any) -> Program:
        return self.and_a(**kwargs)

    def and_a(self, **kwargs: Any) -> Program:
        assert len(kwargs) == 1, "with_a/and_a supports one argument at a time."

        name, value = kwargs.popitem()

        return self.append(f"--{name}={value}")

    def flag(self, **kwargs: bool | None) -> Program:
        for name, value in kwargs.items():
            flag = self.dashify(name)

            if value is not None:
                self.append(f"--{flag}" if value else f"--no-{flag}")

        return self

    def dashify(self, name: str) -> str:
        return name.replace("_", "-")

    def extend(self, arguments: Iterable[Any]) -> Program:
        for argument in arguments:
            self.append(argument)

        return self

    def append(self, argument: Any) -> Program:
        self._arguments.extend(str(argument).split())

        return self

    def run(self) -> TaskResult:
        return TaskResult.parse(
            subprocess.run(
                str(self).split(),
                text=True,
                encoding="utf-8",
                capture_output=True,
            )
        )

    def __str__(self) -> str:
        return " ".join(self._command())

    def _command(self) -> Iterable[str]:
        yield from self.name.split()

        for argument in self._arguments:
            yield from str(argument).split()


@dataclass(frozen=True, kw_only=True)
class Pip:
    name: str = "pip"

    def install(self, *packages: str) -> TaskResult:
        return (
            Program(self.name)
            .append("install")
            .flag(upgrade=True)
            .extend(packages)
            .run()
        )


@dataclass(frozen=True, kw_only=True)
class Poetry:
    on: Path

    name: str = "poetry"

    def install(self) -> TaskResult:
        return Program(self.name).append("install").run()

    def lock(self) -> TaskResult:
        return Program(self.name).append("lock").run()

    def update(self) -> TaskResult:
        return Program(self.name).append("update").run()

    def lint(self) -> TaskResult:
        return (
            Program(self.name)
            .append("check")
            .with_a(project=self.on)
            .flag(strict=True)
            .run()
        )


@dataclass(frozen=True, kw_only=True)
class Ruff:
    on: Path

    name: str = "ruff"

    def lint(self, fix: bool = True, unsafe: bool = False) -> TaskResult:
        return (
            Program(self.name)
            .append("check")
            .append(self.on)
            .flag(fix=fix)
            .flag(unsafe_fixes=unsafe)
            .run()
        )

    def format(self, check: bool | None = None) -> TaskResult:
        return (
            Program(self.name).append("format").append(self.on).flag(check=check).run()
        )


@dataclass(frozen=True, kw_only=True)
class MyPy:
    on: Path

    name: str = "mypy"

    def run(self) -> TaskResult:
        return Program(self.name).append(self.on).run()


@dataclass(frozen=True, kw_only=True)
class Git:
    name: str = "git"

    def amend(self) -> TaskResult:
        return (
            Program(self.name)
            .append("commit")
            .flag(all=True)
            .flag(amend=True)
            .flag(edit=False)
            .run()
        )
