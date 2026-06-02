from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from codex.infra.program import Command, MultiProgram, Program
from codex.infra.result import TaskResult


@dataclass(frozen=True, kw_only=True)
class Pip:
    def install(self, *packages: str) -> Command:
        return (
            Command("python -m pip")
            .append("install")
            .flag(upgrade=True)
            .extend(packages)
        )


@dataclass(frozen=True, kw_only=True)
class Poetry:
    def install(self) -> Command:
        return Command("poetry install")

    def lock(self) -> Command:
        return Command("poetry lock")

    def update(self) -> Command:
        return Command("poetry update")

    def lint(self, target: Path) -> Command:
        return Command("poetry check").with_a(project=target).flag(strict=True)

    def run(self, program: Command) -> Command:
        return Command(f"poetry run {program}")

    def export(self, target: Path) -> Command:
        return (
            Command("poetry export")
            .flag(without_hashes=True)
            .with_a(output="requirements.txt")
            .with_a(directory=target)
        )


@dataclass(frozen=True)
class PoetryRun:
    programs: list[Program] = field(default_factory=list)

    def attach(self, **program: Command) -> PoetryRun:
        for name, value in program.items():
            self.programs.append(Program(name=name, command=value))

        return self

    def execute(self) -> TaskResult:
        return MultiProgram({p.name: p for p in self.programs}).execute()


@dataclass(frozen=True, kw_only=True)
class Ruff:
    on: Path

    def lint(self) -> Command:
        return Command("ruff check").append(self.on)

    def format(self) -> Command:
        return Command("ruff format").append(self.on)


@dataclass(frozen=True, kw_only=True)
class MyPy:
    on: Path

    def check(self) -> Command:
        return Command("mypy").append(self.on)


@dataclass(frozen=True)
class Pytest:
    target: Path | None = None

    @classmethod
    def on(cls, target: Path) -> Pytest:
        return cls(target) if target.resolve() != Path.cwd() else cls()

    def run(self) -> Command:
        return Command("pytest").append(self.target)
