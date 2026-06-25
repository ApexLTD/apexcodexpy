from __future__ import annotations

import subprocess
from collections.abc import Iterable, Iterator, MutableSequence
from dataclasses import dataclass, field, replace
from typing import Any, Protocol

from codex.infra.result import ComboResult, ProgramResult, TaskResult


@dataclass(frozen=True)
class Program:
    command: Command

    name: str = "unknown"

    def execute(self) -> ProgramResult:
        return replace(
            ProgramResult(name=self.name.capitalize()).parse(
                subprocess.run(
                    list(self.command),
                    text=True,
                    encoding="utf-8",
                    capture_output=True,
                )
            ),
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
        match argument:
            case None:
                pass
            case str(text) if not text.startswith("'"):
                self._arguments.extend(argument.split())
            case _:
                self._arguments.append(str(argument))

        return self

    def __str__(self) -> str:
        return " ".join(self)

    def __iter__(self) -> Iterator[str]:
        yield from self.name.split()
        yield from self._arguments


class Executable(Protocol):
    def execute(self) -> TaskResult:
        pass


@dataclass(frozen=True)
class MultiProgram:
    sub_programs: MutableSequence[Executable] = field(default_factory=list)

    def attach(self, program: Executable, when: bool = True) -> MultiProgram:
        if when:
            self.sub_programs.append(program)

        return self

    def execute(self) -> TaskResult:
        return ComboResult([program.execute() for program in self.sub_programs])


@dataclass(frozen=True)
class BoundedProgram:
    before: MultiProgram = field(init=False, default_factory=MultiProgram)
    action: MultiProgram = field(init=False, default_factory=MultiProgram)
    after: MultiProgram = field(init=False, default_factory=MultiProgram)

    def setup(self, program: Executable) -> BoundedProgram:
        self.before.attach(program)

        return self

    def teardown(self, program: Executable) -> BoundedProgram:
        self.after.attach(program)

        return self

    def attach(self, program: Executable) -> BoundedProgram:
        self.action.attach(program)

        return self

    def execute(self) -> TaskResult:
        return (
            MultiProgram()
            .attach(self.before)
            .attach(self.action)
            .attach(self.after)
            .execute()
        )
