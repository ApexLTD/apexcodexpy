from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import typer

from codex.reporters import DefaultReporter
from codex.service import PyCodex

cli = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
)


@cli.command(
    name="sync",
    help="Inject standards into pyproject TOML file.",
)
def _(
    path: str = typer.Option(
        ".",
        "--path",
        "-p",
        help="Target directory.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show changes without applying them.",
    ),
) -> None:
    raise typer.Exit(
        PyCodex(
            target=Path(path),
            reporter=DefaultReporter.using(TyperDevice()),
        ).sync(dry_run=dry_run)
    )


@cli.command(
    name="lock",
    help="Run poetry lock.",
)
def _() -> None:
    raise typer.Exit(
        PyCodex(
            target=Path("."),
            reporter=DefaultReporter.using(TyperDevice()),
        ).lock()
    )


@cli.command(
    name="update",
    help="Run poetry update.",
)
def _() -> None:
    raise typer.Exit(
        PyCodex(
            target=Path("."),
            reporter=DefaultReporter.using(TyperDevice()),
        ).update()
    )


@cli.command(
    name="lint",
    help="Run linting (Ruff) and type checking (MyPy).",
)
def _(
    path: str = typer.Option(
        ".",
        "--path",
        "-p",
        help="Target directory.",
    ),
    silent: bool = typer.Option(
        False,
        "--silent",
        "-s",
        help="Suppress output.",
    ),
) -> None:
    raise typer.Exit(
        PyCodex(
            target=Path(path),
            reporter=DefaultReporter.using(TyperDevice()).silenced().when(silent),
        ).lint()
    )


@cli.command(
    name="fix",
    help="Automatically fix Ruff linting errors.",
)
def _(
    path: str = typer.Option(
        ".",
        "--path",
        "-p",
        help="Target directory.",
    ),
    silent: bool = typer.Option(
        False,
        "--silent",
        "-s",
        help="Suppress output.",
    ),
    unsafe: bool = typer.Option(
        False,
        "--unsafe",
        help="Run unsafe Ruff fixes.",
    ),
) -> None:
    raise typer.Exit(
        PyCodex(
            target=Path(path),
            reporter=DefaultReporter.using(TyperDevice()).silenced().when(silent),
        ).fix(unsafe=unsafe)
    )


@cli.command(
    name="amend",
    help="Amend the last git commit without changing the message.",
)
def _() -> None:
    raise typer.Exit(
        PyCodex(
            target=Path("."),
            reporter=DefaultReporter.using(TyperDevice()),
        ).amend()
    )


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


if __name__ == "__main__":
    cli()
