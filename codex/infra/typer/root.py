from pathlib import Path

import typer

from codex.infra.reporters import DefaultReporter, SimpleReporter
from codex.infra.service import Codex, Git

cli = typer.Typer(no_args_is_help=True)


@cli.command(
    name="version",
    help="Show the codex version and exit.",
)
def _() -> None:
    Codex.version().report(using=SimpleReporter()).exit(using=typer.Exit)


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
) -> None:
    (
        Codex.target(Path(path))
        .sync()
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
        Codex.target(Path(path))
        .install()
        .report(using=DefaultReporter())
        .exit(using=typer.Exit)
    )


@cli.command(
    name="lock",
    help="Lock project dependencies.",
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
        Codex.target(Path(path))
        .lock()
        .report(using=DefaultReporter())
        .exit(using=typer.Exit)
    )


@cli.command(
    name="update",
    help="Update project dependencies.",
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
        Codex.target(Path(path))
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
        Codex.target(Path(path))
        .build(tag=tag)
        .report(using=DefaultReporter())
        .exit(using=typer.Exit)
    )


@cli.command(
    name="push",
    help="Tag and push a Docker image to GitHub Container Registry.",
)
def _(
    tag: str = typer.Option(
        ...,
        "--tag",
        "-t",
        help="Image tag, e.g. latest.",
    ),
    registry: str = typer.Option(
        "ghcr.io",
        "--registry",
        help="Container registry host.",
    ),
    organization: str = typer.Option(
        ...,
        "--organization",
        "-o",
        help="GHCR organization or namespace.",
    ),
    token: str = typer.Option(
        ...,
        "--token",
        help="GitHub token for registry login.",
    ),
    actor: str = typer.Option(
        ...,
        "--actor",
        help="GitHub username for registry login.",
    ),
    path: str = typer.Option(
        ".",
        "--path",
        "-p",
        help="Target directory.",
    ),
) -> None:
    (
        Codex.target(Path(path))
        .push(
            tag=tag,
            registry=registry,
            organization=organization,
            token=token,
            actor=actor,
        )
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
        Codex.target(Path(path))
        .ci(on=ci)
        .lint()
        .report(using=DefaultReporter().silenced(when=silent))
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
        Codex.target(Path(path))
        .fix(unsafe=unsafe)
        .report(using=DefaultReporter().silenced(when=silent))
        .exit(using=typer.Exit)
    )


@cli.command(
    name="amend",
    help="Amend the last git commit without changing the message.",
)
def _() -> None:
    Git().amend().report(using=DefaultReporter()).exit(using=typer.Exit)
