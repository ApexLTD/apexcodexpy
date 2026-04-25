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
    def install(self, *packages: str) -> TaskResult:
        return (
            Program("pip install")
            .flag(upgrade=True)
            .extend(packages)
            .run()
            .named("tools")
        )


@dataclass(frozen=True, kw_only=True)
class Poetry:
    def install(self) -> TaskResult:
        return Program("poetry install").run().named("dependencies")

    def lock(self) -> TaskResult:
        return Program("poetry lock").run().named("lock")

    def update(self) -> TaskResult:
        return Program("poetry update").run().named("update")

    def lint(self, target: Path) -> TaskResult:
        return (
            Program("poetry check")
            .with_a(project=target)
            .flag(strict=True)
            .run()
            .named("poetry")
        )

    def run(self, **program: Program) -> TaskResult:
        assert len(program) == 1, "run supports one program at a time."

        name, command = program.popitem()

        return Program(f"poetry run {command}").run().named(name)


@dataclass(frozen=True, kw_only=True)
class Ruff:
    def lint(
        self,
        target: Path,
        *,
        fix: bool = False,
        unsafe: bool = False,
    ) -> Program:
        return (
            Program("ruff check").append(target).flag(fix=fix).flag(unsafe_fixes=unsafe)
        )

    def format(
        self,
        target: Path,
        *,
        check: bool | None = None,
    ) -> Program:
        return Program("ruff format").append(target).flag(check=check)


@dataclass(frozen=True, kw_only=True)
class MyPy:
    def check(self, target: Path) -> Program:
        return Program("mypy").append(target)
