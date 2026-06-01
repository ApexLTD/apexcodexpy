from __future__ import annotations

from pathlib import Path

import typer

from codex.reporters import DefaultReporter
from codex.service import Codex, Git

cli = typer.Typer(no_args_is_help=True)


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
        .report(using=DefaultReporter())
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
        .report(using=DefaultReporter())
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
        .report(using=DefaultReporter())
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
        .report(using=DefaultReporter())
        .exit(using=typer.Exit)
    )


@cli.command(
    name="build",
    help="Build a Docker image.",
)
def _(
    tag: str = typer.Option(
        ...,
        "--tag",
        "-t",
        help="Target tag, e.g. my-project:latest",
    ),
    path: str = typer.Option(
        ".",
        "--path",
        "-p",
        help="Target directory.",
    ),
) -> None:
    (
        Codex(target=Path(path))
        .build(tag=tag)
        .report(using=DefaultReporter())
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
    ci: bool = typer.Option(
        False,
        "--ci",
        help="Run in CI mode.",
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
        .ci(on=ci)
        .lint()
        .silenced(when=silent)
        .report(using=DefaultReporter())
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
        .report(using=DefaultReporter())
        .exit(using=typer.Exit)
    )


@cli.command(
    name="amend",
    help="Amend the last git commit without changing the message.",
)
def _() -> None:
    Git().amend().report(using=DefaultReporter()).exit(using=typer.Exit)


test_cli = typer.Typer()
cli.add_typer(test_cli, name="test", short_help="Run tests.")


@test_cli.callback(invoke_without_command=True)
def _(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is not None:
        return

    run_unit_tests(path=".", ci=False)


@test_cli.command(
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
        Codex(target=Path(path))
        .ci(on=ci)
        .test()
        .report(using=DefaultReporter())
        .exit(using=typer.Exit)
    )


@test_cli.command(
    name="integration",
    help="Run integration tests.",
)
def _(
    ci: bool = typer.Option(
        False,
        "--ci",
        help="Run in CI mode.",
    ),
) -> None:
    (
        Codex(target=Path("."))
        .ci(on=ci)
        .test_integration()
        .report(using=DefaultReporter())
        .exit(using=typer.Exit)
    )


@test_cli.command(
    name="behaviour",
    help="Run behaviour tests.",
)
def _() -> None:
    (
        Codex(target=Path("."))
        .test_behaviour()
        .report(using=DefaultReporter())
        .exit(using=typer.Exit)
    )


if __name__ == "__main__":
    cli()
