from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import time

from codex.infra.tasks import ComboResult, DependabotYaml, PyProjectToml, TaskResult
from codex.infra.tools import MyPy, Pip, Poetry, Program, Ruff


@dataclass(frozen=True)
class Codex:
    target: Path

    in_ci: bool = False

    def ci(self, on: bool) -> Codex:
        return Codex(self.target, in_ci=on)

    def sync(self, dry_run: bool = False) -> TaskResult:
        return (
            ComboResult()
            .attach(pyproject=PyProjectToml(dry_run=dry_run).sync(self.target))
            .attach(dependabot=DependabotYaml(dry_run=dry_run).sync(self.target))
        )

    def install(self) -> TaskResult:
        return self._install(when=True)

    def _install(self, when: bool) -> ComboResult:
        return (
            (
                ComboResult()
                .attach(tools=Pip().install("pip", "poetry"))
                .attach(dependencies=Poetry().install().execute())
            )
            if when
            else ComboResult()
        )

    def lock(self) -> TaskResult:
        return ComboResult().attach(lock=Poetry().lock().execute())

    def update(self) -> TaskResult:
        return ComboResult().attach(update=Poetry().update().execute())

    def lint(self) -> TaskResult:
        return (
            self._install(when=self.in_ci)
            .attach(poetry=Poetry().lint(self.target).execute())
            .attach(
                black=Poetry()
                .run(Ruff(on=self.target).format().flag(check=True))
                .execute()
            )
            .attach(ruff=Poetry().run(Ruff(on=self.target).lint()).execute())
            .attach(mypy=Poetry().run(MyPy(on=self.target).check()).execute())
        )

    def fix(self, unsafe: bool = False) -> TaskResult:
        return (
            ComboResult()
            .attach(black=Poetry().run(Ruff(on=self.target).format()).execute())
            .attach(
                ruff=Poetry()
                .run(
                    Ruff(on=self.target).lint().flag(fix=True).flag(unsafe_fixes=unsafe)
                )
                .execute()
            )
        )

    def test(self) -> TaskResult:
        return self._install(when=self.in_ci).attach(self.test_unit())

    def test_unit(self) -> TaskResult:
        return CodexTest(self.target).ci(on=self.in_ci).unit()

    def test_integration(self) -> TaskResult:
        return CodexTest(self.target).integration()

    def test_behaviour(self) -> TaskResult:
        return CodexTest(self.target).behaviour()

    def build(self, tag: str) -> TaskResult:
        return (
            ComboResult()
            .attach(
                setup=(
                    ComboResult()
                    .attach(tools=Pip().install("poetry", "poetry-plugin-export"))
                    .attach(export=Poetry().export(self.target).execute())
                )
            )
            .attach(
                docker=(
                    Program("docker build")
                    .flag(tag=True)
                    .append(tag)
                    .flag(build_arg=True)
                    .with_a(RELEASE=Git().revision() or str(int(time())))
                    .append(self.target)
                    .execute()
                )
            )
            .attach(
                teardown=Program("rm")
                .append(self.target / "requirements.txt")
                .execute()
            )
        )


@dataclass(frozen=True)
class CodexTest:
    target: Path

    in_ci: bool = False

    def ci(self, on: bool = False) -> CodexTest:
        return CodexTest(self.target, in_ci=on)

    def unit(self) -> TaskResult:
        return ComboResult().attach(
            pytest=Poetry()
            .run(
                Pytest.on(self.target).run(
                    with_coverage=self._when_not_in_ci(),
                    last_failed=self._when_not_in_ci(),
                )
            )
            .execute()
        )

    def _when_not_in_ci(self) -> bool | None:
        return None if self.in_ci else True

    def integration(self) -> TaskResult:
        return (
            ComboResult()
            .attach(
                setup=(
                    ComboResult()
                    .attach(tools=Pip().install("poetry", "poetry-plugin-export"))
                    .attach(export=Poetry().export(self.target).execute())
                )
            )
            .attach(
                pytest=Poetry()
                .run(Pytest.on(self.target / "tests" / "integration").run())
                .execute()
            )
            .attach(
                teardown=Program("rm")
                .append(self.target / "requirements.txt")
                .execute()
            )
        )

    def behaviour(self) -> TaskResult:
        return ComboResult().attach(
            behave=Poetry()
            .run(Program("behave").append(self.target / "tests" / "features"))
            .execute()
        )


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


@dataclass(frozen=True)
class Git:
    def revision(self, of: str = "HEAD", short: bool = True) -> str:
        return Program("git rev-parse").flag(short=short).append(of).execute().stdout

    def amend(self) -> TaskResult:
        return ComboResult().attach(
            amend=(
                Program("git commit")
                .flag(all=True)
                .flag(amend=True)
                .flag(edit=False)
                .execute()
            )
        )
