from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from codex.infra.result import Reporter
from codex.infra.typer.device import TyperDevice


@dataclass(frozen=True)
class DefaultReporter:
    device: _Device = field(default_factory=TyperDevice)

    def silenced(self, *, when: bool) -> Reporter:
        if when:
            return DefaultReporter(SilentDevice())

        return self

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


class SilentDevice:  # pragma: no cover
    def with_green(self) -> _Device:
        return self

    def with_red(self) -> _Device:
        return self

    def with_white(self) -> _Device:
        return self

    def with_yellow(self) -> _Device:
        return self

    def echo(self, message: str) -> _Device:
        _ = message

        return self
