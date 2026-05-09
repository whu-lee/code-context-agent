from __future__ import annotations

import hashlib
from pathlib import Path

from .models import SourceFile


LANGUAGE_BY_SUFFIX = {
    ".java": "java",
    ".proto": "proto",
    ".xml": "xml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".properties": "properties",
    ".gradle": "gradle",
}

SPECIAL_FILENAMES = {
    "pom.xml": "maven",
    "build.gradle": "gradle",
    "settings.gradle": "gradle",
}

IGNORED_DIRS = {
    ".git",
    ".idea",
    ".gradle",
    "target",
    "build",
    "out",
    "node_modules",
}


def default_index_dir(repo: Path) -> Path:
    digest = hashlib.sha256(str(repo.resolve()).encode("utf-8")).hexdigest()[:16]
    return Path.home() / ".codeagent" / "indexes" / digest


def scan_repo(repo: Path) -> list[SourceFile]:
    repo = repo.resolve()
    files: list[SourceFile] = []
    for path in sorted(repo.rglob("*")):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRS for part in path.relative_to(repo).parts):
            continue

        rel_path = path.relative_to(repo).as_posix()
        language = SPECIAL_FILENAMES.get(path.name) or LANGUAGE_BY_SUFFIX.get(path.suffix)
        if not language:
            continue

        files.append(
            SourceFile(
                path=path,
                rel_path=rel_path,
                language=language,
                sha256=_sha256(path),
                module=_infer_module(rel_path),
            )
        )
    return files


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _infer_module(rel_path: str) -> str | None:
    parts = rel_path.split("/")
    markers = {"src", "proto", "resources"}
    for idx, part in enumerate(parts):
        if part in markers:
            return "/".join(parts[:idx]) or None
    return parts[0] if len(parts) > 1 else None
