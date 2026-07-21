from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from codex.infra.tools import Version
from codex.infra.yamler import Yamler

from .base import YamlWorkflow
from .ci import CiJob, CiWorkflow


@dataclass(frozen=True, kw_only=True)
class CheckCodeWorkflow(YamlWorkflow):
    name: str = "CheckCode"
    path: Path = Path(".github") / "workflows" / "check_code.yml"

    SETUP = Yamler.parse(
        {
            "name": "Setup Environment",
            "uses": "ApexLTD/actions/setup@main",
            "with": {
                "python": Version.of_python(),
                "codex": str(Version()),
            },
        }
    ).anchor("setup")

    @property
    def standards(self) -> Yamler:
        return (
            CiWorkflow(name="Validate Python Code")
            .with_job(
                CiJob(name="lint")
                .with_step(self.SETUP)
                .run(
                    step="Lint Code",
                    command="codex lint --ci",
                )
                .enabled(True)
            )
            .with_job(
                CiJob(name="test-unit")
                .needs("lint")
                .with_step(self.SETUP)
                .run(
                    step="Run unit tests",
                    command="codex test unit --ci",
                )
                .enabled(True)
            )
            .with_job(
                CiJob(name="test-integration")
                .needs("lint", "test-unit")
                .with_step(self.SETUP)
                .run(
                    step="Run integration tests",
                    command="codex test integration --ci",
                )
                .enabled(when=Version().is_installed("pytest-docker"))
            )
            .with_job(
                CiJob(name="test-behaviour")
                .needs("lint", "test-unit")
                .with_step(self.SETUP)
                .run(
                    step="Run behaviour tests",
                    command="codex test behaviour --ci",
                )
                .enabled(when=Version().is_installed("behave"))
            )
            .yamlify()
        )
