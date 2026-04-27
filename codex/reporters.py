from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import typer


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


@dataclass(frozen=True)
class TyperDevice:
    color: str = typer.colors.RESET

    def with_green(self) -> TyperDevice:
        return TyperDevice(typer.colors.GREEN)

    def with_red(self) -> TyperDevice:
        return TyperDevice(typer.colors.RED)

    def with_white(self) -> TyperDevice:
        return TyperDevice(typer.colors.WHITE)

    def with_yellow(self) -> TyperDevice:
        return TyperDevice(typer.colors.YELLOW)

    def echo(self, message: str) -> TyperDevice:
        if message.strip():
            typer.secho(message, fg=self.color)

        return self
