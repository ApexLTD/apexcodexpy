from __future__ import annotations

from dataclasses import dataclass, field
from subprocess import CompletedProcess
from typing import Any, Protocol


class TaskResult(Protocol):
    def named(self, name: str) -> TaskResult:
        pass

    def report(self, using: Reporter) -> TaskResult:
        pass

    def exit(self, using: type[Exception] | None = None) -> int:
        pass


@dataclass(frozen=True)
class ComboResult:
    results: list[TaskResult] = field(default_factory=list)

    def named(self, _: str) -> ComboResult:
        return self

    @property
    def _exit_code(self) -> int:
        return sum(result.exit() for result in self.results)

    def attach(self, *args: TaskResult, **kwargs: TaskResult) -> ComboResult:
        for name, result in kwargs.items():
            self.results.append(result.named(name))

        for result in args:
            self.results.append(result)

        return self

    def report(self, using: Reporter) -> ComboResult:
        for result in self.results:
            result.report(using)

        return self

    def exit(self, using: type[Exception] | None = None) -> int:
        if using is None:
            return self._exit_code

        raise using(self._exit_code)


@dataclass(frozen=True, kw_only=True)
class ProgramResult:
    stdout: str
    stderr: str
    exit_code: int

    name: str = "Unknown"

    def named(self, name: str) -> ProgramResult:
        return ProgramResult(
            stdout=self.stdout,
            stderr=self.stderr,
            exit_code=self.exit_code,
            name=name.capitalize(),
        )

    def __int__(self) -> int:
        return self.exit_code

    def __bool__(self) -> bool:
        return self.exit_code == 0

    @classmethod
    def parse(cls, result: CompletedProcess[Any]) -> ProgramResult:
        return cls(
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.returncode,
        )

    @classmethod
    def success(cls, *, stdout: str = "", stderr: str = "") -> ProgramResult:
        return cls(stdout=stdout, stderr=stderr, exit_code=0)

    @classmethod
    def fail(cls, *, stdout: str = "", stderr: str = "") -> ProgramResult:
        return cls(stdout=stdout, stderr=stderr, exit_code=1)

    def report(self, using: Reporter) -> ProgramResult:
        if self.exit_code == 0:
            using.success_of(self.name)
        else:
            using.failure_of(self.name)

        using.out(self.stdout)
        using.error(self.stderr)

        return self

    def exit(self, using: type[Exception] | None = None) -> int:
        if using is None:
            return self.exit_code

        raise using(self.exit_code)


class Reporter(Protocol):
    def success_of(self, name: str) -> None:
        pass

    def failure_of(self, name: str) -> None:
        pass

    def out(self, message: str) -> None:
        pass

    def error(self, message: str) -> None:
        pass
