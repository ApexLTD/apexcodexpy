from __future__ import annotations

import copy
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

import tomlkit

from codex.infra.result import ProgramResult

if TYPE_CHECKING:
    from collections.abc import Mapping

    from codex.infra.program import Executable


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
                "RUF",
                "FURB",
                "PERF",
                "LOG",
                "PIE",
                "SLF",
                "DTZ",
                "PTH",
                "TRY",
                "PL",
                "TCH",
            ],
            "mccabe": {
                "max-complexity": 10,
            },
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
    _result: ProgramResult = field(init=False, default=ProgramResult(name="PyProject"))

    NAME = "pyproject.toml"

    def sync(self, target: Path) -> Executable:
        return self._sync(self.toml_on(target))

    def _sync(self, pyproject: Path) -> Executable:
        if not pyproject.exists():
            return self._result.fail(message=f"{self.NAME} not found.")

        current = Tomler.read(pyproject).dumps()
        latest = Tomler.read(pyproject).update_with(STANDARDS).dumps()

        if current == latest:
            return self._result.no_changes()

        pyproject.write_text(latest, encoding="utf-8", newline="\n")

        return self._result.success(message=f"{self.NAME} synchronized successfully.\n")

    def toml_on(self, path: Path) -> Path:
        return path / self.NAME

    @staticmethod
    def latest() -> Tomler:
        return Tomler.read(Path("pyproject.toml")).update_with(STANDARDS)


@dataclass(frozen=True)
class Tomler:
    document: Mapping[str, Any]

    @classmethod
    def read(cls, path: Path) -> Tomler:
        return cls(tomlkit.parse(path.read_text(encoding="utf-8")))

    def dumps(self) -> str:
        return tomlkit.dumps(self.document)

    def update_with(self, source: Mapping[str, Any]) -> Tomler:
        return Tomler(deep_merge(source, self.document))

    def hashed(self) -> str:
        return hashlib.sha256(self.dumps().encode()).hexdigest()


def deep_merge(
    source: Mapping[str, Any],
    destination: Mapping[str, Any],
) -> Mapping[str, Any]:
    """
    Recursively merges two TOML documents or mappings,
    updating the values of the destination with those from the source.
    The merge is performed deeply to handle nested mappings, ensuring that
    both simple and complex TOML structures are merged effectively.

    This function ensures that TOML-compliant data structures are preserved during the
    merge process, including the creation of properly formatted TOML arrays and tables.

    :param source: The source mapping to be merged into the destination.
    :type source: Mapping[str, Any]
    :param destination: The destination mapping.
    :type destination: Mapping[str, Any]
    :return: A TOMLDocument representing the merged result.
    :rtype: Mapping[str, Any]
    """
    result = {**destination}

    for key, value in source.items():
        match (result.get(key), value):
            case (dict(destination_value), dict(source_value)):
                # Both exist and are dicts -> recursively merge
                result[key] = deep_merge(source_value, destination_value)
            case (_, dict(source_value)):
                # Only source is a dict -> convert to TOML table
                result[key] = deep_merge(source_value, {})
            case (_, list(src_list)):
                # Formatted TOML array
                new_array = tomlkit.array()
                new_array.extend(copy.deepcopy(src_list))
                new_array.multiline(True)
                result[key] = new_array
            case _:
                result[key] = copy.deepcopy(value)

    return result
