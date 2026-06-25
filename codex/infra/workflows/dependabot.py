from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from codex.infra.yamler import Yamler

from .workflows import YamlWorkflow


@dataclass(frozen=True, kw_only=True)
class DependabotWorkflow(YamlWorkflow):
    name: str = "Dependabot"
    path: Path = Path(".github") / "dependabot.yml"

    @property
    def standards(self) -> Yamler:
        return Yamler.parse(
            {
                "version": 2,
                "updates": [
                    self._pip_config().as_mapping(),
                    self._gh_actions_config().as_mapping(),
                ],
            }
        )

    @staticmethod
    def _pip_config() -> Yamler:
        return Yamler.parse(
            {
                "package-ecosystem": "pip",
                "directory": "/",
                "schedule": {
                    "interval": "weekly",
                    "day": "thursday",
                },
                "groups": {
                    "python": {
                        "patterns": ["*"],
                    }
                },
            }
        )

    @staticmethod
    def _gh_actions_config() -> Yamler:
        return Yamler.parse(
            {
                "package-ecosystem": "github-actions",
                "directory": "/",
                "schedule": {
                    "interval": "weekly",
                    "day": "thursday",
                },
                "groups": {
                    "gh-actions": {
                        "patterns": ["*"],
                    }
                },
            }
        )
