from __future__ import annotations

import copy
import hashlib
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any

import tomlkit

from codex.infra.result import ProgramResult

if TYPE_CHECKING:
    from collections.abc import Mapping

    from codex.infra.program import Executable


@dataclass(frozen=True)
class PyProjectToml:
    name: str = "PyProject"
    path: Path = Path("pyproject.toml")

    def sync(self, target: Path) -> Executable:
        pyproject = PyProjectFile(target / self.path, standards=self.standards)

        if not pyproject.exists():
            return ProgramResult(name=self.name).fail(message=f"{self.name} not found.")

        if not pyproject.is_outdated():
            return ProgramResult(name=self.name).no_changes()

        pyproject.sync()

        return ProgramResult(name=self.name).workflow_success()

    @property
    def standards(self) -> Mapping[str, Any]:
        return {
            "tool": {
                "mypy": self._mypy,
                "ruff": self._ruff,
                "coverage": self._coveragepy,
            }
        }

    @property
    def _mypy(self) -> dict[str, Any]:
        return {
            "strict": True,
            "ignore_missing_imports": True,
            "show_error_codes": True,
            "pretty": True,
        }

    @property
    def _ruff(self) -> dict[str, Any]:
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

    @property
    def _coveragepy(self) -> dict[str, Any]:
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


@dataclass(frozen=True)
class PyProjectFile:
    path: Path

    standards: Mapping[str, Any] = field(default_factory=dict)

    @cached_property
    def current(self) -> Tomler:
        return Tomler.read(self.path)

    @cached_property
    def latest(self) -> Tomler:
        return self.current.update_with(self.standards)

    def exists(self) -> bool:
        return self.path.exists()

    def is_outdated(self) -> bool:
        return self.current != self.latest

    def sync(self) -> None:
        self.path.write_text(self.latest.dumps(), encoding="utf-8", newline="\n")


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
