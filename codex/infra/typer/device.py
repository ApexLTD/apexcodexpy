from __future__ import annotations

from dataclasses import dataclass

import typer


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
