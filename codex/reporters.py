from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from codex.tasks import TaskResult
from codex.tasks.result import Reporter


@dataclass(frozen=True)
class DefaultReporter:
    device: _Device

    @classmethod
    def using(cls, device: _Device) -> DefaultReporter:
        return cls(device)

    def silenced(self) -> _Silenced:
        return _Silenced(self)

    def report(self, *results: TaskResult) -> int:
        return sum(self.report_one(result) for result in results)

    def report_one(self, result: TaskResult) -> int:
        if result:
            self.success_of(result.name)
        else:
            self.failure_of(result.name)

        self.out(result.stdout)
        self.error(result.stderr)

        return int(result)

    def success_of(self, name: str) -> None:
        self.device.with_green().echo(f"✅ {name} passed!")

    def failure_of(self, name: str) -> None:
        self.device.with_red().echo(f"❌ {name} failed!")

    def out(self, message: str) -> None:
        self.device.with_white().echo(message)

    def error(self, message: str) -> None:
        self.device.with_yellow().echo(message)


class _Device(Protocol):
    def with_green(self) -> _Device:
        pass

    def with_red(self) -> _Device:
        pass

    def with_white(self) -> _Device:
        pass

    def with_yellow(self) -> _Device:
        pass

    def echo(self, message: str) -> _Device:
        pass


@dataclass(frozen=True)
class _Silenced:
    reporter: Reporter

    def when(self, silenced: bool) -> Reporter:
        return self.reporter if not silenced else DefaultReporter.using(_NoDevice())


@dataclass(frozen=True)
class _NoDevice:
    def with_green(self) -> _Device:
        return self

    def with_red(self) -> _Device:
        return self

    def with_white(self) -> _Device:
        return self

    def with_yellow(self) -> _Device:
        return self

    def echo(self, message: str) -> _Device:
        _ = message  # suppresses IDE warning for unused argument

        return self
