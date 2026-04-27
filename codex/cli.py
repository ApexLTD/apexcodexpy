from __future__ import annotations

from pathlib import Path

import typer

from codex.reporters import DefaultReporter, TyperDevice
from codex.service import Codex, Git

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
    (
        Codex(target=Path(path))
        .sync(dry_run=dry_run)
        .report(using=DefaultReporter.using(TyperDevice()))
        .exit(using=typer.Exit)
    )


@cli.command(
    name="install",
    help="Install project tools and dependencies.",
)
def _(
    path: str = typer.Option(
        ".",
        "--path",
        "-p",
        help="Target directory.",
    ),
) -> None:
    (
        Codex(target=Path(path))
        .install()
        .report(using=DefaultReporter.using(TyperDevice()))
        .exit(using=typer.Exit)
    )


@cli.command(
    name="lock",
    help="Lock project dependencies.",
)
def _() -> None:
    (
        Codex(target=Path("."))
        .lock()
        .report(using=DefaultReporter.using(TyperDevice()))
        .exit(using=typer.Exit)
    )


@cli.command(
    name="update",
    help="Update project dependencies.",
)
def _() -> None:
    (
        Codex(target=Path("."))
        .update()
        .report(using=DefaultReporter.using(TyperDevice()))
        .exit(using=typer.Exit)
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
    (
        Codex(target=Path(path))
        .lint()
        .silenced(when=silent)
        .report(using=DefaultReporter.using(TyperDevice()))
        .exit(using=typer.Exit)
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
    (
        Codex(target=Path(path))
        .fix(unsafe=unsafe)
        .silenced(when=silent)
        .report(using=DefaultReporter.using(TyperDevice()))
        .exit(using=typer.Exit)
    )


@cli.command(
    name="amend",
    help="Amend the last git commit without changing the message.",
)
def _() -> None:
    (
        Git()
        .amend()
        .report(using=DefaultReporter.using(TyperDevice()))
        .exit(using=typer.Exit)
    )


if __name__ == "__main__":
    cli()
