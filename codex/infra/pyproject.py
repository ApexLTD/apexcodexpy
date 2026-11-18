from __future__ import annotations

import contextlib
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
                "deptry": self._deptry,
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
            "extend-exclude": ["migrations"],
            "lint": {
                "mccabe": None,
                "select": [
                    "A",
                    "ARG",
                    "B",
                    "C4",
                    "DTZ",
                    "E",
                    "F",
                    "FBT",
                    "FLY",
                    "FURB",
                    "I",
                    "LOG",
                    "N",
                    "PERF",
                    "PGH",
                    "PIE",
                    "PL",
                    "PT",
                    "PTH",
                    "PYI",
                    "RET",
                    "RSE",
                    "RUF",
                    "SIM",
                    "SLF",
                    "T20",
                    "TCH",
                    "TRY",
                    "UP",
                    "W",
                ],
                "ignore": [
                    "PLR2004",
                    "TRY003",
                ],
            },
        }

    @property
    def _coveragepy(self) -> dict[str, Any]:
        return {
            "run": {
                "branch": True,
            },
            "report": {
                "exclude_also": [
                    r"@(abc\.)?abstractmethod",
                    r"class .*\bProtocol\)",
                    r"if TYPE_CHECKING:",
                ],
                "skip_empty": True,
                "skip_covered": True,
                "show_missing": True,
                "sort": "Cover",
            },
        }

    @property
    def _deptry(self) -> dict[str, Any]:
        return {"extend_exclude": ["migrations"]}


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

    for key, updates in source.items():
        as_is = result.get(key)

        match updates:
            case None:
                # Source is None -> Erase destination key completely
                with contextlib.suppress(KeyError):
                    del result[key]
            case dict():
                # Source is a dict -> merge recursively
                result[key] = deep_merge(updates, as_is or {})
            case list():
                # Source is a list -> Combine as TOML array
                new_array = tomlkit.array()
                new_array.extend(copy.deepcopy(sorted(set(updates + as_is))))
                new_array.multiline(multiline=True)
                result[key] = new_array
            case _:
                # Overwrite with source value
                result[key] = copy.deepcopy(updates)

    return result
