from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class DefaultReporter:
    device: _Device

    @classmethod
    def using(cls, device: _Device) -> DefaultReporter:
        return cls(device)

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
