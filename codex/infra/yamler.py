from __future__ import annotations

import io
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap


@dataclass(frozen=True, kw_only=True)
class Yamler:
    value: CommentedMap

    def as_mapping(self) -> CommentedMap:
        return self.value

    @classmethod
    def read(cls, path: Path) -> Yamler:
        return cls(value=YAML().load(path))

    @classmethod
    def parse(cls, data: Mapping[str, Any]) -> Yamler:
        serializer = YAML()
        serializer.indent(mapping=2, sequence=4, offset=2)

        stream = io.StringIO()
        serializer.dump(data, stream)

        stream.seek(0)
        loaded = serializer.load(stream)

        return cls(value=loaded)

    def anchor(self, name: str) -> Yamler:
        self.value.yaml_set_anchor(name, always_dump=True)

        return self

    def comment(self, *messages: str) -> Yamler:
        self.value.yaml_set_start_comment("\n".join(messages))

        return self

    def dump_to(self, path: Path) -> None:
        serializer = YAML()
        serializer.indent(mapping=2, sequence=4, offset=2)

        with path.open("w", newline="\n") as stream:
            serializer.dump(self.value, stream)
