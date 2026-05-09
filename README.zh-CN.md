# Code Context Agent

Code Context Agent 是一个面向 Java + Protobuf RPC 代码库的轻量级语义上下文工具。

它会把代码索引成本地 SQLite 知识图谱，然后回答普通文本搜索很难直接回答的问题：符号定位、类上下文、调用方、被调方、继承关系、Proto RPC 契约、字段变更影响分析等。

这个项目的目标不是替代 Claude Code、CodeFlicker、Codex、Cursor 等 AI 编码工具写代码，而是帮助这些 Agent 在改代码前更快、更准地理解代码库。

## Agent Skill

仓库内置了一份可安装的 skill prompt：

[skills/code-context-agent/SKILL.md](skills/code-context-agent/SKILL.md)

它描述了 Agent 什么时候应该使用图谱、如何发现 Java 仓库、以及在读源码前应该优先执行哪些 CLI 命令。

## v1 已支持能力

- 扫描 Java、Proto、Maven、Gradle、XML、YAML、properties 文件。
- 解析 `.proto` 的 package、import、message、field、enum、service、RPC method、request/response 类型。
- 解析 Java 的 class、interface、enum、field、method、annotation、import、继承、实现、注入关系和轻量方法调用。
- 解析 Maven `pom.xml` 的 module 和依赖关系。
- 使用本地 SQLite 存储代码事实图谱。
- 提供 CLI 查询能力：符号定位、类上下文、调用方、被调方、子类/实现类、RPC 解释、Proto 字段影响分析、Context Pack 生成。
- 支持安装可选的 git `post-merge` hook，在 `git pull` 后自动刷新图谱。
- 提供 Serena 可选集成入口，用于后续增强 Java 符号分析能力。

## 安装

在仓库根目录执行：

```bash
python3 -m pip install -e .
```

验证安装：

```bash
codeagent --help
```

也可以不安装，直接通过模块方式运行：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B -m codeagent.cli --help
```

## 快速开始

为一个 Java 仓库生成图谱：

```bash
JAVA_REPO=/path/to/java-repo
GRAPH_DB="$JAVA_REPO/.codeflicker/graph.sqlite"

codeagent --db "$GRAPH_DB" index "$JAVA_REPO" --clear
```

查找符号：

```bash
codeagent --db "$GRAPH_DB" find-symbol ItemExpressTagSinkTask --limit 20
```

查看一个类的整体上下文：

```bash
codeagent --db "$GRAPH_DB" class-context ItemExpressTagSinkTask --limit 20
```

查询调用方和被调方：

```bash
codeagent --db "$GRAPH_DB" find-callers ItemExpressTagSinkService --limit 50
codeagent --db "$GRAPH_DB" find-callees ItemExpressTagSinkService --limit 50
```

查询子类或实现类：

```bash
codeagent --db "$GRAPH_DB" find-subclasses AbstractSinkPipeLineService
```

解释一个 Protobuf RPC：

```bash
codeagent --db "$GRAPH_DB" explain-rpc OrderService.CreateOrder
```

分析新增 Proto 字段的影响：

```bash
codeagent --db "$GRAPH_DB" impact-add-field CreateOrderRequest coupon_id
```

为 AI 编码 Agent 生成上下文包：

```bash
codeagent --db "$GRAPH_DB" context "给订单创建请求加一个优惠券字段"
```

## IDEA Terminal 示例

当 Java 仓库已经在 IntelliJ IDEA 2024 中打开时，可以直接在 IDEA 底部 Terminal 执行：

```bash
JAVA_REPO="$(pwd)"

codeagent \
  --db "$JAVA_REPO/.codeflicker/graph.sqlite" \
  index "$JAVA_REPO" \
  --clear
```

然后不离开 IDE，直接查询图谱：

```bash
codeagent \
  --db "$JAVA_REPO/.codeflicker/graph.sqlite" \
  class-context ItemExpressTagSinkTask \
  --limit 20
```

输出结果会包含文件路径和行号，后续可以直接跳转到对应源码。

## Git Hook

为 Java 仓库安装 `post-merge` hook：

```bash
codeagent install-hook /path/to/java-repo
```

安装后，`git pull` 或 merge 操作会在后台触发图谱重建。图谱会写入：

```text
/path/to/java-repo/.codeflicker/graph.sqlite
```

## 可选 Serena 后端

Serena 可以作为可选 Java 符号后端，用于获取更强的 references、implementations、declarations、diagnostics 等信息。Code Context Agent 仍然负责 Proto/RPC 语义和 Context Pack 生成。

检查 Serena 是否可用：

```bash
codeagent serena status /path/to/java-repo
```

输出某个符号的 Serena 增强查询计划：

```bash
codeagent serena plan AddAppealRequest
```

更多设计见：[docs/serena-integration.md](docs/serena-integration.md)。

## 技术方案

MVP 技术方案文档：

[code-assistant-agent-mvp.md](code-assistant-agent-mvp.md)

## 边界

v1 版本刻意保持 Java 分析轻量化。它还不做完整 classpath 解析、精确数据流分析或动态框架解析。

低置信度调用会被保留为候选，尤其是 `unresolved-call:*`，方便后续分析器或人工读源码进一步确认。

更准确地说：

> 图谱不替代 Agent 的语义理解，但它给 Agent 提供结构化事实和导航路径，让 Agent 的理解更少依赖盲搜和猜测。
