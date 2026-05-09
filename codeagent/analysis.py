from __future__ import annotations

import json
from dataclasses import dataclass

from .graph_store import GraphStore


@dataclass
class RpcExplanation:
    rpc: dict
    request: list[dict]
    response: list[dict]
    impl_candidates: list[dict]


class AnalysisEngine:
    def __init__(self, store: GraphStore):
        self.store = store

    def explain_rpc(self, rpc_name: str) -> RpcExplanation | None:
        service, method = _split_rpc(rpc_name)
        candidates = self.store.find_nodes(method, ("ProtoRpcMethod",))
        if service:
            candidates = [c for c in candidates if f".{service}." in c["qualified_name"] or c["qualified_name"].endswith(f"{service}.{method}")]
        if not candidates:
            return None

        rpc = candidates[0]
        request = self._edge_nodes(rpc["qualified_name"], "REQUEST_TYPE")
        response = self._edge_nodes(rpc["qualified_name"], "RESPONSE_TYPE")
        impl_candidates = self._find_java_impl_candidates(method)
        return RpcExplanation(_row(rpc), request, response, impl_candidates)

    def find_message_usage(self, message: str) -> dict:
        messages = self.store.find_nodes(message, ("ProtoMessage",))
        java_hits = self.store.find_nodes(message, ("JavaFile", "JavaClass", "JavaMethod", "JavaField"))
        return {"messages": [_row(item) for item in messages], "java_hits": [_row(item) for item in java_hits]}

    def impact_add_proto_field(self, message: str, field: str) -> dict:
        usage = self.find_message_usage(message)
        risks = [
            "不要复用已经删除或 reserved 的 proto field number。",
            "新增字段应兼容老客户端缺省不传的情况。",
            "需要刷新生成的 Java 代码。",
            "需要检查 request builder、测试 fixture、mock 数据是否要补字段。",
        ]
        if field:
            risks.append(f"如果 {field} 需要持久化，需要检查 Mapper XML、Entity/DO 和数据库字段。")
        return {"message": message, "field": field, "usage": usage, "risks": risks}

    def find_symbol(self, symbol: str, limit: int = 20) -> dict:
        matches = self._resolve_symbols(
            symbol,
            (
                "JavaClass",
                "JavaInterface",
                "JavaEnum",
                "JavaMethod",
                "JavaField",
                "ProtoService",
                "ProtoRpcMethod",
                "ProtoMessage",
                "ProtoField",
                "MavenModule",
                "JavaFile",
                "ProtoFile",
            ),
            limit,
        )
        return {"symbol": symbol, "matches": matches}

    def class_context(self, symbol: str, limit: int = 20) -> dict:
        hits = self.store.find_nodes(symbol, ("JavaClass", "JavaInterface", "JavaEnum"))
        if not hits:
            return {"symbol": symbol, "class": None, "matches": self.find_symbol(symbol, limit)["matches"]}

        cls = hits[0]
        class_qn = cls["qualified_name"]
        members = self._contained_nodes(class_qn)
        methods = [item for item in members if item.get("type") == "JavaMethod"]
        fields = [item for item in members if item.get("type") == "JavaField"]

        outgoing_calls = self._calls_from([item["qualified_name"] for item in methods], limit)
        incoming_callers = self._callers_of([item["qualified_name"] for item in methods], limit)

        parents = []
        for edge_type in ("EXTENDS", "IMPLEMENTS"):
            for edge in self.store.out_edges(class_qn, edge_type):
                node = self.store.get_node(edge["to_qn"])
                parents.append({"relation": edge_type, **(_row(node) if node else {"qualified_name": edge["to_qn"]})})

        children = []
        for edge_type in ("EXTENDS", "IMPLEMENTS"):
            for edge in self.store.in_edges(class_qn, edge_type):
                node = self.store.get_node(edge["from_qn"])
                children.append({"relation": edge_type, **(_row(node) if node else {"qualified_name": edge["from_qn"]})})

        injections = []
        for edge in self.store.out_edges(class_qn, "INJECTS"):
            node = self.store.get_node(edge["to_qn"])
            injections.append({"edge": _edge_row(edge), "target": _row(node) if node else {"qualified_name": edge["to_qn"]}})

        return {
            "symbol": symbol,
            "class": _row(cls),
            "fields": fields[:limit],
            "methods": methods[:limit],
            "parents": parents[:limit],
            "children": children[:limit],
            "injections": injections[:limit],
            "callers": incoming_callers,
            "callees": outgoing_calls,
        }

    def trace_call_chain(self, symbol: str, depth: int = 3) -> list[dict]:
        starts = self.store.find_nodes(symbol, ("JavaMethod",))
        if not starts:
            class_hits = self.store.find_nodes(symbol, ("JavaClass", "JavaInterface", "JavaEnum"))
            if class_hits:
                method_starts = []
                for cls in class_hits[:3]:
                    for edge in self.store.out_edges(cls["qualified_name"], "CONTAINS"):
                        node = self.store.get_node(edge["to_qn"])
                        if node and node["type"] == "JavaMethod":
                            method_starts.append(node)
                starts = method_starts
        if not starts:
            return []
        result: list[dict] = []
        queue: list[tuple[str, int]] = [(s["qualified_name"], 0) for s in starts[:5]]
        seen: set[str] = set()
        while queue:
            current, level = queue.pop(0)
            if current in seen or level > depth:
                continue
            seen.add(current)
            node = self.store.get_node(current)
            result.append({"depth": level, "node": _row(node) if node else {"qualified_name": current}})
            for edge in self.store.out_edges(current, "CALLS"):
                queue.append((edge["to_qn"], level + 1))
        return result

    def find_callers(self, symbol: str, limit: int = 50) -> dict:
        hits = self.store.find_nodes(symbol, ("JavaMethod", "JavaClass", "JavaInterface", "JavaEnum"))
        targets = self._callable_qns(hits)

        class_like_hit = any(hit["type"] in {"JavaClass", "JavaInterface", "JavaEnum"} for hit in hits)
        if not class_like_hit:
            unresolved_names = {symbol}
            for hit in hits:
                if hit["type"] == "JavaMethod":
                    unresolved_names.add(hit["name"])
            for name in unresolved_names:
                targets.append(f"unresolved-call:{_method_name(name)}")

        return {"symbol": symbol, "matches": [_row(item) for item in hits[:10]], "callers": self._callers_of(targets, limit)}

    def find_callees(self, symbol: str, limit: int = 50) -> dict:
        hits = self.store.find_nodes(symbol, ("JavaMethod", "JavaClass", "JavaInterface", "JavaEnum"))
        sources = self._callable_qns(hits)
        return {"symbol": symbol, "matches": [_row(item) for item in hits[:10]], "callees": self._calls_from(sources, limit)}

    def find_subclasses(self, symbol: str) -> dict:
        hits = self.store.find_nodes(symbol, ("JavaClass", "JavaInterface"))
        results = []
        for node in hits[:5]:
            qn = node["qualified_name"]
            for edge_type in ("EXTENDS", "IMPLEMENTS"):
                in_edges = self.store.in_edges(qn, edge_type)
                for edge in in_edges:
                    child = self.store.get_node(edge["from_qn"])
                    results.append({
                        "relation": edge_type,
                        **((_row(child)) if child else {"qualified_name": edge["from_qn"]}),
                    })
        return {"symbol": symbol, "subclasses": results}

    def related_tests(self, symbol: str) -> list[dict]:
        stem = symbol.split("#", 1)[0].split(".")[-1].replace("Impl", "")
        return [_row(item) for item in self.store.find_nodes(f"{stem}Test", ("JavaClass", "JavaFile"))]

    def _resolve_symbols(self, symbol: str, types: tuple[str, ...], limit: int) -> list[dict]:
        rows = [_row(item) for item in self.store.find_nodes(symbol, types)]
        return _dedupe_rows(rows)[:limit]

    def _contained_nodes(self, class_qn: str) -> list[dict]:
        rows = []
        for edge in self.store.out_edges(class_qn, "CONTAINS"):
            node = self.store.get_node(edge["to_qn"])
            if node:
                rows.append(_row(node))
        rows.sort(key=lambda item: (item.get("start_line") or 0, item.get("type") or "", item.get("name") or ""))
        return rows

    def _callable_qns(self, hits) -> list[str]:
        qns: list[str] = []
        for node in hits[:10]:
            if node["type"] == "JavaMethod":
                qns.append(node["qualified_name"])
            elif node["type"] in {"JavaClass", "JavaInterface", "JavaEnum"}:
                for edge in self.store.out_edges(node["qualified_name"], "CONTAINS"):
                    member = self.store.get_node(edge["to_qn"])
                    if member and member["type"] == "JavaMethod":
                        qns.append(member["qualified_name"])
        return _dedupe_values(qns)

    def _callers_of(self, target_qns: list[str], limit: int) -> list[dict]:
        rows = []
        for qn in _dedupe_values(target_qns):
            for edge in self.store.in_edges(qn, "CALLS"):
                caller = self.store.get_node(edge["from_qn"])
                rows.append({
                    "edge": _edge_row(edge),
                    "caller": _row(caller) if caller else {"qualified_name": edge["from_qn"]},
                })
        return _dedupe_edge_rows(rows, "caller")[:limit]

    def _calls_from(self, source_qns: list[str], limit: int) -> list[dict]:
        rows = []
        for qn in _dedupe_values(source_qns):
            source = self.store.get_node(qn)
            for edge in self.store.out_edges(qn, "CALLS"):
                callee = self.store.get_node(edge["to_qn"])
                rows.append({
                    "edge": _edge_row(edge),
                    "source": _row(source) if source else {"qualified_name": qn},
                    "callee": _row(callee) if callee else {"qualified_name": edge["to_qn"], "type": "Unresolved"},
                })
        return _dedupe_edge_rows(rows, "callee")[:limit]

    def _edge_nodes(self, from_qn: str, edge_type: str) -> list[dict]:
        rows = []
        for edge in self.store.out_edges(from_qn, edge_type):
            node = self.store.get_node(edge["to_qn"])
            rows.append(_row(node) if node else {"qualified_name": edge["to_qn"], "type": "Unresolved"})
        return rows

    def _find_java_impl_candidates(self, method: str) -> list[dict]:
        candidates = self.store.find_nodes(method, ("JavaMethod",))
        return [_row(item) for item in candidates[:10]]


def _split_rpc(value: str) -> tuple[str | None, str]:
    if "." in value:
        service, method = value.rsplit(".", 1)
        return service, method
    if "/" in value:
        service, method = value.rsplit("/", 1)
        return service, method
    return None, value


def _row(row) -> dict:
    if row is None:
        return {}
    data = dict(row)
    if "metadata" in data:
        data["metadata"] = json.loads(data["metadata"] or "{}")
    return data


def _edge_row(row) -> dict:
    data = dict(row)
    if "metadata" in data:
        data["metadata"] = json.loads(data["metadata"] or "{}")
    return data


def _dedupe_values(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _dedupe_rows(rows: list[dict]) -> list[dict]:
    seen: set[str] = set()
    result = []
    for item in rows:
        key = item.get("qualified_name")
        if key and key not in seen:
            seen.add(key)
            result.append(item)
    return result


def _dedupe_edge_rows(rows: list[dict], node_key: str) -> list[dict]:
    seen: set[tuple[str, str, str]] = set()
    result = []
    for item in rows:
        node = item.get(node_key) or {}
        edge = item.get("edge") or {}
        key = (edge.get("from_qn") or "", edge.get("to_qn") or "", node.get("qualified_name") or "")
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def _method_name(value: str) -> str:
    if "#" in value:
        value = value.split("#", 1)[1]
    if "(" in value:
        value = value.split("(", 1)[0]
    if "." in value:
        value = value.rsplit(".", 1)[-1]
    return value
