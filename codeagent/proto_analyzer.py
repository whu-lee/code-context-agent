from __future__ import annotations

import re

from .models import AnalysisResult, Edge, Node, SourceFile


PACKAGE_RE = re.compile(r"^\s*package\s+([\w.]+)\s*;", re.MULTILINE)
IMPORT_RE = re.compile(r"^\s*import\s+(?:public\s+|weak\s+)?\"([^\"]+)\"\s*;", re.MULTILINE)
MESSAGE_RE = re.compile(r"^\s*message\s+(\w+)\s*\{", re.MULTILINE)
ENUM_RE = re.compile(r"^\s*enum\s+(\w+)\s*\{", re.MULTILINE)
SERVICE_RE = re.compile(r"^\s*service\s+(\w+)\s*\{", re.MULTILINE)
RPC_RE = re.compile(r"^\s*rpc\s+(\w+)\s*\(\s*([\w.]+)\s*\)\s*returns\s*\(\s*([\w.]+)\s*\)", re.MULTILINE)
FIELD_RE = re.compile(
    r"^\s*(?:(optional|required|repeated)\s+)?([\w.<>]+)\s+(\w+)\s*=\s*(\d+)"
    r"(?:\s*\[([^\]]+)\])?\s*;",
    re.MULTILINE,
)
RESERVED_RE = re.compile(r"^\s*reserved\s+([^;]+)\s*;", re.MULTILINE)


def analyze_proto(source: SourceFile) -> AnalysisResult:
    text = source.path.read_text(encoding="utf-8", errors="ignore")
    result = AnalysisResult()

    package = _first(PACKAGE_RE, text) or ""
    file_qn = f"proto:{source.rel_path}"
    result.nodes.append(
        Node(
            type="ProtoFile",
            name=source.path.name,
            qualified_name=file_qn,
            file_path=source.rel_path,
            metadata={"package": package, "module": source.module},
        )
    )

    if package:
        package_qn = f"proto-package:{package}"
        result.nodes.append(Node(type="ProtoPackage", name=package, qualified_name=package_qn))
        result.edges.append(Edge(file_qn, package_qn, "DECLARES_PACKAGE"))

    for imported in IMPORT_RE.findall(text):
        import_qn = f"proto:{imported}"
        result.nodes.append(Node(type="ProtoFile", name=imported.split("/")[-1], qualified_name=import_qn, file_path=imported))
        result.edges.append(Edge(file_qn, import_qn, "IMPORTS_PROTO"))

    for match in MESSAGE_RE.finditer(text):
        name = match.group(1)
        body, end_line = _block_body(text, match.end() - 1)
        message_qn = _proto_qn("message", package, name)
        result.nodes.append(
            Node(
                type="ProtoMessage",
                name=name,
                qualified_name=message_qn,
                file_path=source.rel_path,
                start_line=_line(text, match.start()),
                end_line=end_line,
                metadata={"package": package, "reserved": RESERVED_RE.findall(body)},
            )
        )
        result.edges.append(Edge(file_qn, message_qn, "DEFINES_MESSAGE"))

        for field in FIELD_RE.finditer(body):
            label, field_type, field_name, number, options = field.groups()
            field_qn = f"{message_qn}.{field_name}"
            result.nodes.append(
                Node(
                    type="ProtoField",
                    name=field_name,
                    qualified_name=field_qn,
                    file_path=source.rel_path,
                    metadata={
                        "label": label or "singular",
                        "field_type": field_type,
                        "number": int(number),
                        "options": options,
                    },
                )
            )
            result.edges.append(Edge(message_qn, field_qn, "HAS_FIELD"))

    for match in ENUM_RE.finditer(text):
        name = match.group(1)
        enum_qn = _proto_qn("enum", package, name)
        result.nodes.append(
            Node(
                type="ProtoEnum",
                name=name,
                qualified_name=enum_qn,
                file_path=source.rel_path,
                start_line=_line(text, match.start()),
            )
        )
        result.edges.append(Edge(file_qn, enum_qn, "DEFINES_ENUM"))

    for match in SERVICE_RE.finditer(text):
        name = match.group(1)
        body, end_line = _block_body(text, match.end() - 1)
        service_qn = _proto_qn("service", package, name)
        result.nodes.append(
            Node(
                type="ProtoService",
                name=name,
                qualified_name=service_qn,
                file_path=source.rel_path,
                start_line=_line(text, match.start()),
                end_line=end_line,
                metadata={"package": package},
            )
        )
        result.edges.append(Edge(file_qn, service_qn, "DEFINES_SERVICE"))

        for rpc in RPC_RE.finditer(body):
            rpc_name, request_type, response_type = rpc.groups()
            rpc_qn = f"{service_qn}.{rpc_name}"
            request_qn = _proto_qn("message", package, request_type)
            response_qn = _proto_qn("message", package, response_type)
            result.nodes.append(
                Node(
                    type="ProtoRpcMethod",
                    name=rpc_name,
                    qualified_name=rpc_qn,
                    file_path=source.rel_path,
                    metadata={"request_type": request_type, "response_type": response_type},
                )
            )
            result.edges.append(Edge(service_qn, rpc_qn, "DEFINES_RPC"))
            result.edges.append(Edge(rpc_qn, request_qn, "REQUEST_TYPE"))
            result.edges.append(Edge(rpc_qn, response_qn, "RESPONSE_TYPE"))

    return result


def _first(pattern: re.Pattern[str], text: str) -> str | None:
    match = pattern.search(text)
    return match.group(1) if match else None


def _proto_qn(kind: str, package: str, name: str) -> str:
    clean_name = name.split(".")[-1]
    return f"proto-{kind}:{package}.{clean_name}" if package else f"proto-{kind}:{clean_name}"


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
