from __future__ import annotations

import copy
import hashlib
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import tomlkit

from codex.infra.result import ProgramResult

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

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

    def verify(self, target: Path) -> Executable:
        return self._verify(self.toml_on(target))

    def _verify(self, pyproject: Path) -> ProgramResult:
        if not pyproject.exists():
            return self._result.fail(message=f"{self.NAME} not found.")

        current = Tomler.read(pyproject)
        latest = current.update_with(STANDARDS)

        if current == latest:
            return self._result.no_changes()

        return self._result.fail(
            message=f"""
                {self.NAME} is outdated!
                Run `codex sync` to bring configuration up to date.
            """
        )


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
    Recursively merges two mappings, taking the source and merging it into
    the destination. Performs a deep merge such that nested dictionaries or
    arrays are combined intelligently.

    The function identifies the type of each key-value pair in the `source`
    and `destination` mappings and determines how to merge them based on
    their data types, supporting nested dictionaries and TOML data
    structures.

    :param source: The source mapping to merge into the destination.
    :param destination: The destination mapping that will be updated with the
        data from `source`.
    :return: A new mapping that represents the merged result of `source`
        and `destination`.
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
