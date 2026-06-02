from __future__ import annotations

from dataclasses import dataclass, field
from subprocess import CompletedProcess
from typing import Any, Protocol


class TaskResult(Protocol):
    def report(self, using: Reporter) -> TaskResult:
        pass

    def exit(self, using: type[Exception] | None = None) -> int:
        pass


@dataclass(frozen=True)
class ComboResult:
    results: list[TaskResult] = field(default_factory=list)

    @property
    def _exit_code(self) -> int:
        return sum(result.exit() for result in self.results)

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
    name: str

    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0

    def __int__(self) -> int:
        return self.exit_code

    def __bool__(self) -> bool:
        return self.exit_code == 0

    def parse(self, result: CompletedProcess[Any]) -> ProgramResult:
        return ProgramResult(
            name=self.name,
            stdout=result.stdout or "",
            stderr=result.stderr or "",
            exit_code=result.returncode,
        )

    def success(self, *, message: str = "") -> ProgramResult:
        return ProgramResult(
            name=self.name,
            stdout=message or self.stdout,
            stderr=self.stderr,
            exit_code=0,
        )

    def fail(self, *, message: str = "") -> ProgramResult:
        return ProgramResult(
            name=self.name,
            stdout=self.stdout,
            stderr=message or self.stderr,
            exit_code=1,
        )

    def execute(self) -> ProgramResult:
        return self

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
