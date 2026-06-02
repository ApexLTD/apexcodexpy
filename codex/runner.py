from codex.infra.typer import root_cli, testing_cli


def cli() -> None:
    root_cli.add_typer(testing_cli, name="test", short_help="Run tests.")

    root_cli()
