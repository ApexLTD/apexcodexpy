from __future__ import annotations

import subprocess
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field, replace
from typing import Any, Protocol

from codex.infra.result import ComboResult, ProgramResult, TaskResult


@dataclass(frozen=True)
class Program:
    command: Command

    name: str = "unknown"

    def execute(self) -> ProgramResult:
        return replace(
            ProgramResult.parse(
                subprocess.run(
                    list(self.command),
                    text=True,
                    encoding="utf-8",
                    capture_output=True,
                )
            ),
            name=self.name.capitalize(),
        )


@dataclass(frozen=True)
class Command:
    name: str

    _arguments: list[str] = field(init=False, default_factory=list)

    def with_a(self, **kwargs: Any) -> Command:
        return self.and_a(**kwargs)

    def and_a(self, **kwargs: Any) -> Command:
        assert len(kwargs) == 1, "with_a/and_a supports one argument at a time."

        name, value = kwargs.popitem()

        return self.append(f"--{name}={value}")

    def flag(self, **kwargs: bool | None) -> Command:
        for name, value in kwargs.items():
            flag = self.dashify(name)

            if value is not None:
                self.append(f"--{flag}" if value else f"--no-{flag}")

        return self

    def dashify(self, name: str) -> str:
        return name.replace("_", "-")

    def extend(self, arguments: Iterable[Any]) -> Command:
        for argument in arguments:
            self.append(argument)

        return self

    def append(self, argument: Any) -> Command:
        if argument is not None:
            self._arguments.extend(str(argument).split())

        return self

    def __str__(self) -> str:
        return " ".join(self)

    def __iter__(self) -> Iterator[str]:
        yield from self.name.split()

        for argument in self._arguments:
            yield from str(argument).split()


@dataclass(frozen=True)
class FinishedProgram:
    result: ProgramResult

    def execute(self) -> ProgramResult:
        return self.result


class Executable(Protocol):
    def execute(self) -> TaskResult:
        pass


@dataclass(frozen=True)
class MultiProgram:
    sub_programs: list[Executable] = field(default_factory=list)

    def attach(self, program: Executable) -> MultiProgram:
        self.sub_programs.append(program)

        return self

    def execute(self) -> TaskResult:
        return ComboResult([program.execute() for program in self.sub_programs])
