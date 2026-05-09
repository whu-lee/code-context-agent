---
name: code-context-agent
description: Use this skill automatically for Java/Protobuf repository understanding, impact analysis, call-chain tracing, scheduled task analysis, RPC/proto field change review, and class or method dependency analysis. When the user mentions a Java project, Java class or method, proto/RPC, callers/callees, inheritance, impact surface, or rerun/refresh impact, query or build the local codeagent graph first, then read source code precisely; do not start with broad grep.
---

# Code Context Agent

## Purpose

This skill uses Code Context Agent to query a local SQLite knowledge graph for Java + Protobuf RPC repositories.

Use it before broad grep/read workflows when analyzing Java code. The graph gives structured facts such as symbols, class members, call edges, inheritance, injection, Proto RPC contracts, and file/line evidence.

## Automatic Trigger Rules

Use this skill directly, without asking the user to name it, when the task involves any of these:

- Understanding, modifying, or reviewing a Java repository or Maven multi-module project.
- Analyzing the impact surface of a Java class, method, Service, Task, Scheduler, DAO, Manager, or Factory.
- Tracing "who calls this", "what does this call", call chains, scheduled jobs, refresh/rerun impact, or batch task impact.
- Analyzing Java + Protobuf RPCs, proto messages, or proto field changes.
- Building a context pack for Claude Code, CodeFlicker, Codex, Cursor, or another coding agent.

Example user requests:

- `Analyze ItemExpressTagSinkTask rerun impact`
- `Continue analyzing ItemExpressTagSinkService call chain`
- `What is the impact of adding coupon_id to CreateOrderRequest?`
- `Where is this RPC implemented?`
- `Which classes implement this interface?`

## Repository Discovery

If the user provides a Java repository path, use it.

If the user does not provide a path, try these sources before asking:

1. Current working directory, if it contains `pom.xml`, `build.gradle`, `settings.gradle`, or `.codeflicker/graph.sqlite`.
2. Existing graph files under common local workspace roots such as:
   - `~/IdeaProjects/*/.codeflicker/graph.sqlite`
   - `~/workspace/*/.codeflicker/graph.sqlite`
   - `~/code/*/.codeflicker/graph.sqlite`
3. For each candidate graph, run `find-symbol` against the class or method from the user request and prefer a repository that matches.

Only ask the user for the repository path after these discovery attempts fail.

## Installation Check

First check whether `codeagent` is available:

```bash
codeagent --help
```

If it is not installed, install it from the Code Context Agent repository:

```bash
cd /path/to/code-context-agent
python3 -m pip install -e .
```

If a local wrapper is preferred, it can call the module directly:

```bash
cd /path/to/code-context-agent
PYTHONDONTWRITEBYTECODE=1 python3 -B -m codeagent.cli --help
```

## Graph Path Convention

Store the graph inside the Java repository:

```text
{java_repo}/.codeflicker/graph.sqlite
```

Temporary graph files can be used for experiments, but durable project graphs should be written back to the Java repository.

## Workflow

### 1. Ensure The Graph Exists

```bash
ls {java_repo}/.codeflicker/graph.sqlite
```

If it does not exist, or if the user asks for a fresh analysis:

```bash
codeagent --db {java_repo}/.codeflicker/graph.sqlite index {java_repo} --clear
```

### 2. Query Structured Facts First

Find a symbol:

```bash
codeagent --db {java_repo}/.codeflicker/graph.sqlite find-symbol ClassName --limit 20
```

Summarize a class:

```bash
codeagent --db {java_repo}/.codeflicker/graph.sqlite class-context ClassName --limit 20
```

Trace a lightweight call chain:

```bash
codeagent --db {java_repo}/.codeflicker/graph.sqlite trace ClassName --depth 3
```

Find callers:

```bash
codeagent --db {java_repo}/.codeflicker/graph.sqlite find-callers ClassName --limit 50
```

Find callees:

```bash
codeagent --db {java_repo}/.codeflicker/graph.sqlite find-callees ClassName --limit 50
```

Find subclasses or implementations:

```bash
codeagent --db {java_repo}/.codeflicker/graph.sqlite find-subclasses AbstractClassName
```

Build a task context pack:

```bash
codeagent --db {java_repo}/.codeflicker/graph.sqlite context "natural language task"
```

Analyze a proto field addition:

```bash
codeagent --db {java_repo}/.codeflicker/graph.sqlite impact-add-field MessageName field_name
```

Explain an RPC:

```bash
codeagent --db {java_repo}/.codeflicker/graph.sqlite explain-rpc ServiceName.MethodName
```

### 3. Read Source Precisely

Use `file_path` and `start_line` from graph output to read the relevant source code. The graph is navigation and evidence; source code remains the final authority.

## Git Hook

To keep the graph fresh after `git pull`, install a post-merge hook once per Java repository:

```bash
codeagent install-hook {java_repo}
```

## Interpretation Rules

- Treat graph nodes and edges as static-analysis facts.
- Treat `CALLS` edges with `confidence < 0.5` as candidates that need source confirmation.
- Treat `unresolved-call:*` targets as useful hints, not final truth.
- Prefer graph queries to narrow the scope, then read source code for exact behavior.
