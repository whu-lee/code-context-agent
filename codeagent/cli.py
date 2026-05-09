from __future__ import annotations

import argparse
import json
import stat
import sys
from pathlib import Path

from .analysis import AnalysisEngine
from .context_pack import build_context_pack
from .graph_store import GraphStore
from .java_analyzer import analyze_java
from .models import AnalysisResult
from .pom_analyzer import analyze_pom
from .proto_analyzer import analyze_proto
from .scanner import default_index_dir, scan_repo
from .serena_backend import enrichment_plan, serena_status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="codeagent")
    parser.add_argument("--db", help="Path to graph SQLite database")
    sub = parser.add_subparsers(dest="command", required=True)

    index_cmd = sub.add_parser("index", help="Index a Java + Proto repository")
    index_cmd.add_argument("repo", help="Repository path")
    index_cmd.add_argument("--clear", action="store_true", help="Clear existing graph before indexing")

    explain_cmd = sub.add_parser("explain-rpc", help="Explain a proto RPC")
    explain_cmd.add_argument("rpc")

    msg_cmd = sub.add_parser("find-message", help="Find proto message usage")
    msg_cmd.add_argument("message")

    impact_cmd = sub.add_parser("impact-add-field", help="Analyze impact of adding a proto field")
    impact_cmd.add_argument("message")
    impact_cmd.add_argument("field")

    trace_cmd = sub.add_parser("trace", help="Trace simple Java call chain")
    trace_cmd.add_argument("symbol")
    trace_cmd.add_argument("--depth", type=int, default=3)

    symbol_cmd = sub.add_parser("find-symbol", help="Find graph nodes by class, method, field, proto, or file name")
    symbol_cmd.add_argument("symbol")
    symbol_cmd.add_argument("--limit", type=int, default=20)

    class_cmd = sub.add_parser("class-context", help="Summarize a Java class with methods, fields, hierarchy, callers, and callees")
    class_cmd.add_argument("symbol")
    class_cmd.add_argument("--limit", type=int, default=20)

    callers_cmd = sub.add_parser("find-callers", help="Find callers of a Java class or method")
    callers_cmd.add_argument("symbol")
    callers_cmd.add_argument("--limit", type=int, default=50)

    callees_cmd = sub.add_parser("find-callees", help="Find calls made by a Java class or method")
    callees_cmd.add_argument("symbol")
    callees_cmd.add_argument("--limit", type=int, default=50)

    subclasses_cmd = sub.add_parser("find-subclasses", help="Find subclasses/implementations of a Java class or interface")
    subclasses_cmd.add_argument("symbol")

    context_cmd = sub.add_parser("context", help="Build a Markdown context pack")
    context_cmd.add_argument("task")

    hook_cmd = sub.add_parser("install-hook", help="Install git post-merge hook to auto-reindex after git pull")
    hook_cmd.add_argument("repo", help="Repository path")

    serena_cmd = sub.add_parser("serena", help="Inspect optional Serena integration")
    serena_sub = serena_cmd.add_subparsers(dest="serena_command", required=True)
    serena_status_cmd = serena_sub.add_parser("status", help="Show Serena availability and start command")
    serena_status_cmd.add_argument("repo", help="Repository path")
    serena_status_cmd.add_argument("--context", default="claude-code", help="Serena context name")
    serena_plan_cmd = serena_sub.add_parser("plan", help="Show planned Serena queries for a symbol")
    serena_plan_cmd.add_argument("symbol")

    args = parser.parse_args(argv)

    if args.command == "serena":
        if args.serena_command == "status":
            print_json(serena_status(Path(args.repo), context=args.context).as_dict())
        elif args.serena_command == "plan":
            print_json(enrichment_plan(args.symbol))
        return 0

    if args.command == "install-hook":
        return _install_hook(Path(args.repo).resolve())

    repo = Path(getattr(args, "repo", ".")).resolve()
    db_path = Path(args.db).expanduser() if args.db else default_index_dir(repo) / "graph.sqlite"
    store = GraphStore(db_path)
    try:
        if args.command == "index":
            return _index(args, store)

        engine = AnalysisEngine(store)
        if args.command == "explain-rpc":
            print_json(engine.explain_rpc(args.rpc))
        elif args.command == "find-message":
            print_json(engine.find_message_usage(args.message))
        elif args.command == "impact-add-field":
            print_json(engine.impact_add_proto_field(args.message, args.field))
        elif args.command == "trace":
            print_json(engine.trace_call_chain(args.symbol, args.depth))
        elif args.command == "find-symbol":
            print_json(engine.find_symbol(args.symbol, args.limit))
        elif args.command == "class-context":
            print_json(engine.class_context(args.symbol, args.limit))
        elif args.command == "find-callers":
            print_json(engine.find_callers(args.symbol, args.limit))
        elif args.command == "find-callees":
            print_json(engine.find_callees(args.symbol, args.limit))
        elif args.command == "find-subclasses":
            print_json(engine.find_subclasses(args.symbol))
        elif args.command == "context":
            print(build_context_pack(engine, args.task))
        return 0
    finally:
        store.close()


def _index(args, store: GraphStore) -> int:
    repo = Path(args.repo).resolve()
    files = scan_repo(repo)
    if args.clear:
        store.clear()
    store.upsert_files(files)

    result = AnalysisResult()
    for source in files:
        if source.language == "proto":
            result.extend(analyze_proto(source))
        elif source.language == "java":
            result.extend(analyze_java(source))
        elif source.language == "maven":
            result.extend(analyze_pom(source))

    store.upsert_result(result)
    stats = store.stats()
    print(f"Indexed {stats['files']} files, {stats['nodes']} nodes, {stats['edges']} edges")
    print(f"Graph DB: {store.db_path}")
    return 0


def _install_hook(repo: Path) -> int:
    git_dir = repo / ".git"
    if not git_dir.is_dir():
        print(f"Error: {repo} is not a git repository", file=sys.stderr)
        return 1

    codeagent_pkg = Path(__file__).resolve().parent.parent
    db_path = repo / ".codeflicker" / "graph.sqlite"
    log_path = repo / ".codeflicker" / "index.log"
    meta_path = repo / ".codeflicker" / "index.meta"

    hook_content = f"""#!/bin/sh
# auto-generated by codeagent install-hook
REPO_DIR=$(git rev-parse --show-toplevel)
COMMIT=$(git rev-parse HEAD)
mkdir -p "$REPO_DIR/.codeflicker"
(
  cd "{codeagent_pkg}" && \\
  PYTHONDONTWRITEBYTECODE=1 python3 -B -m codeagent.cli \\
    --db "{db_path}" \\
    index "$REPO_DIR" --clear >> "{log_path}" 2>&1 && \\
  python3 -c "import json,time; open('{meta_path}','w').write(json.dumps({{'commit':'$COMMIT','indexed_at':time.strftime('%Y-%m-%dT%H:%M:%S')}}))"
) &
echo "[codeagent] Graph reindex started in background (log: {log_path})"
"""

    hook_path = git_dir / "hooks" / "post-merge"
    existing = hook_path.read_text() if hook_path.exists() else ""
    if "codeagent" in existing:
        print(f"Hook already installed at {hook_path}")
        return 0

    if existing:
        hook_path.write_text(existing.rstrip() + "\n\n" + hook_content)
    else:
        hook_path.write_text(hook_content)

    hook_path.chmod(hook_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"Hook installed: {hook_path}")
    print(f"Graph will be saved to: {db_path}")
    print("Run 'git pull' to trigger the first reindex, or run 'index' manually.")
    return 0


def print_json(value) -> None:
    if hasattr(value, "__dict__"):
        value = value.__dict__
    print(json.dumps(value, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    raise SystemExit(main())
