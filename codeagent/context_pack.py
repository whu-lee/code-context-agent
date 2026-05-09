from __future__ import annotations

from .analysis import AnalysisEngine


def build_context_pack(engine: AnalysisEngine, task: str) -> str:
    terms = _terms(task)
    message = _guess_message(terms)
    rpc = _guess_rpc(terms)
    java_class = _guess_java_class(terms)

    lines = [
        "# Context Pack",
        "",
        "## User Task",
        task,
        "",
        "## Task Understanding",
        _task_understanding(task, message, rpc, java_class),
        "",
    ]

    if rpc:
        explanation = engine.explain_rpc(rpc)
        if explanation:
            lines.extend(
                [
                    "## Contract",
                    f"- RPC: `{explanation.rpc['name']}`",
                    f"- Proto node: `{explanation.rpc['qualified_name']}`",
                ]
            )
            for req in explanation.request:
                lines.append(f"- Request: `{req.get('qualified_name')}`")
            for resp in explanation.response:
                lines.append(f"- Response: `{resp.get('qualified_name')}`")
            lines.append("")

            if explanation.impl_candidates:
                lines.extend(["## Server Implementation Candidates"])
                for item in explanation.impl_candidates[:8]:
                    lines.append(_format_node(item))
                lines.append("")

    if message:
        impact = engine.impact_add_proto_field(message, _guess_field(terms))
        if impact["usage"]["messages"]:
            lines.extend(["## Proto Message Candidates"])
            for item in impact["usage"]["messages"][:8]:
                lines.append(_format_node(item))
            lines.append("")

        if impact["usage"]["java_hits"]:
            lines.extend(["## Java Usage Candidates"])
            for item in impact["usage"]["java_hits"][:12]:
                lines.append(_format_node(item))
            lines.append("")

        lines.extend(["## Risks"])
        for risk in impact["risks"]:
            lines.append(f"- {risk}")
        lines.append("")

    if java_class and not message and not rpc:
        callers = engine.find_callers(java_class)
        subclasses = engine.find_subclasses(java_class)
        call_chain = engine.trace_call_chain(java_class, depth=3)

        if call_chain:
            lines.extend(["## Call Chain"])
            for item in call_chain[:20]:
                indent = "  " * item["depth"]
                lines.append(f"{indent}- `{item['node'].get('qualified_name', '?')}`")
            lines.append("")

        if callers["callers"]:
            lines.extend(["## Callers"])
            for item in callers["callers"][:10]:
                lines.append(_format_node(item))
            lines.append("")

        if subclasses["subclasses"]:
            lines.extend(["## Subclasses / Implementations"])
            for item in subclasses["subclasses"][:10]:
                lines.append(f"- [{item.get('relation')}] `{item.get('qualified_name')}`")
            lines.append("")

    lines.extend(
        [
            "## Suggested Change Boundary",
            "- 优先修改 Proto 契约和服务端实现入口。",
            "- 如果新增字段会落库，继续检查 Entity/DO、Mapper XML、数据库字段和测试 fixture。",
            "- 如果字段影响调用方构造请求，继续检查 request builder 使用点。",
            "",
            "## Notes",
            "- This MVP context pack is based on static graph facts and lightweight heuristics.",
            "- Unresolved Java calls should be treated as candidates, not final truth.",
        ]
    )
    return "\n".join(lines)


def _terms(task: str) -> list[str]:
    cleaned = task.replace("-", " ").replace(".", " ")
    return [part for part in cleaned.split() if part]


def _guess_message(terms: list[str]) -> str | None:
    for term in terms:
        if term.endswith(("Request", "Response", "Req", "Resp")):
            return term
    return None


def _guess_rpc(terms: list[str]) -> str | None:
    for term in terms:
        if "/" in term or "." in term:
            return term
    return None


def _guess_field(terms: list[str]) -> str:
    for term in terms:
        if "_" in term or term.endswith("Id"):
            return term.strip("，。,. ")
    return ""


def _guess_java_class(terms: list[str]) -> str | None:
    for term in terms:
        if len(term) >= 4 and term[0].isupper() and not term.endswith(("Request", "Response", "Req", "Resp")):
            return term
    return None


def _task_understanding(task: str, message: str | None, rpc: str | None, java_class: str | None = None) -> str:
    if message:
        return (
            f"用户任务可能涉及修改 Proto Message `{message}`，需要检查 proto 契约、生成 Java 代码、"
            "服务端实现、调用方 request builder、兼容性风险和相关测试。"
        )
    if rpc:
        return f"用户任务可能围绕 RPC `{rpc}` 展开，需要定位 Proto 契约、Java 实现入口和主要调用链。"
    if java_class:
        return f"用户任务可能围绕 Java 类 `{java_class}` 展开，需要分析其调用链、继承关系和调用方。"
    return "用户任务需要先通过业务词匹配定位 Proto/RPC/Java 符号，再生成更精确的修改上下文。"


def _format_node(item: dict) -> str:
    loc = item.get("file_path") or "unknown"
    line = item.get("start_line")
    suffix = f":{line}" if line else ""
    return f"- `{item.get('qualified_name')}` ({loc}{suffix})"
