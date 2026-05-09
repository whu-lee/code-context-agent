from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


Metadata = dict[str, Any]


@dataclass(frozen=True)
class SourceFile:
    path: Path
    rel_path: str
    language: str
    sha256: str
    module: str | None = None


@dataclass(frozen=True)
class Node:
    type: str
    name: str
    qualified_name: str
    file_path: str | None = None
    start_line: int | None = None
    end_line: int | None = None
    metadata: Metadata = field(default_factory=dict)


@dataclass(frozen=True)
class Edge:
    from_qn: str
    to_qn: str
    type: str
    metadata: Metadata = field(default_factory=dict)


@dataclass
class AnalysisResult:
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)

    def extend(self, other: "AnalysisResult") -> None:
        self.nodes.extend(other.nodes)
        self.edges.extend(other.edges)
