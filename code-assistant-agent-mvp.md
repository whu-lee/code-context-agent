# Code Context Agent MVP 技术方案

## 1. 项目定位

Code Context Agent 是一个面向 Java + Protobuf RPC 代码库的语义上下文助手。它不替代 Claude Code、CodeFlicker、Cursor 写代码，而是为这些 AI 编码助手提供结构化、长期化、可查询的代码库理解能力。

一句话定位：

> 给 AI 编码助手装一个 Java + Protobuf 代码库大脑。

当前 MVP 的重点不是“自动改代码”，而是在改代码前把事实找准：

- Java 类、方法、字段、继承、实现、注入关系。
- 方法级调用关系，包括已解析调用和低置信度 unresolved call 候选。
- Proto package、message、field、service、RPC、request/response 类型。
- Maven module 和模块依赖。
- 可交给 Claude Code / CodeFlicker 使用的结构化上下文包。

## 2. 与 Claude Code / CodeFlicker 的关系

Claude Code / CodeFlicker 更擅长交互、推理、读写文件和执行修改；Code Context Agent 更擅长沉淀代码事实和图谱查询。

二者关系是协作而不是替代：

- Claude Code / CodeFlicker 负责理解用户意图、组织分析过程、最后修改代码。
- Code Context Agent 负责提供图谱事实：符号在哪、谁调用谁、谁继承谁、RPC 对应什么 request/response。
- 对 Java + Protobuf 任务，AI 编码助手应先查图谱，再精准读源码，而不是一开始全库 grep。

典型协作方式：

```text
用户问题
  -> CodeFlicker 自动触发 code-context-agent skill
  -> codeagent 查询或生成仓库图谱
  -> 返回 class-context / callers / callees / proto impact
  -> CodeFlicker 根据文件路径和行号精准 read 源码
  -> 形成影响分析或交给 Claude Code 修改
```

## 3. 当前 MVP 已落地能力

当前项目路径：

```text
/Users/lishishun/Documents/New project
```

当前 CLI wrapper：

```text
/Users/lishishun/.codeflicker/bin/codeagent
```

当前 CodeFlicker skill：

```text
/Users/lishishun/.codeflicker/skills/code-context-agent/SKILL.md
```

当前已实现能力：

- 扫描 Java / Proto / Maven / Gradle / XML / YAML / properties 文件。
- 解析 Proto 文件，建立 service、rpc、message、field、request、response 关系。
- 解析 Java 文件，建立 class、interface、enum、field、method、annotation、import、extends、implements、injects、calls 关系。
- 解析 Maven `pom.xml`，建立 MavenModule、CHILD_OF、INCLUDES_MODULE、DEPENDS_ON 关系。
- 使用 SQLite 存储本地图谱。
- 提供 CLI 查询能力：符号定位、类上下文、调用方、被调方、继承实现、Proto 影响分析、Context Pack。
- 提供 CodeFlicker skill 自动触发规则。
- 提供 git `post-merge` hook，支持 `git pull` 后后台刷新图谱。
- 提供 Serena 可选集成入口，但当前不把 Serena 源码嵌入项目。

## 4. 当前架构

```text
Java / Proto 仓库
  -> Repository Scanner
  -> Proto Analyzer
  -> Java Analyzer
  -> Maven / Pom Analyzer
  -> Knowledge Graph Store(SQLite)
  -> Analysis Engine
  -> Context Pack Generator
  -> CLI
  -> CodeFlicker Skill / Claude Code / Codex

可选增强：
  -> Serena Backend(符号级 Java 能力)
```

当前 MVP 采用“轻量静态分析 + 图谱查询”的路线，不依赖本地 PostgreSQL，也不要求用户安装 Neo4j。SQLite 图谱默认放在被分析 Java 仓库下：

```text
{java_repo}/.codeflicker/graph.sqlite
```

如果 CLI 显式传入 `--db /private/tmp/xxx.sqlite`，图谱就会写到显式路径；正式约定是写回 Java 项目的 `.codeflicker/graph.sqlite`。

## 5. 核心模块设计

### 5.1 Repository Scanner

负责扫描仓库结构并识别文件类型。

当前识别：

- Java 文件。
- Proto 文件。
- Maven `pom.xml`。
- Gradle 文件。
- XML / YAML / properties 配置文件。

输出：

- `SourceFile`
- 相对路径
- language
- module
- sha256

后续增强：

- 增量扫描，只重建变更文件。
- 更准确识别 source root / test root / resource root。

### 5.2 Proto Analyzer

Proto 是 RPC 代码库的一等入口。

当前解析：

- `package`
- `import`
- `message`
- `field`
- `enum`
- `service`
- `rpc`
- request / response type

当前图谱节点：

- `ProtoFile`
- `ProtoPackage`
- `ProtoMessage`
- `ProtoField`
- `ProtoEnum`
- `ProtoService`
- `ProtoRpcMethod`

当前图谱关系：

- `IMPORTS_PROTO`
- `DEFINES_PACKAGE`
- `DEFINES_MESSAGE`
- `DEFINES_ENUM`
- `DEFINES_SERVICE`
- `DEFINES_RPC`
- `REQUEST_TYPE`
- `RESPONSE_TYPE`
- `HAS_FIELD`

### 5.3 Java Analyzer

当前 Java Analyzer 采用轻量静态解析，优先满足 MVP 的图谱事实沉淀。

当前解析：

- class / interface / enum
- method / field
- annotation
- import
- extends / implements
- field injection / constructor injection
- method call

当前图谱节点：

- `JavaFile`
- `JavaClass`
- `JavaInterface`
- `JavaEnum`
- `JavaMethod`
- `JavaField`

当前图谱关系：

- `DECLARES`
- `CONTAINS`
- `EXTENDS`
- `IMPLEMENTS`
- `INJECTS`
- `CALLS`

调用边说明：

- 能根据 receiver field type 推断的调用，会生成类似 `java:xxx.Service#method(*)` 的目标。
- 无法解析的调用会保留为 `unresolved-call:methodName`，并带低置信度 metadata。
- `confidence < 0.5` 的调用只能作为候选，需要结合源码确认。

下一阶段增强：

- 引入 JavaParser + Symbol Solver 或 Eclipse JDT，提升类型解析准确率。
- 识别同类内方法调用，将 `unresolved-call:buildXxx` 解析到当前类方法。
- 识别 Lombok、泛型、静态方法、构造器调用。
- 识别测试类和被测类关系。

### 5.4 Maven / Pom Analyzer

当前已经解析 Maven module 和依赖。

当前节点：

- `MavenModule`

当前关系：

- `CHILD_OF`
- `INCLUDES_MODULE`
- `DEPENDS_ON`

价值：

- 帮助判断代码属于哪个 Maven 模块。
- 分析模块依赖边界。
- 后续支持“改这个类可能影响哪些模块”。

### 5.5 Knowledge Graph Store

当前使用 SQLite，原因是：

- 本地零运维，不要求安装数据库服务。
- 单仓库图谱规模可控。
- 便于 CodeFlicker / Claude Code 通过 CLI 直接使用。
- 后续可以迁移到 PostgreSQL 或图数据库，但 MVP 不提前引入复杂依赖。

核心表：

```text
files(path, language, sha256, module, updated_at)
nodes(id, type, name, qualified_name, file_path, start_line, end_line, metadata)
edges(id, from_qn, to_qn, type, metadata)
```

图谱路径约定：

```text
{java_repo}/.codeflicker/graph.sqlite
```

临时兼容：

```text
/private/tmp/*codeagent*.sqlite
```

临时路径只作为旧图谱 fallback，新图谱应写回 Java 仓库。

### 5.6 Analysis Engine

Analysis Engine 是把底层图谱变成可用分析能力的核心层。

当前 CLI 能力：

```bash
codeagent index <java_repo> --clear
codeagent find-symbol <symbol> --limit 20
codeagent class-context <class> --limit 20
codeagent find-callers <class_or_method> --limit 50
codeagent find-callees <class_or_method> --limit 50
codeagent find-subclasses <class_or_interface>
codeagent trace <symbol> --depth 3
codeagent explain-rpc <Service.Method>
codeagent find-message <ProtoMessage>
codeagent impact-add-field <ProtoMessage> <field_name>
codeagent context "<自然语言任务>"
codeagent install-hook <java_repo>
codeagent serena status <java_repo>
codeagent serena plan <symbol>
```

其中最重要的是：

- `find-symbol`：先确认符号是否命中图谱。
- `class-context`：一次返回类、字段、方法、父类/接口、子类、注入依赖、调用方、被调方。
- `find-callers`：查某类/方法的调用方。
- `find-callees`：查某类/方法调用了谁。
- `find-subclasses`：查继承/实现关系。

这次迭代的重点，就是把原本需要直接 SQL 查图谱的能力产品化成 CLI。

### 5.7 Context Pack Generator

Context Pack 的目标不是把所有代码塞给 AI，而是生成一份刚好够用、结构化、带证据的任务上下文。

输入：

```text
分析 ItemExpressTagSinkTask 重刷影响
```

输出应包含：

- 任务理解。
- 关键符号。
- 图谱命中情况。
- 相关类和方法。
- 调用方 / 被调方。
- 继承和实现关系。
- 相关文件路径与行号。
- 风险点。
- 后续需要读源码确认的位置。

任务理解原则：

- LLM 负责自然语言理解和摘要。
- 图谱负责事实和关系。
- 规则负责工程经验和风险识别。
- 所有结论都应能追溯到文件路径和符号证据。

## 6. CodeFlicker Skill 集成

当前已安装 CodeFlicker skill：

```text
/Users/lishishun/.codeflicker/skills/code-context-agent/SKILL.md
/Users/lishishun/.codeflicker/skills/code-context-agent/skill.json
```

自动触发场景：

- 分析、修改、理解 Java 仓库或 Maven 多模块项目。
- 分析 Java 类、方法、Service、Task、Scheduler、DAO、Manager、Factory 的影响面。
- 分析“重刷影响”“定时任务影响”“调用链”“谁调用了它”“它调用了谁”。
- 分析 Java + Protobuf RPC、proto message、proto field 变更。
- 需要给 Claude Code / CodeFlicker / Codex 生成任务上下文包。

用户不需要显式说“使用 code-context-agent”。例如：

```text
分析 ItemExpressTagSinkTask 重刷影响
继续分析 ItemExpressTagSinkService 的调用链
给 AddAppealRequest 加字段有什么影响
这个 RPC 的实现在哪里
这个类有哪些子类/实现类
```

Skill 默认策略：

1. 如果用户给了 Java 仓库路径，使用该路径。
2. 如果当前目录是 Java 仓库，使用当前目录。
3. 如果没给路径，先尝试已知常用仓库：
   - `/Users/lishishun/IdeaProjects/kwaishop-apollo-pinocchio-center`
   - `/Users/lishishun/IdeaProjects/kwaishop-themis-rightprotect-center`
4. 查找 `/Users/lishishun/IdeaProjects/*/.codeflicker/graph.sqlite`，优先使用能 `find-symbol` 命中目标类的仓库。
5. 只有全部失败后，才询问用户 Java 仓库路径。

## 7. 启动与使用方式

推荐通过 wrapper 使用：

```bash
~/.codeflicker/bin/codeagent --help
```

为 Java 仓库生成图谱：

```bash
JAVA_REPO=/Users/lishishun/IdeaProjects/kwaishop-apollo-pinocchio-center

~/.codeflicker/bin/codeagent \
  --db "$JAVA_REPO/.codeflicker/graph.sqlite" \
  index "$JAVA_REPO" \
  --clear
```

查询类上下文：

```bash
~/.codeflicker/bin/codeagent \
  --db "$JAVA_REPO/.codeflicker/graph.sqlite" \
  class-context ItemExpressTagSinkTask \
  --limit 20
```

查询被调方：

```bash
~/.codeflicker/bin/codeagent \
  --db "$JAVA_REPO/.codeflicker/graph.sqlite" \
  find-callees ItemExpressTagSinkService \
  --limit 50
```

查询继承关系：

```bash
~/.codeflicker/bin/codeagent \
  --db "$JAVA_REPO/.codeflicker/graph.sqlite" \
  find-subclasses AbstractSinkPipeLineService
```

### 7.1 IDEA 2024 控制台调用用例

在 IDEA 2024 中打开 Java 项目后，可以直接使用底部 Terminal 控制台调用 `codeagent`。这种方式适合研发在看代码时临时生成图谱、补充调用链事实，结果仍然写回当前 Java 项目的 `.codeflicker/graph.sqlite`。

前提：

- IDEA 2024 打开的项目是目标 Java 仓库。
- Terminal 当前目录在 Java 仓库根目录，能看到 `pom.xml` 或多模块根 `pom.xml`。
- 本机已存在 wrapper：`~/.codeflicker/bin/codeagent`。

在 IDEA Terminal 中执行：

```bash
JAVA_REPO="$(pwd)"

~/.codeflicker/bin/codeagent \
  --db "$JAVA_REPO/.codeflicker/graph.sqlite" \
  index "$JAVA_REPO" \
  --clear
```

分析 `ItemExpressTagSinkTask` 重刷影响：

```bash
~/.codeflicker/bin/codeagent \
  --db "$JAVA_REPO/.codeflicker/graph.sqlite" \
  class-context ItemExpressTagSinkTask \
  --limit 20
```

继续查看核心 Sink Service 调用了哪些下游：

```bash
~/.codeflicker/bin/codeagent \
  --db "$JAVA_REPO/.codeflicker/graph.sqlite" \
  find-callees ItemExpressTagSinkService \
  --limit 50
```

查看同一抽象管线下的兄弟实现：

```bash
~/.codeflicker/bin/codeagent \
  --db "$JAVA_REPO/.codeflicker/graph.sqlite" \
  find-subclasses AbstractSinkPipeLineService
```

这个用例的价值：

- 不需要离开 IDEA，即可快速生成或刷新图谱。
- 图谱结果包含 `file_path` 和 `start_line`，可以回到 IDEA 中直接打开对应源码。
- 控制台命令可复制给 CodeFlicker / Claude Code，作为后续分析的结构化证据。
- 对“重刷影响”“定时任务影响”“调用链梳理”这类问题，比直接全库 grep 更适合作为第一步。

## 8. Git Hook 自动刷新图谱

`install-hook` 用于在被分析 Java 仓库安装 `post-merge` hook。

目标：

- 每次 `git pull` / merge 后，后台自动重建最新图谱。
- 图谱写入 `{java_repo}/.codeflicker/graph.sqlite`。
- 日志写入 `{java_repo}/.codeflicker/index.log`。
- 元信息写入 `{java_repo}/.codeflicker/index.meta`。

安装：

```bash
~/.codeflicker/bin/codeagent install-hook /path/to/java_repo
```

注意：

- hook 是保持图谱新鲜的机制，不是用户每次手动分析的必需步骤。
- 如果已有 hook，当前实现会追加 codeagent hook，不覆盖原内容。

## 9. Serena 集成定位

Serena 是一个开源代码语义工具，可以作为 Java 符号分析增强后端。

当前策略：

- 不 vendor Serena 源码。
- 不把 Serena 变成主存储。
- 保留 `serena status` 和 `serena plan` 入口。
- 后续在本项目中把 Serena 作为可选 backend，用来增强 references、implementations、declarations、diagnostics。

分工：

- Serena：增强 Java symbol-level 语义能力。
- Code Context Agent：保留 Proto/RPC、Context Pack、CodeFlicker skill、组织内 Java + Protobuf 规则。

## 10. 当前真实验证结果

在 `kwaishop-themis-rightprotect-center` 上已验证：

```text
Indexed 625 files, 9394 nodes, 23224 edges
```

在 `kwaishop-apollo-pinocchio-center` 的旧图谱上已验证：

```text
JavaClass / JavaMethod / JavaField / ProtoMessage / ProtoRpcMethod 节点可查询
CALLS / EXTENDS / IMPLEMENTS / INJECTS / CONTAINS 边可查询
ItemExpressTagSinkTask 可通过 find-symbol 和 class-context 命中
AbstractSinkPipeLineService 可通过 find-subclasses 查到 ItemExpressTagSinkService 等子类
ItemExpressTagSinkService 可通过 find-callees 查到 DAO、KConf、Redis、IC service 等候选调用
```

这说明底层图谱已经具备价值；本次迭代把直接 SQL 查询沉淀为 CLI 能力，降低 CodeFlicker 使用成本。

## 11. MVP 边界

当前不承诺：

- 100% 精准解析所有 Java 动态调用。
- 替代 IDEA / LSP。
- 完整数据流分析。
- 完整跨仓库追踪。
- 自动代码修改。
- Web 图谱 UI。
- 组织级权限和治理。

当前 CALLS 边仍有启发式成分：

- `confidence >= 0.5`：较可靠候选。
- `confidence < 0.5`：低置信度候选，需要读源码确认。
- `unresolved-call:*`：未解析调用，保留是为了不丢信息。

## 12. 下一阶段路线

### Phase 1：图谱质量增强

- 解析同类方法调用，减少 `unresolved-call`。
- 改进字段类型识别，避免 `return` 这类误识别。
- 识别静态方法、构造器、lambda、方法引用。
- 增强调用边 metadata：receiver、receiver_type、confidence、source_line。

### Phase 2：Java 语义后端增强

- 评估 JavaParser + Symbol Solver、Eclipse JDT、Spoon、Serena 的组合。
- 对常用内部框架建立解析规则。
- 提升 Spring Bean、接口实现、泛型和多模块 classpath 解析能力。

### Phase 3：框架与基础设施语义

- MyBatis Mapper XML -> Mapper interface -> SQL statement -> table。
- KConf / config key 使用关系。
- MQ producer / consumer。
- Redis key / cache 访问。
- Scheduler / Task 入口。

### Phase 4：Context Pack 产品化

- 输出 Markdown + JSON 两种格式。
- 引入上下文预算裁剪。
- 给 Claude Code / CodeFlicker 提供“先查图谱，再读源码，再总结风险”的标准流程。
- 支持影响分析模板，例如“重刷影响”“新增 proto 字段”“修改 RPC request”“改 DAO 字段”。

### Phase 5：服务化集成

- 在 CLI 稳定后，再考虑 MCP Server。
- MCP tools 可包括：
  - `repo.index`
  - `repo.refresh`
  - `java.find_symbol`
  - `java.class_context`
  - `java.find_callers`
  - `java.find_callees`
  - `proto.explain_rpc`
  - `proto.impact_add_field`
  - `context.build_pack`
- HTTP API / Web UI 放到后续，不进入当前 MVP 主线。

## 13. 验收标准

用真实 Java + Protobuf 仓库验证：

1. 能生成 `{java_repo}/.codeflicker/graph.sqlite`。
2. 能通过 `find-symbol` 命中目标类/方法/Proto Message。
3. 能通过 `class-context` 输出类成员、父子关系、注入依赖、调用方、被调方。
4. 能通过 `find-subclasses` 查继承/实现关系。
5. 能通过 `find-callees` / `find-callers` 替代常见 SQL 查询。
6. 能通过 `impact-add-field` 给出 Proto 字段变更风险。
7. CodeFlicker 在 Java/Proto/影响分析场景能自动触发 skill。
8. 用户不需要手写 SQL，也不需要每次显式说“使用 code-context-agent”。

核心判断标准：

> 它是否能让 Claude Code / CodeFlicker 在修改 Java + Protobuf 代码前，更快、更准地拿到相关上下文和风险边界。
