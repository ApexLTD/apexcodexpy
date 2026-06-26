from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from codex.infra.tools import Version
from codex.infra.yamler import Yamler

from .base import YamlWorkflow
from .ci import CiJob


@dataclass(frozen=True, kw_only=True)
class BuildCodeWorkflow(YamlWorkflow):
    name: str = "BuildCode"
    path: Path = Path(".github") / "workflows" / "build_code.yml"

    @property
    def standards(self) -> Yamler:
        workflow = Yamler.read(self.path).as_mapping()
        workflow["name"] = "Build Python Application"
        workflow["on"] = {"push": {"branches": ["main"]}}
        workflow["permissions"] = "write-all"
        workflow["jobs"] = workflow.get("jobs", {})
        workflow["jobs"]["build"] = (
            CiJob(name="build")
            .with_step(
                Yamler.parse(
                    {
                        "name": "Checkout Code",
                        "uses": "actions/checkout@v7",
                    }
                )
            )
            .with_step(
                Yamler.parse(
                    {
                        "name": "Setup Python",
                        "uses": "actions/setup-python@v6",
                        "with": {
                            "python-version": Version.of_python(),
                            "pip-install": "apexcodexpy",
                        },
                    }
                )
            )
            .run(
                step="Build Docker image",
                command=Yamler.folded(
                    "codex build",
                    "--tag ${{ github.event.repository.name }}:latest",
                ),
            )
            .run(
                step="Push Docker image",
                command=Yamler.folded(
                    "codex push",
                    "--tag ${{ github.event.repository.name }}:latest",
                    "--token ${{ secrets.GITHUB_TOKEN }}",
                    "--actor ${{ github.actor }}",
                    "--organization ${{ github.repository_owner }}",
                ),
            )
            .yamlify()
            .as_mapping()
        )

        return Yamler.parse(workflow)
