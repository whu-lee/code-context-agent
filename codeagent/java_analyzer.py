from __future__ import annotations

import re

from .models import AnalysisResult, Edge, Node, SourceFile


PACKAGE_RE = re.compile(r"^\s*package\s+([\w.]+)\s*;", re.MULTILINE)
IMPORT_RE = re.compile(r"^\s*import\s+(?:static\s+)?([\w.*]+)\s*;", re.MULTILINE)
CLASS_RE = re.compile(
    r"(?P<annotations>(?:^\s*@[\w.]+(?:\([^)]*\))?\s*\n)*)"
    r"^\s*(?P<mods>(?:public|protected|private|abstract|final|static|\s)+)?"
    r"(?P<kind>class|interface|enum)\s+(?P<name>\w+)"
    r"(?:\s+extends\s+(?P<extends>[\w.<>]+))?"
    r"(?:\s+implements\s+(?P<implements>[\w.,\s<>]+))?"
    r"\s*\{",
    re.MULTILINE,
)
FIELD_RE = re.compile(
    r"(?P<annotations>(?:^\s*@[\w.]+(?:\([^)]*\))?\s*\n)*)"
    r"^\s*(?:private|protected|public)?\s*(?:final\s+)?(?P<type>[\w.<>]+)\s+(?P<name>\w+)\s*(?:=|;)",
    re.MULTILINE,
)
METHOD_RE = re.compile(
    r"(?P<annotations>(?:^\s*@[\w.]+(?:\([^)]*\))?\s*\n)*)"
    r"^\s*(?:public|protected|private)?\s*(?:static\s+)?(?:final\s+)?"
    r"(?P<return>[\w.<>]+|void)\s+(?P<name>\w+)\s*\((?P<params>[^)]*)\)\s*(?:throws\s+[\w.,\s]+)?\s*\{",
    re.MULTILINE,
)
CONSTRUCTOR_RE = re.compile(
    r"(?P<annotations>(?:^\s*@[\w.]+(?:\([^)]*\))?\s*\n)*)"
    r"^\s*(?:public|protected|private)?\s*(?P<name>\w+)\s*\((?P<params>[^)]*)\)\s*(?:throws\s+[\w.,\s]+)?\s*\{",
    re.MULTILINE,
)
CALL_RE = re.compile(r"(?:(?P<receiver>\b\w+)\s*\.)?(?P<method>\b\w+)\s*\(")
IGNORED_CALLS = {
    "if",
    "for",
    "while",
    "switch",
    "catch",
    "return",
    "throw",
    "new",
    "super",
    "this",
}


def analyze_java(source: SourceFile) -> AnalysisResult:
    text = source.path.read_text(encoding="utf-8", errors="ignore")
    package = _first(PACKAGE_RE, text) or ""
    imports = IMPORT_RE.findall(text)
    result = AnalysisResult()

    file_qn = f"java-file:{source.rel_path}"
    result.nodes.append(
        Node(
            type="JavaFile",
            name=source.path.name,
            qualified_name=file_qn,
            file_path=source.rel_path,
            metadata={"package": package, "imports": imports, "module": source.module},
        )
    )

    for class_match in CLASS_RE.finditer(text):
        class_name = class_match.group("name")
        class_qn = f"java:{package}.{class_name}" if package else f"java:{class_name}"
        body, end_line = _block_body(text, class_match.end() - 1)
        body_offset = class_match.end()
        class_node_type = {"class": "JavaClass", "interface": "JavaInterface", "enum": "JavaEnum"}[class_match.group("kind")]
        annotations = _annotations(class_match.group("annotations"))

        result.nodes.append(
            Node(
                type=class_node_type,
                name=class_name,
                qualified_name=class_qn,
                file_path=source.rel_path,
                start_line=_line(text, class_match.start()),
                end_line=end_line,
                metadata={
                    "package": package,
                    "annotations": annotations,
                    "imports": imports,
                    "modifiers": (class_match.group("mods") or "").split(),
                },
            )
        )
        result.edges.append(Edge(file_qn, class_qn, "DECLARES"))

        extends = class_match.group("extends")
        if extends:
            result.edges.append(Edge(class_qn, _java_type_qn(extends, package, imports), "EXTENDS"))

        implements = class_match.group("implements")
        if implements:
            for item in _split_types(implements):
                result.edges.append(Edge(class_qn, _java_type_qn(item, package, imports), "IMPLEMENTS"))

        field_types: dict[str, str] = {}
        for field_match in FIELD_RE.finditer(body):
            field_name = field_match.group("name")
            field_type = field_match.group("type")
            if field_name == class_name:
                continue
            field_types[field_name] = field_type
            field_qn = f"{class_qn}.{field_name}"
            field_annotations = _annotations(field_match.group("annotations"))
            result.nodes.append(
                Node(
                    type="JavaField",
                    name=field_name,
                    qualified_name=field_qn,
                    file_path=source.rel_path,
                    start_line=_line(text, body_offset + field_match.start()),
                    metadata={"field_type": field_type, "annotations": field_annotations},
                )
            )
            result.edges.append(Edge(class_qn, field_qn, "CONTAINS"))
            if _is_injection(field_annotations):
                result.edges.append(Edge(class_qn, _java_type_qn(field_type, package, imports), "INJECTS", {"via": "field"}))

        for method_match in METHOD_RE.finditer(body):
            _add_method(
                result,
                source,
                class_qn,
                class_name,
                method_match,
                text,
                body_offset,
                package,
                imports,
                field_types,
                is_constructor=False,
            )

        for ctor_match in CONSTRUCTOR_RE.finditer(body):
            if ctor_match.group("name") == class_name:
                _add_method(
                    result,
                    source,
                    class_qn,
                    class_name,
                    ctor_match,
                    text,
                    body_offset,
                    package,
                    imports,
                    field_types,
                    is_constructor=True,
                )

    return result


def _add_method(
    result: AnalysisResult,
    source: SourceFile,
    class_qn: str,
    class_name: str,
    match: re.Match[str],
    full_text: str,
    body_offset: int,
    package: str,
    imports: list[str],
    field_types: dict[str, str],
    is_constructor: bool,
) -> None:
    method_name = "<init>" if is_constructor else match.group("name")
    params = _params(match.group("params"))
    signature = ",".join(param_type for param_type, _ in params)
    method_qn = f"{class_qn}#{method_name}({signature})"
    absolute_start = body_offset + match.start()
    absolute_open_brace = body_offset + match.end() - 1
    body, end_line = _block_body(full_text, absolute_open_brace)
    annotations = _annotations(match.group("annotations"))

    result.nodes.append(
        Node(
            type="JavaMethod",
            name=method_name,
            qualified_name=method_qn,
            file_path=source.rel_path,
            start_line=_line(full_text, absolute_start),
            end_line=end_line,
            metadata={
                "return_type": "constructor" if is_constructor else match.group("return"),
                "params": [{"type": t, "name": n} for t, n in params],
                "annotations": annotations,
            },
        )
    )
    result.edges.append(Edge(class_qn, method_qn, "CONTAINS"))

    if is_constructor:
        for param_type, _ in params:
            if _looks_like_service_type(param_type):
                result.edges.append(Edge(class_qn, _java_type_qn(param_type, package, imports), "INJECTS", {"via": "constructor"}))

    for call in CALL_RE.finditer(body):
        call_name = call.group("method")
        if call_name in IGNORED_CALLS or call_name == class_name:
            continue
        receiver = call.group("receiver")
        metadata = {"receiver": receiver, "resolution": "unresolved", "confidence": 0.35}
        if receiver and receiver in field_types:
            target_type = _java_type_qn(field_types[receiver], package, imports)
            target_qn = f"{target_type}#{call_name}(*)"
            metadata.update({"receiver_type": field_types[receiver], "confidence": 0.55})
        else:
            target_qn = f"unresolved-call:{call_name}"
        result.edges.append(Edge(method_qn, target_qn, "CALLS", metadata))


def _first(pattern: re.Pattern[str], text: str) -> str | None:
    match = pattern.search(text)
    return match.group(1) if match else None


def _line(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _block_body(text: str, open_brace_offset: int) -> tuple[str, int | None]:
    depth = 0
    start = open_brace_offset + 1
    for idx in range(open_brace_offset, len(text)):
        char = text[idx]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start:idx], _line(text, idx)
    return text[start:], None


def _annotations(text: str | None) -> list[str]:
    if not text:
        return []
    return re.findall(r"@([\w.]+)", text)


def _params(text: str) -> list[tuple[str, str]]:
    params: list[tuple[str, str]] = []
    for raw in text.split(","):
        raw = raw.strip()
        if not raw:
            continue
        raw = re.sub(r"@\w+(?:\([^)]*\))?\s*", "", raw)
        parts = raw.split()
        if len(parts) >= 2:
            params.append((parts[-2], parts[-1].replace("...", "[]")))
    return params


def _split_types(text: str) -> list[str]:
    return [item.strip() for item in text.replace("\n", " ").split(",") if item.strip()]


def _java_type_qn(type_name: str, package: str, imports: list[str]) -> str:
    clean = re.sub(r"<.*>", "", type_name).strip()
    if "." in clean:
        return f"java:{clean}"
    for imported in imports:
        if imported.endswith(f".{clean}"):
            return f"java:{imported}"
    return f"java:{package}.{clean}" if package else f"java:{clean}"


def _is_injection(annotations: list[str]) -> bool:
    return any(annotation.endswith(("Autowired", "Resource", "Inject")) for annotation in annotations)


def _looks_like_service_type(type_name: str) -> bool:
    return type_name.endswith(("Service", "Manager", "Repository", "Mapper", "Client", "Producer", "Publisher"))
