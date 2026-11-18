from __future__ import annotations

import copy
import hashlib
from contextlib import suppress
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any

import tomlkit

from codex.infra.result import ProgramResult

if TYPE_CHECKING:
    from codex.infra.program import Executable


_TomlMapping = dict[str, list[Any] | dict[str, Any] | bool | None]


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
    def standards(self) -> _TomlMapping:
        return {
            "tool": {
                "mypy": self._mypy,
                "ruff": self._ruff,
                "coverage": self._coveragepy,
                "deptry": self._deptry,
            }
        }

    @property
    def _mypy(self) -> _TomlMapping:
        return {
            "strict": True,
            "ignore_missing_imports": True,
            "show_error_codes": True,
            "pretty": True,
        }

    @property
    def _ruff(self) -> _TomlMapping:
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
    def _coveragepy(self) -> _TomlMapping:
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
    def _deptry(self) -> _TomlMapping:
        return {"extend_exclude": ["migrations"]}


@dataclass(frozen=True)
class PyProjectFile:
    path: Path

    standards: _TomlMapping = field(default_factory=dict)

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
    document: _TomlMapping

    @classmethod
    def read(cls, path: Path) -> Tomler:
        return cls(tomlkit.parse(path.read_text(encoding="utf-8")))

    def dumps(self) -> str:
        return tomlkit.dumps(self.document)

    def update_with(self, source: _TomlMapping) -> Tomler:
        return Tomler(deep_merge(source, self.document))

    def hashed(self) -> str:
        return hashlib.sha256(self.dumps().encode()).hexdigest()


def deep_merge(source: _TomlMapping, destination: _TomlMapping) -> _TomlMapping:
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
        match updates:
            case dict():  # Merge recursively
                as_id = result.get(key, {})
                assert isinstance(as_id, dict), f"Expected dict, got {as_id}"

                result[key] = deep_merge(updates, as_id)
            case list():  # Combine as TOML array
                as_is = result.get(key, [])
                assert isinstance(as_is, list), f"Expected list, got {as_is}"

                combo = tomlkit.array()
                combo.extend(copy.deepcopy(sorted(set(updates + as_is))))
                combo.multiline(multiline=True)

                result[key] = combo
            case None:  # Erase key
                with suppress(KeyError):
                    del result[key]
            case _:
                result[key] = updates

    return result
