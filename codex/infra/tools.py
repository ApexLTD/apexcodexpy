from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from codex.infra.program import Program


@dataclass(frozen=True, kw_only=True)
class Pip:
    def install(self, *packages: str) -> Program:
        return (
            Program("python -m pip")
            .append("install")
            .flag(upgrade=True)
            .extend(packages)
        )


@dataclass(frozen=True, kw_only=True)
class Poetry:
    def install(self) -> Program:
        return Program("poetry install")

    def lock(self) -> Program:
        return Program("poetry lock")

    def update(self) -> Program:
        return Program("poetry update")

    def lint(self, target: Path) -> Program:
        return Program("poetry check").with_a(project=target).flag(strict=True)

    def run(self, program: Program) -> Program:
        return Program(f"poetry run {program}")

    def export(self, target: Path) -> Program:
        return (
            Program("poetry export")
            .flag(without_hashes=True)
            .with_a(output="requirements.txt")
            .with_a(directory=target)
        )


@dataclass(frozen=True, kw_only=True)
class Ruff:
    on: Path

    def lint(self) -> Program:
        return Program("ruff check").append(self.on)

    def format(self) -> Program:
        return Program("ruff format").append(self.on)


@dataclass(frozen=True, kw_only=True)
class MyPy:
    on: Path

    def check(self) -> Program:
        return Program("mypy").append(self.on)


@dataclass(frozen=True)
class Pytest:
    target: Path | None = None

    @classmethod
    def on(cls, target: Path) -> Pytest:
        return cls(target) if target.resolve() != Path.cwd() else cls()

    def run(
        self,
        with_coverage: bool | None = None,
        last_failed: bool | None = None,
    ) -> Program:
        return (
            Program("pytest")
            .append(self.target)
            .flag(cov=with_coverage)
            .flag(last_failed=last_failed)
        )
