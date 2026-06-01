from __future__ import annotations

import subprocess
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from codex.infra.tasks import ProgramResult


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
        if argument is not None:
            self._arguments.extend(str(argument).split())

        return self

    def run(self) -> ProgramResult:
        return ProgramResult.parse(
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
    def install(self, *packages: str) -> ProgramResult:
        return (
            Program("python -m pip")
            .append("install")
            .flag(upgrade=True)
            .extend(packages)
            .run()
        )


@dataclass(frozen=True, kw_only=True)
class Poetry:
    def install(self) -> ProgramResult:
        return Program("poetry install").run()

    def lock(self) -> ProgramResult:
        return Program("poetry lock").run()

    def update(self) -> ProgramResult:
        return Program("poetry update").run()

    def lint(self, target: Path) -> ProgramResult:
        return Program("poetry check").with_a(project=target).flag(strict=True).run()

    def run(self, program: Program) -> Program:
        return Program(f"poetry run {program}")

    def export(self, target: Path) -> ProgramResult:
        return (
            Program("poetry export")
            .flag(without_hashes=True)
            .with_a(output="requirements.txt")
            .with_a(directory=target)
            .run()
        )


@dataclass(frozen=True, kw_only=True)
class Ruff:
    on: Path

    def lint(self) -> Program:
        return Program("ruff check").append(self.on)

    def format(self) -> Program:
        return Program("ruff format").append(self.on)


@dataclass(frozen=True, kw_only=True)
class MyPy:
    on: Path

    def check(self) -> Program:
        return Program("mypy").append(self.on)
