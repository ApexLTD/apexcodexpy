from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import time

from codex.infra.program import Command, Executable, MultiProgram, Program
from codex.infra.pyproject import PyProjectToml
from codex.infra.result import ProgramResult, TaskResult
from codex.infra.tools import (
    Deptry,
    MyPy,
    Pip,
    Poetry,
    PoetryRun,
    Pytest,
    Ruff,
    Version,
)
from codex.infra.workflows import (
    BuildCodeWorkflow,
    CheckCodeWorkflow,
    DependabotWorkflow,
)


@dataclass(frozen=True)
class Codex:
    tools: CodexTools

    @classmethod
    def target(cls, target: Path) -> Codex:
        return cls(CodexTools(target))

    def ci(self, on: bool) -> Codex | CiCodex:
        if on:
            return CiCodex(tools=self.tools)

        return self

    @staticmethod
    def version() -> TaskResult:
        return ProgramResult(name="version").success(message=str(Version()))

    def sync(self, force: bool) -> TaskResult:
        return self.tools.sync(force).execute()

    def lock(self) -> TaskResult:
        return self.tools.lock().execute()

    def update(self) -> TaskResult:
        return self.tools.update().execute()

    def install(self) -> TaskResult:
        return self.tools.install().execute()

    def lint(self) -> TaskResult:
        return self.tools.lint().execute()

    def fix(self, unsafe: bool = False) -> TaskResult:
        return self.tools.fix(unsafe=unsafe).execute()

    def unit(self) -> TaskResult:
        return self.tools.unit().execute()

    def integration(self) -> TaskResult:
        return self.tools.integration().execute()

    def behaviour(self) -> TaskResult:
        return self.tools.behaviour().execute()

    def build(self, tag: str) -> TaskResult:
        return self.tools.build(tag).execute()

    def push(
        self,
        tag: str,
        registry: str,
        organization: str,
        token: str,
        actor: str,
    ) -> TaskResult:
        return self.tools.push(
            tag=tag,
            registry=registry,
            organization=organization,
            token=token,
            actor=actor,
        ).execute()


@dataclass(frozen=True)
class CiCodex:
    tools: CodexTools

    def lint(self) -> TaskResult:
        return (
            MultiProgram()
            .attach(self.tools.install())
            .attach(self.tools.lint())
            .execute()
        )

    def unit(self) -> TaskResult:
        return (
            MultiProgram()
            .attach(self.tools.install())
            .attach(self.tools.unit(in_ci=True))
            .execute()
        )

    def integration(self) -> TaskResult:
        return (
            MultiProgram()
            .attach(self.tools.install())
            .attach(self.tools.integration())
            .execute()
        )

    def behaviour(self) -> TaskResult:
        return (
            MultiProgram()
            .attach(self.tools.install())
            .attach(self.tools.behaviour(in_ci=True))
            .execute()
        )


@dataclass(frozen=True)
class CodexTools:
    target: Path

    def sync(self, force: bool) -> Executable:
        return (
            MultiProgram()
            .attach(PyProjectToml().sync(self.target))
            .attach(DependabotWorkflow().sync(self.target, force=force))
            .attach(CheckCodeWorkflow().sync(self.target, force=force))
            .attach(
                BuildCodeWorkflow(disclaimer=False).sync(self.target, force=force),
                when=self.target.joinpath("Dockerfile").exists(),
            )
        )

    def lock(self) -> Executable:
        return Program(name="lock", command=Poetry().lock())

    def update(self) -> Executable:
        return Program(name="update", command=Poetry().update())

    def install(self) -> Executable:
        return (
            MultiProgram()
            .attach(
                Program(
                    name="tools",
                    command=Pip().install("pip", "poetry"),
                )
            )
            .attach(
                Program(
                    name="dependencies",
                    command=Poetry().install(),
                )
            )
        )

    def lint(self) -> Executable:
        return (
            PoetryRun()
            .attach(
                Program(
                    name="poetry",
                    command=Poetry().lint(self.target),
                )
            )
            .attach(
                Program(
                    name="black",
                    command=Ruff(on=self.target).format().flag(check=True),
                )
            )
            .attach(
                Program(
                    name="dependencies",
                    command=Deptry(on=self.target).lint(),
                )
            )
            .attach(
                Program(
                    name="ruff",
                    command=Ruff(on=self.target).lint(),
                )
            )
            .attach(
                Program(
                    name="mypy",
                    command=MyPy(on=self.target).check(),
                )
            )
        )

    def fix(self, unsafe: bool = False) -> Executable:
        return (
            PoetryRun()
            .attach(
                Program(
                    name="black",
                    command=Ruff(on=self.target).format(),
                )
            )
            .attach(
                Program(
                    name="ruff",
                    command=(
                        Ruff(on=self.target)
                        .lint()
                        .flag(fix=True)
                        .flag(unsafe_fixes=unsafe)
                    ),
                ),
            )
        )

    def unit(self, in_ci: bool = False) -> Executable:
        return PoetryRun().attach(
            Program(
                name="test",
                command=(
                    Pytest.on(self.target)
                    .run()
                    .flag(cov=not in_ci or None)
                    .flag(last_failed=not in_ci or None)
                    .with_a(
                        hypothesis_profile="ci" if in_ci else "dev",
                        when=Version().is_installed("hypothesis"),
                    )
                ),
            )
        )

    def behaviour(self, in_ci: bool = False) -> Executable:
        return PoetryRun().attach(
            Program(
                name="behave",
                command=(
                    Command("behave")
                    .append(self.target / "tests" / "features")
                    .with_a(format="progress" if in_ci else "pretty")
                    .flag(summary=not in_ci)
                ),
            )
        )

    def integration(self) -> Executable:
        return (
            Poetry()
            .export(self.target)
            .attach(
                PoetryRun().attach(
                    Program(
                        name="test",
                        command=Pytest.on(self.target / "tests" / "integration").run(),
                    )
                )
            )
        )

    def build(self, tag: str) -> Executable:
        return (
            Poetry()
            .export(self.target)
            .attach(
                Program(
                    name="build",
                    command=(
                        Command("docker build")
                        .flag(tag=True)
                        .append(tag.lower())
                        .flag(build_arg=True)
                        .with_a(RELEASE=Git().revision() or str(int(time())))
                        .append(self.target)
                    ),
                )
            )
        )

    def push(
        self,
        tag: str,
        registry: str,
        organization: str,
        token: str,
        actor: str,
    ) -> Executable:
        local_tag = tag.lower()
        remote_tag = f"{registry}/{organization.lower()}/{local_tag}"

        return (
            MultiProgram()
            .attach(
                Program(
                    name="tag",
                    command=Command("docker tag").append(local_tag).append(remote_tag),
                )
            )
            .attach(
                Program(
                    name="login",
                    command=(
                        Command("docker login")
                        .append(registry)
                        .flag(username=True)
                        .append(actor)
                        .flag(password=True)
                        .append(token)
                    ),
                )
            )
            .attach(
                Program(
                    name="push",
                    command=Command("docker push").append(remote_tag),
                )
            )
        )


@dataclass(frozen=True)
class Git:
    def revision(self, of: str = "HEAD", short: bool = True) -> str:
        return (
            Program(Command("git rev-parse").flag(short=short).append(of))
            .execute()
            .stdout
        )

    def amend(self) -> TaskResult:
        return Program(
            name="amend",
            command=Command("git commit")
            .flag(all=True)
            .flag(amend=True)
            .flag(edit=False),
        ).execute()
