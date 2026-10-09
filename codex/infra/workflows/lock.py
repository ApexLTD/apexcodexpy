from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from codex.infra.yamler import Yamler

from ..program import Executable, LazyExecutable
from ..pyproject import PyProjectToml
from ..result import ProgramResult
from .base import YamlWorkflow


def hash_of(path: Path) -> str:
    with path.open("rb") as f:
        return hashlib.file_digest(f, hashlib.sha256).hexdigest()


@dataclass(frozen=True, kw_only=True)
class CodexLockWorkflow(YamlWorkflow):
    name: str = "CodexLock"
    path: Path = Path("codex.lock")

    @property
    def standards(self) -> Yamler:
        return Yamler.parse(
            {
                "hashes": {
                    "pyproject": PyProjectToml.latest().hashed(),
                },
            }
        )

    def verify(self, target: Path) -> Executable:
        def _() -> ProgramResult:
            lock = target / self.path

            if not lock.exists():
                return ProgramResult(name=self.name).fail(
                    message="""
                        Lock file does not exist!
                        Run `codex sync` to bring configuration up to date.
                    """
                )

            if self.standards != Yamler.read(lock):
                return ProgramResult(name=self.name).fail(
                    message="""
                        Lock file is outdated!
                        Run `codex sync` to bring configuration up to date.
                    """
                )

            return ProgramResult(name=self.name).success(
                message=f"{self.name} workflow succeeded."
            )

        return LazyExecutable(_)
