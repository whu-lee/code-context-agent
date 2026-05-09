# Code Context Agent

Code Context Agent is a lightweight semantic context tool for Java + Protobuf RPC repositories.

It indexes code into a local SQLite knowledge graph, then answers code-understanding questions that are hard to solve with plain text search: symbol lookup, class context, callers, callees, inheritance, Proto RPC contracts, and impact analysis.

The project is designed to help AI coding agents such as Claude Code, CodeFlicker, Codex, Cursor, and similar tools understand a repository before editing it.

## Agent Skill

An installable skill prompt is included at [skills/code-context-agent/SKILL.md](skills/code-context-agent/SKILL.md). It tells coding agents when to use the graph, how to discover a Java repository, and which CLI commands to run before reading source code.

## What Works In v1

- Scans Java, Proto, Maven, Gradle, XML, YAML, and properties files.
- Parses `.proto` packages, imports, messages, fields, enums, services, RPC methods, and request/response types.
- Parses Java classes, interfaces, enums, fields, methods, annotations, imports, inheritance, injection, and lightweight method calls.
- Parses Maven `pom.xml` modules and dependencies.
- Stores facts in a local SQLite graph.
- Provides CLI commands for symbol lookup, class context, callers, callees, subclasses, RPC explanation, Proto field impact, and context-pack generation.
- Installs an optional git `post-merge` hook to refresh the graph after `git pull`.
- Provides optional Serena integration planning commands for richer Java symbol analysis.

## Install

From the repository root:

```bash
python3 -m pip install -e .
```

Then verify:

```bash
codeagent --help
```

You can also run it without installation:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B -m codeagent.cli --help
```

## Quick Start

Index a Java repository:

```bash
JAVA_REPO=/path/to/java-repo
GRAPH_DB="$JAVA_REPO/.codeflicker/graph.sqlite"

codeagent --db "$GRAPH_DB" index "$JAVA_REPO" --clear
```

Find a symbol:

```bash
codeagent --db "$GRAPH_DB" find-symbol ItemExpressTagSinkTask --limit 20
```

Summarize a Java class:

```bash
codeagent --db "$GRAPH_DB" class-context ItemExpressTagSinkTask --limit 20
```

Find callers and callees:

```bash
codeagent --db "$GRAPH_DB" find-callers ItemExpressTagSinkService --limit 50
codeagent --db "$GRAPH_DB" find-callees ItemExpressTagSinkService --limit 50
```

Find subclasses or implementations:

```bash
codeagent --db "$GRAPH_DB" find-subclasses AbstractSinkPipeLineService
```

Explain a Protobuf RPC:

```bash
codeagent --db "$GRAPH_DB" explain-rpc OrderService.CreateOrder
```

Analyze a Proto field addition:

```bash
codeagent --db "$GRAPH_DB" impact-add-field CreateOrderRequest coupon_id
```

Build a context pack for an AI coding agent:

```bash
codeagent --db "$GRAPH_DB" context "给订单创建请求加一个优惠券字段"
```

## IDEA Terminal Example

When a Java repository is open in IntelliJ IDEA 2024, run this in the IDEA Terminal:

```bash
JAVA_REPO="$(pwd)"

codeagent \
  --db "$JAVA_REPO/.codeflicker/graph.sqlite" \
  index "$JAVA_REPO" \
  --clear
```

Then query the graph without leaving the IDE:

```bash
codeagent \
  --db "$JAVA_REPO/.codeflicker/graph.sqlite" \
  class-context ItemExpressTagSinkTask \
  --limit 20
```

The output includes file paths and line numbers, so the next step can jump directly to the relevant source code.

## Git Hook

Install a post-merge hook for a Java repository:

```bash
codeagent install-hook /path/to/java-repo
```

After that, `git pull` or merge operations start a background graph rebuild. The graph is written to:

```text
/path/to/java-repo/.codeflicker/graph.sqlite
```

## Optional Serena Backend

Serena can be used as an optional Java symbol backend for richer references, implementations, declarations, and diagnostics. Code Context Agent keeps ownership of Proto/RPC semantics and context-pack generation.

Check availability:

```bash
codeagent serena status /path/to/java-repo
```

Print planned enrichment queries:

```bash
codeagent serena plan AddAppealRequest
```

See [docs/serena-integration.md](docs/serena-integration.md) for details.

## Design

The MVP technical design is in [code-assistant-agent-mvp.md](code-assistant-agent-mvp.md).

## Boundaries

This v1 release intentionally keeps Java analysis lightweight. It does not perform full classpath resolution, precise data flow analysis, or dynamic framework resolution. Low-confidence calls are preserved as candidates, especially as `unresolved-call:*`, so later analyzers and human review can confirm them.
