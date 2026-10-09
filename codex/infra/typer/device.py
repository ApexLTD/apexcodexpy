from __future__ import annotations

from dataclasses import dataclass
from textwrap import dedent
from typing import TYPE_CHECKING

import typer

if TYPE_CHECKING:
    from collections.abc import Callable


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
        _Message.parse(message).display(using=lambda m: typer.secho(m, fg=self.color))

        return self


@dataclass(frozen=True)
class _Message:
    raw: str

    @staticmethod
    def parse(raw: str) -> _Message | _NoMessage:
        message = dedent(raw).strip()

        return _Message(message + "\n") if message else _NoMessage()

    def display(self, using: Callable[[str], None]) -> None:
        using(self.raw)


@dataclass(frozen=True)
class _NoMessage:
    def display(self, using: Callable[[str], None]) -> None:
        _ = using
