from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from codex.infra.tools import Version
from codex.infra.yamler import Yamler

from .workflows import CiWorkflow, CodeCheckJob, YamlWorkflow


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
