from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from codex.infra.program import Executable
from codex.infra.result import ProgramResult


def _pip_config() -> dict[str, Any]:
    return {
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


def _gh_actions_config() -> dict[str, Any]:
    return {
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


STANDARDS = {
    "version": 2,
    "updates": [
        _pip_config(),
        _gh_actions_config(),
    ],
}


@dataclass(frozen=True)
class DependabotYaml:
    dry_run: bool = False

    NAME = "dependabot.yml"

    def sync(self, target: Path) -> Executable:
        dependabot = self.yaml_on(target)
        dependabot.parent.mkdir(parents=True, exist_ok=True)

        return self._sync(dependabot)

    def _sync(self, dependabot: Path) -> Executable:
        if self.dry_run:
            dumped = json.dumps(STANDARDS, indent=2)
            return ProgramResult(name="Dependabot").success(
                stdout=f"Changes would be applied:\n{dumped}",
            )

        with dependabot.open(mode="w", encoding="utf-8", newline="\n") as stream:
            yaml.dump(
                STANDARDS,
                stream,
                Dumper=IndentDumper,
                sort_keys=False,
                default_flow_style=False,
            )

        return ProgramResult(name="Dependabot").success(
            stdout="Configuration synchronized successfully.",
        )

    def yaml_on(self, path: Path) -> Path:
        return path / ".github" / self.NAME


class IndentDumper(yaml.Dumper):
    """Custom dumper to force indentation for list items."""

    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        _ = indentless

        return super().increase_indent(flow, False)
