from pathlib import Path

import typer

from codex.infra.reporters import DefaultReporter
from codex.infra.service import Codex

cli = typer.Typer()


@cli.command(
    name="unit",
    help="Run programmer tests.",
)
def run_unit_tests(
    path: str = typer.Option(
        ".",
        "--path",
        "-p",
        help="Target directory.",
    ),
    ci: bool = typer.Option(
        False,
        "--ci",
        help="Run in CI mode.",
    ),
) -> None:
    (
        Codex.target(Path(path))
        .ci(on=ci)
        .unit()
        .report(using=DefaultReporter())
        .exit(using=typer.Exit)
    )


@cli.command(
    name="integration",
    help="Run integration tests.",
)
def _(
    path: str = typer.Option(
        ".",
        "--path",
        "-p",
        help="Target directory.",
    ),
    ci: bool = typer.Option(
        False,
        "--ci",
        help="Run in CI mode.",
    ),
) -> None:
    (
        Codex.target(Path(path))
        .ci(on=ci)
        .integration()
        .report(using=DefaultReporter())
        .exit(using=typer.Exit)
    )


@cli.command(
    name="behaviour",
    help="Run behaviour tests.",
)
def _(
    path: str = typer.Option(
        ".",
        "--path",
        "-p",
        help="Target directory.",
    ),
    ci: bool = typer.Option(
        False,
        "--ci",
        help="Run in CI mode.",
    ),
) -> None:
    (
        Codex.target(Path(path))
        .ci(on=ci)
        .behaviour()
        .report(using=DefaultReporter())
        .exit(using=typer.Exit)
    )


@cli.callback(invoke_without_command=True)
def _(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is not None:
        return

    run_unit_tests(path="", ci=False)
