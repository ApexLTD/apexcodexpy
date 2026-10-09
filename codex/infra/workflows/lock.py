from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from codex.infra.yamler import Yamler

from ..pyproject import PyProjectToml
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

    def verify(self) -> bool:
        return self.path.exists() and self.standards == Yamler.read(self.path)
