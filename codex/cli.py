from codex.root import cli
from codex.testing import cli as testing_cli

cli.add_typer(testing_cli, name="test", short_help="Run tests.")


if __name__ == "__main__":
    cli()
