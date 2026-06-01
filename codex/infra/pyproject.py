from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import tomlkit

from codex.infra.program import Executable, FinishedProgram
from codex.infra.result import ProgramResult


def _mypy_config() -> dict[str, Any]:
    return {
        "strict": True,
        "ignore_missing_imports": True,
        "show_error_codes": True,
        "pretty": True,
    }


def _ruff_config() -> dict[str, Any]:
    return {
        "lint": {
            "select": [
                "A",
                "ARG",
                "B",
                "C4",
                "PT",
                "RSE",
                "RET",
                "SIM",
                "T20",
                "E",
                "W",
                "F",
                "I",
                "N",
                "UP",
            ],
            "mccabe": {"max-complexity": 10},
        }
    }


def _coverage_config() -> dict[str, Any]:
    return {
        "run": {
            "branch": True,
        },
        "report": {
            "skip_empty": True,
            "skip_covered": True,
            "show_missing": True,
        },
    }


STANDARDS = {
    "tool": {
        "mypy": _mypy_config(),
        "ruff": _ruff_config(),
        "coverage": _coverage_config(),
    }
}


@dataclass(frozen=True)
class PyProjectToml:
    dry_run: bool = False

    NAME = "pyproject.toml"

    def sync(self, target: Path) -> Executable:
        return self._sync(self.toml_on(target))

    def _sync(self, pyproject: Path) -> Executable:
        if not pyproject.exists():
            return FinishedProgram(ProgramResult.fail(stderr=f"{self.NAME} not found."))

        document = tomlkit.parse(pyproject.read_text(encoding="utf-8"))

        # Create a copy for comparison if dry-run
        original = tomlkit.dumps(document)
        deep_merge(STANDARDS, document)
        modified = tomlkit.dumps(document)

        if original == modified:
            return FinishedProgram(
                ProgramResult.success(stdout="Configuration is already up to date.")
            )

        if self.dry_run:
            return FinishedProgram(
                ProgramResult.success(stdout=f"Changes would be applied:\n{modified}")
            )

        pyproject.write_text(modified, encoding="utf-8", newline="\n")

        return FinishedProgram(
            ProgramResult.success(stdout="Configuration synchronized successfully.")
        )

    def toml_on(self, path: Path) -> Path:
        return path / self.NAME


def deep_merge(source: dict[str, Any], destination: dict[str, Any]) -> None:
    """Recursively merges the source into destination with TOML formatting."""
    for key, value in source.items():
        match value:
            case dict():
                if key not in destination:
                    destination[key] = tomlkit.table()
                deep_merge(value, destination[key])
            case list():
                new_array = tomlkit.array()
                new_array.extend(value)
                new_array.multiline(True)
                destination[key] = new_array
            case _:
                destination[key] = value
