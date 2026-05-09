from __future__ import annotations

import re
from pathlib import Path

from .models import AnalysisResult, Edge, Node, SourceFile

_TAG = re.compile(r"<(?P<tag>\w[\w.-]*)(?:[^>]*)>(?P<content>[^<]*)</(?P=tag)>", re.DOTALL)
_DEPENDENCY_BLOCK = re.compile(r"<dependency>(.*?)</dependency>", re.DOTALL)
_MODULE_BLOCK = re.compile(r"<modules>(.*?)</modules>", re.DOTALL)


def analyze_pom(source: SourceFile) -> AnalysisResult:
    text = source.path.read_text(encoding="utf-8", errors="ignore")
    result = AnalysisResult()

    group_id = _tag_value(text, "groupId") or ""
    artifact_id = _tag_value(text, "artifactId") or ""
    version = _tag_value(text, "version") or ""
    packaging = _tag_value(text, "packaging") or "jar"

    if not artifact_id:
        return result

    pom_qn = f"maven:{group_id}:{artifact_id}"
    result.nodes.append(
        Node(
            type="MavenModule",
            name=artifact_id,
            qualified_name=pom_qn,
            file_path=source.rel_path,
            metadata={
                "group_id": group_id,
                "artifact_id": artifact_id,
                "version": version,
                "packaging": packaging,
                "module": source.module,
            },
        )
    )

    parent_group = _parent_tag(text, "groupId")
    parent_artifact = _parent_tag(text, "artifactId")
    if parent_artifact:
        parent_qn = f"maven:{parent_group or group_id}:{parent_artifact}"
        result.edges.append(Edge(pom_qn, parent_qn, "CHILD_OF"))

    modules_match = _MODULE_BLOCK.search(text)
    if modules_match:
        for m in _TAG.finditer(modules_match.group(1)):
            if m.group("tag") == "module":
                sub_name = m.group("content").strip()
                sub_qn = f"maven-submodule:{artifact_id}/{sub_name}"
                result.nodes.append(
                    Node(
                        type="MavenSubmoduleRef",
                        name=sub_name,
                        qualified_name=sub_qn,
                        file_path=source.rel_path,
                        metadata={"parent_artifact": artifact_id},
                    )
                )
                result.edges.append(Edge(pom_qn, sub_qn, "INCLUDES_MODULE"))

    for dep_match in _DEPENDENCY_BLOCK.finditer(text):
        block = dep_match.group(1)
        dep_group = _tag_value(block, "groupId") or ""
        dep_artifact = _tag_value(block, "artifactId") or ""
        dep_version = _tag_value(block, "version") or ""
        dep_scope = _tag_value(block, "scope") or "compile"
        if not dep_artifact:
            continue
        dep_qn = f"maven:{dep_group}:{dep_artifact}"
        result.edges.append(
            Edge(
                pom_qn,
                dep_qn,
                "DEPENDS_ON",
                {"version": dep_version, "scope": dep_scope},
            )
        )

    return result


def _tag_value(text: str, tag: str) -> str | None:
    pattern = re.compile(rf"<{tag}>([^<]*)</{tag}>")
    m = pattern.search(text)
    return m.group(1).strip() if m else None


def _parent_tag(text: str, tag: str) -> str | None:
    parent_block = re.search(r"<parent>(.*?)</parent>", text, re.DOTALL)
    if not parent_block:
        return None
    return _tag_value(parent_block.group(1), tag)
