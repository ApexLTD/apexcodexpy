from __future__ import annotations

from collections.abc import MutableMapping, MutableSequence
from dataclasses import dataclass, field
from pathlib import Path

from codex.infra.tools import Version
from codex.infra.yamler import Yamler

from .base import YamlWorkflow
from .ci import CiJob


@dataclass(frozen=True, kw_only=True)
class CheckCodeWorkflow(YamlWorkflow):
    name: str = "CheckCode"
    path: Path = Path(".github") / "workflows" / "check_code.yml"

    @property
    def standards(self) -> Yamler:
        return (
            CiWorkflow(name="Validate Python Code")
            .with_job(
                CodeCheckJob(name="lint")
                .run(
                    step="Lint Code",
                    command="codex lint --ci",
                )
                .enabled(True)
            )
            .with_job(
                CodeCheckJob(name="test-unit")
                .run(
                    step="Run unit tests",
                    command="codex test unit --ci",
                )
                .enabled(True)
            )
            .with_job(
                CodeCheckJob(name="test-integration")
                .run(
                    step="Run integration tests",
                    command="codex test integration --ci",
                )
                .enabled(when=Version().is_installed("pytest-docker"))
            )
            .with_job(
                CodeCheckJob(name="test-behaviour")
                .run(
                    step="Run behaviour tests",
                    command="codex test behaviour --ci",
                )
                .enabled(when=Version().is_installed("behave"))
            )
            .yamlify()
        )


@dataclass(frozen=True)
class CiWorkflow:
    name: str

    jobs: MutableMapping[str, Yamler] = field(default_factory=dict)

    def with_job(self, value: CiJob) -> CiWorkflow:
        if value.is_enabled:
            self.jobs[value.name] = value.yamlify()

        return self

    def yamlify(self) -> Yamler:
        return Yamler.parse(
            {
                "name": self.name,
                "on": {"pull_request": {"branches": ["main"]}},
                "permissions": {"contents": "read"},
                "jobs": {name: job.as_mapping() for name, job in self.jobs.items()},
            }
        )


CHECKOUT = Yamler.parse(
    {
        "name": "Checkout Code",
        "uses": "actions/checkout@v7",
    }
).anchor("checkout")
SETUP = Yamler.parse(
    {
        "name": "Setup Python",
        "uses": "actions/setup-python@v6",
        "with": {
            "python-version": Version.of_python(),
            "pip-install": f"apexcodexpy=={Version()}",
        },
    }
).anchor("setup")


@dataclass(frozen=True)
class CodeCheckJob(CiJob):
    steps: MutableSequence[Yamler] = field(default_factory=lambda: [CHECKOUT, SETUP])
