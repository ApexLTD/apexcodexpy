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
                        "name": "Setup Environment",
                        "uses": "ApexLTD/apexcodexpy/setup@main",
                        "with": {
                            "python": Version.of_python(),
                        },
                    }
                )
            )
            .run(
                step="Build Docker image",
                command=Yamler.folded(
                    lines=[
                        "codex build",
                        "  --tag ${{ github.event.repository.name }}:latest",
                    ]
                ),
            )
            .run(
                step="Push Docker image",
                command=Yamler.folded(
                    lines=[
                        "codex push",
                        "  --tag ${{ github.event.repository.name }}:latest",
                        "  --token ${{ secrets.GITHUB_TOKEN }}",
                        "  --actor ${{ github.actor }}",
                        "  --organization ${{ github.repository_owner }}",
                    ],
                ),
            )
            .yamlify()
            .as_mapping()
        )

        return Yamler.parse(workflow)
