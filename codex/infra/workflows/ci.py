from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING

from codex.infra.yamler import Yamler

if TYPE_CHECKING:
    from collections.abc import MutableMapping, MutableSequence


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


@dataclass(frozen=True)
class CiJob:
    name: str

    platform: str = "ubuntu-latest"
    is_enabled: bool = True

    _steps: MutableSequence[Yamler] = field(default_factory=list)
    _needs: MutableSequence[str] = field(default_factory=list)

    def needs(self, *names: str) -> CiJob:
        self._needs.extend(names)

        return self

    def with_step(self, step: Yamler) -> CiJob:
        self._steps.append(step)

        return self

    def run(self, step: str, command: str) -> CiJob:
        return self.with_step(Yamler.parse({"name": step, "run": command}))

    def enabled(self, when: bool) -> CiJob:
        return replace(self, is_enabled=when)

    def yamlify(self) -> Yamler:
        return Yamler.parse(
            {
                "runs-on": self.platform,
                **({"needs": self._needs} if self._needs else {}),
                "steps": [step.as_mapping() for step in self._steps],
            }
        )
