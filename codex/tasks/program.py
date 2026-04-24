from __future__ import annotations

import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from itertools import chain
from typing import Any

from codex.tasks.result import TaskResult


@dataclass(frozen=True, kw_only=True)
class ShellProgram:
    name: str

    def run(self, *args: Any, **kwargs: Any) -> TaskResult:
        return TaskResult.parse(
            subprocess.run(
                list(self._command_with([*args, *kwargs.values()])),
                text=True,
                encoding="utf-8",
                capture_output=True,
            )
        )

    def _command_with(self, args: Iterable[str]) -> Iterable[str]:
        yield from self.name.split()
        yield from chain.from_iterable(str(arg).split() for arg in args)
