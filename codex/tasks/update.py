from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import tomlkit

from codex.tasks import TaskResult


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
class Toml:
    dry_run: bool = False

    PYPROJECT_TOML = "pyproject.toml"

    def toml_on(self, path: Path) -> Path:
        return path / self.PYPROJECT_TOML

    def sync(self, target: Path) -> TaskResult:
        return self._sync(target).named("sync")

    def _sync(self, target: Path) -> TaskResult:
        if not self.toml_on(target).exists():
            return TaskResult.fail(stderr=f"{self.PYPROJECT_TOML} not found.")

        document = tomlkit.parse(self.toml_on(target).read_text(encoding="utf-8"))

        # Create a copy for comparison if dry-run
        original = tomlkit.dumps(document)
        deep_merge(STANDARDS, document)
        modified = tomlkit.dumps(document)

        if original == modified:
            return TaskResult.success(stdout="Configuration is already up to date.")

        if self.dry_run:
            return TaskResult.success(stdout=f"Changes would be applied:\n{modified}")

        self.toml_on(target).write_text(modified, encoding="utf-8", newline="\n")

        return TaskResult.success(stdout="Configuration synchronized successfully.")


def deep_merge(source: dict[str, Any], destination: dict[str, Any]) -> None:
    """Recursively merges the source into destination with TOML formatting."""
    for key, value in source.items():
        match value:
            case dict():
                # Create a table if the key doesn't exist
                if key not in destination:
                    destination[key] = tomlkit.table()
                deep_merge(value, destination[key])
            case list():
                # Create a multiline array
                new_array = tomlkit.array()
                for item in value:
                    new_array.append(item)
                new_array.multiline(True)
                destination[key] = new_array
            case _:
                destination[key] = value
