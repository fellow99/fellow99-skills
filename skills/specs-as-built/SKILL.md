---
name: specs-as-built
description: "Generate comprehensive as-built specification documentation for existing codebases. Use this skill when the user wants to reverse-document a completed project, create spec.md and plan.md for existing code, generate architecture docs from source code, or produce a full documentation suite (constitution, specs, plans, data models, API contracts) for a codebase that already exists. Trigger on phrases like 'document this codebase', 'write specs for existing code', 'reverse-engineer documentation', 'create spec documents', 'as-built documentation', or any request to analyze finished code and produce structured specification artifacts. Also use when the user wants to baseline an existing system before refactoring."
---

# As-Built Specification Generator

Generate a complete, structured documentation suite for an existing codebase by reading source code and reverse-engineering specification artifacts. This is **not** forward-looking planning — it documents what was actually built.

## When to Use

- A codebase exists without written specifications or architecture docs
- The team needs to document a system before refactoring or handing off
- You want a structured understanding of a complex existing project
- Onboarding documentation is needed for an inherited codebase
- Pre-migration analysis requires understanding the current system

## Core Principle: Source Code is Truth

Every claim in the generated documentation must trace back to actual source code. Never speculate about unread code. If a module's behavior is unclear, mark it `[NEEDS CLARIFICATION]` rather than guessing.

---

## Phase 0: Project Discovery

Before writing any documentation, build a mental model of the entire project.

### Step 1: Read project metadata

- `README.md` — project purpose, features, tech stack
- `package.json` / `Cargo.toml` / `pyproject.toml` — dependencies, scripts, version
- Config files — `vite.config.*`, `tsconfig.json`, `.eslintrc.*`, `tailwind.config.*`, `docker-compose.yml`
- License file

### Step 2: Scan directory structure

- Map the top-level directory layout
- Identify source code directories vs. config/build/deploy directories
- Count files per directory to gauge module size
- Identify page/route files if it's a web application

### Step 3: Identify API surface

- If an OpenAPI/Swagger spec exists, read it
- Otherwise scan for route definitions, endpoint handlers, API client files
- Record: path, HTTP method, purpose, entry file

### Step 4: Identify functional modules

Group source code into cohesive functional modules. Each module should:

- Have a clear single responsibility
- Map to a recognizable user-facing feature or infrastructure concern
- Contain 3-40 source files (split or merge if outside this range)

Assign sequential numeric codes starting from `001`:

```
001-api-layer
002-chat-feature
003-message-rendering
...
```

Use `action-noun` format: lowercase, hyphenated, 2-4 words.

---

## Phase 1: Project-Level Documents

Generate these documents in order. Each builds on the previous.

### 1. STRUCTURE.md — Directory & Route Map

Content:

- Full directory tree (2-3 levels deep)
- Page/route inventory (if web app): path, component file, description
- Key config file locations

### 2. API.md — API Endpoint Inventory

For each API endpoint:
| Path | Method | Purpose | Entry File |

Only record facts visible in the code. Don't invent endpoints.

### 3. TECH.md — Technology Inventory

| Category | Technology | Version | Purpose |

Include: framework, build tool, styling, state management, testing, deployment, notable libraries.

### 4. ARCHITECTURE.md — System Architecture

Content:

- Layer diagram (presentation → business logic → data/API → external services)
- Data flow description
- Deployment topology (if applicable: containers, services, ports)
- Key architectural decisions observed in the code

### 5. constitution.md — Project Principles

Extract implicit principles from the codebase:

- Coding conventions (naming, file organization, patterns)
- Architectural constraints (no direct API calls from components, all state through stores, etc.)
- Quality standards (TypeScript strictness, linting rules, test expectations)
- Security boundaries

Frame as "the codebase follows these principles" — descriptive, not prescriptive.

### 6. overall-spec.md — System-Level Specification

A technology-agnostic description of WHAT the system does and WHY.

Structure:

- System purpose and target users
- Core capabilities (user stories format)
- Functional requirements by domain
- Non-functional requirements (performance, accessibility, i18n)
- System boundaries (what's in scope, what's not)

Key rule: **No implementation details.** Write as if the reader doesn't know the tech stack.

### 7. overall-plan.md — System-Level Technical Plan

HOW the system is built — the technical counterpart to overall-spec.md.

Structure:

- Technical Context (runtime environments, key dependencies)
- Constitution compliance check
- Implementation strategy overview
- Cross-cutting concerns (error handling, logging, security)
- Testing approach
- Deployment strategy

### 8. overall-data-model.md — Data Model

- Key entities and their relationships
- State shapes (for frontend stores) or database schemas
- State machines for entities with lifecycle (e.g., session states, message states)
- Validation rules extracted from code

### 9. overall-api.md — Interface Contracts

- External API contracts (what the system consumes)
- Internal module boundaries and contracts
- Event/message protocols (SSE, WebSocket, pub/sub)

### 10. SPECS_CHECKLIST.md — Progress Tracker

A table tracking completion status of every document:

```markdown
| #    | Document            | Path                           | Status  |
| ---- | ------------------- | ------------------------------ | ------- |
| P-01 | Directory Structure | [STRUCTURE.md](./STRUCTURE.md) | ✅ Done |
```

Update this after every document is created. After Phase 3 completes, add a final entry for README.md and mark it ✅ Done.

### 11. README.md — Documentation Index (Placeholder)

Generate a minimal placeholder README.md at this stage — just a title and a note saying "Full index will be generated after all module documents are complete." This placeholder **will be completely overwritten** by the comprehensive README.md generated in Phase 3, so do not invest effort in it here.

---

## Phase 2: Module-Level Documents (spec.md + plan.md)

For each functional module identified in Phase 0, generate **both** `spec.md` and `plan.md`. These are the core module deliverables and MUST be produced together for each module — do not defer plan.md generation to a separate pass.

### Why spec.md + plan.md Together

- **Context preservation**: The subagent that reads source code for spec.md already has full module understanding. Generating plan.md immediately avoids re-reading the same files.
- **Cross-referencing accuracy**: plan.md must reference spec.md's requirement IDs (FR-NNN-xxx). Generating them together ensures accurate cross-references.
- **Parallel efficiency**: Each module's spec.md + plan.md pair is independent of other modules, so they can be generated in parallel batches.

### Reading Source Code First

Before writing any module documents, read the actual source files:

1. List all files in the module directory
2. Read entry points and key files (not every helper)
3. Identify: public API, data types, dependencies, error handling
4. Note file count and approximate line count

### spec.md Structure

```markdown
# {Module Name} Specification

> Module: {NNN-short-name}
> Status: Implemented
> Last Updated: {date}

## 1. Module Overview

### 1.1 Purpose — Why this module exists

### 1.2 Problems Solved — What pain points it addresses

### 1.3 Scope — What's included and excluded

## 2. User Stories

- As a {role}, I can {action} so that {benefit}

## 3. Functional Requirements

### 3.1 {Capability Group}

- FR-NNN-001: System MUST {requirement}

## 4. Key Entities

| Entity | Description | Key Attributes |

## 5. Acceptance Scenarios

### Scenario: {Name}

- Given {context}
- When {action}
- Then {expected result}

## 6. Non-Functional Requirements

- Performance, accessibility, i18n considerations

## 7. Assumptions & Constraints

## 8. Dependencies

- Upstream and downstream module dependencies
```

### spec.md Rules

- **Technology-agnostic**: Describe WHAT, not HOW. No framework names, no file paths.
- **Traceable**: Every requirement should map to observable code behavior.
- **Use RFC 2119 language**: MUST, SHOULD, MAY for requirements.
- **Max 3 `[NEEDS CLARIFICATION]`** markers per spec.
- **Derive user stories from code paths**, not imagination.

---

### plan.md Generation (per module)

After completing spec.md for a module, immediately generate `plan.md` — the technical counterpart to spec.md, using the same source code context already loaded.

### plan.md Structure

```markdown
# {NNN-short-name} Technical Plan (As-Built)

> This document is a retrospective technical plan documenting the actual architecture,
> design decisions, and implementation strategies as built.
> Module: {NNN-short-name}
> Corresponding spec: {path-to-spec.md}
> Last Updated: {date}

## 1. Technical Context

### 1.1 Runtime Environment — Where this code runs

### 1.2 Dependencies — Direct and indirect, with versions and purposes

## 2. Constitution Compliance

- Check each principle from constitution.md
- Mark: ✅ Compliant / ⚠️ Partial / ❌ Violation (with justification)

## 3. Research Findings

- Key technical decisions and their rationale
- Alternatives that were considered (if visible in code/comments)

## 4. Data Model

- Entity definitions with types
- State transitions
- Validation rules from actual code

## 5. Interface Contracts

### 5.1 Provided Interfaces — What this module exports

### 5.2 Consumed Interfaces — What this module imports

### 5.3 Event Protocols — Pub/sub, callbacks, SSE streams

## 6. Implementation Strategy

### 6.1 Architecture Pattern — The actual pattern used

### 6.2 Key Algorithms — Non-trivial logic explained

### 6.3 Error Handling — How errors propagate

### 6.4 Performance — Caching, memoization, lazy loading

## 7. Testing Considerations

- What's testable, suggested test categories
- Edge cases identified from code review

## 8. File Inventory

| File | Purpose | Lines |
```

### plan.md Rules

- **Implementation-specific**: This is where framework names, file paths, and code patterns belong.
- **As-Built, not aspirational**: Document what IS, not what should be.
- **Include actual dependency versions** from package manifests.
- **Reference real file paths** in the codebase.
- **Cross-reference spec.md**: Each technical decision in plan.md should trace to a functional requirement in spec.md (e.g., "Implements FR-NNN-001").

---

## Phase 3: README.md Generation

After ALL project-level and module-level documents are complete, re-scan the output directory and generate a comprehensive `README.md` following the structured format below. This is NOT a simple index — it is a navigation and reference document that gives readers a complete overview of the documentation suite.

### Step 1: Scan the Output Directory

Re-scan the `{output-dir}/` directory to discover all generated documents:

1. List all files and directories under `{output-dir}/`
2. For each module directory (`NNN-name/`), list all files inside
3. Count documents by category (project-level, module-level)
4. Extract module names and numbers

### Step 2: Generate README.md

Use the following structure. Adapt section content based on what was actually generated — do not include sections for documents that don't exist.

```markdown
# 规格文档索引

**项目名称：** {project name}
**版本：** {version from package manifest or "N/A"}
**技术栈：** {key technologies from TECH.md}
**文档生成时间：** {generation date}
**最后更新：** {today's date}

---

## 一、文档总览

| 层级 | 分类 | 文档数量 | 说明 |
|------|------|---------|------|
| 整体 | 项目级顶层文档 | {count} | 架构、技术、宪法等全局文档 |
| 整体 | 整体规格文档 | {count} | overall-* 系列文档 |
| 模块 | {module category 1} | {count} | {range of module numbers} |
| 模块 | {module category 2} | {count} | {range of module numbers} |
| **合计** | **{total dirs} 目录 / {total files} 文件** | | |

---

## 二、项目级顶层文档

全局性的架构、技术、宪法等文档，定义项目基线和开发准则。

| 文档 | 路径 | 说明 |
|------|------|------|
| **方案总纲** | [ARCHITECTURE.md](./ARCHITECTURE.md) | 系统整体架构设计 |
| **技术选型** | [TECH.md](./TECH.md) | 核心技术栈选型理由、版本、依赖说明 |
| **宪法原则** | [constitution.md](./constitution.md) | 项目开发原则、编码规范、治理规则 |
| **项目结构** | [STRUCTURE.md](./STRUCTURE.md) | 源码目录结构、路由清单、组件清单 |
| **API 清单** | [API.md](./API.md) | 全量 API 接口清单 |
| **检查清单** | [SPECS_CHECKLIST.md](./SPECS_CHECKLIST.md) | 规格文档完成度追踪 |

### 整体规格文档

描述跨模块的全局规格、方案和数据模型。

| 文档 | 路径 | 说明 |
|------|------|------|
| **整体规格** | [overall-spec.md](./overall-spec.md) | 系统级功能规格 |
| **整体方案** | [overall-plan.md](./overall-plan.md) | 系统级技术方案 |
| **数据模型** | [overall-data-model.md](./overall-data-model.md) | 全局数据实体定义 |
| **接口模型** | [overall-api.md](./overall-api.md) | 全局 API 规范 |
| **测试用例索引** | [overall-test-cases.md](./overall-test-cases.md) | 全模块测试用例索引总览 |

> 注：仅列出实际生成的文档，未生成的文档不在此表中。

---

## 三、{Module Category Name}（{Range}）

### {NNN} — {Module Chinese Name} ({English Name})

> {One-line module description from spec.md Module Overview.}

| 文档 | 链接 | 说明 |
|------|------|------|
| 功能规格 | [{NNN}-{name}/spec.md](./{NNN}-{name}/spec.md) | {Module}功能规格 |
| 技术方案 | [{NNN}-{name}/plan.md](./{NNN}-{name}/plan.md) | {Module}技术实现方案 |
{additional per-module docs if present, e.g., tasks.md, api.md, data-model.md, pages.md, test-cases.md}

---

{Repeat Section 三 for each module category}

---

## 六、模块编号一览

| 编号 | 模块名 | 英文名 | 分类 |
|------|--------|--------|------|
| {NNN} | {Chinese name} | {English name} | {category} |

> 注：编号中如有跳号，标注为预留编号。

---

## 七、模块文档结构规范

每个模块目录 `NNN-name/` 下包含以下标准文档：

| 文件 | 命名 | 说明 |
|------|------|------|
| 功能规格 | `spec.md` | 定义模块的功能需求、用户故事、验收标准 |
| 技术方案 | `plan.md` | 模块的技术实现方案、架构决策、组件设计 |

> 如项目需要，模块目录还可扩展以下文档：
> - `tasks.md` — 开发任务拆解、依赖关系、里程碑
> - `api.md` — 模块涉及的 API 接口定义
> - `data-model.md` — 模块所需的实体、类型、枚举定义
> - `pages.md` — 模块包含的页面路由、组件树、交互流程
> - `test-cases.md` — 模块 UI 功能测试用例

---

## 八、快速导航

| 目标读者 | 推荐阅读顺序 |
|---------|-------------|
| **新加入开发者** | constitution.md → STRUCTURE.md → overall-spec.md → 具体模块 spec.md |
| **架构师 / Tech Lead** | ARCHITECTURE.md → TECH.md → overall-plan.md → overall-api.md |
| **前端开发** | STRUCTURE.md → 对应模块的 spec.md + plan.md |
| **后端开发** | overall-api.md → overall-data-model.md → 对应模块的 plan.md |
| **测试 / QA** | overall-test-cases.md → SPECS_CHECKLIST.md → 各模块 test-cases.md |
| **产品经理** | overall-spec.md → 对应模块 spec.md |

---

**文档维护者：** {project name} 开发团队
```

### README.md Generation Rules

- **Scan, don't assume**: Read the actual output directory to discover what was generated. Never list documents that don't exist.
- **Chinese with English technical terms**: Section headers in Chinese, technical names preserved in English (matching the reference format).
- **Categorize modules**: Group modules by functional category (e.g., 系统管理, 监控模块, 工具模块). Derive categories from the module descriptions.
- **Include all module docs**: If a module has additional files beyond spec.md and plan.md (e.g., api.md, data-model.md), include them in the module's document table.
- **Accurate counts**: The 文档总览 table must have accurate counts — count actual files, don't estimate.
- **Module numbering**: If there are gaps in numbering, note them as "预留编号" (reserved numbers).

---

## Execution Strategy

### Parallelization

When generating module-level documents, parallelize aggressively:

- Fire 4-8 background agents simultaneously, each handling one module
- Each agent generates **both spec.md AND plan.md** for its module in a single pass
- Each agent reads its own source files independently
- Collect and verify results as they complete

### Delegation Prompt Template

When delegating module documentation to a subagent, always request both documents together:

```
TASK: Generate spec.md AND plan.md for module {NNN-name}.

CONTEXT:
- Project: {project name and brief description}
- Module source: {path to module directory}
- File list: {enumerate key files}
- Project-level docs already exist at: {path}
- Constitution: {path to constitution.md}

REQUIREMENTS:
1. Read ALL source files in {module path} before writing anything
2. Generate spec.md FIRST, then plan.md — both in this same session
3. spec.md: Technology-agnostic, focus on WHAT and WHY
   - Follow the spec.md structure from the skill
   - Use RFC 2119 language (MUST, SHOULD, MAY)
   - Derive user stories from code paths, not imagination
   - Max 3 [NEEDS CLARIFICATION] markers
4. plan.md: Implementation-specific, focus on HOW
   - Follow the plan.md structure from the skill
   - Cross-reference spec.md requirement IDs (e.g., "Implements FR-NNN-001")
   - Include actual dependency versions from package manifests
   - Reference real file paths in the codebase
   - As-Built: document what IS, not what should be
5. Write in {language preference, e.g., Chinese with English technical terms}
6. Output spec.md to: {exact output path for spec.md}
7. Output plan.md to: {exact output path for plan.md}

MUST NOT:
- Speculate about code you haven't read
- Include features not present in the source
- Use placeholder content
- Generate spec.md and plan.md in separate sessions — both MUST be produced in this single session
```

### Verification

After each document is generated:

1. Confirm the file exists and has content (`ls -la`, `wc -l`)
2. Spot-check that key modules/features mentioned match actual source code
3. Update SPECS_CHECKLIST.md

After Phase 3 (README.md) is generated:

4. Verify all links in README.md point to existing files (`grep -oP '\[.*?\]\(\K[^)]+' README.md | while read f; do [ ! -f "$f" ] && echo "BROKEN: $f"; done`)
5. Verify document counts in 文档总览 table match actual file counts
6. Verify module list in 模块编号一览 matches all `NNN-*/` directories
7. Update SPECS_CHECKLIST.md to mark README.md as complete

### Layered Document Strategy

Always generate documents in this order:

1. **Project-level first** — constitution, architecture, and overall docs establish the frame (Phase 0 + Phase 1)
2. **Module-level second** — For each module, generate spec.md then plan.md together. Modules can be parallelized across agents, but within each module spec.md must come before plan.md. (Phase 2)
3. **Final index last** — README.md is generated after ALL other documents are complete, by scanning the actual output directory. (Phase 3)

This prevents forward references to nonexistent documents and ensures the README.md index is accurate.

---

## Output Structure

```
{output-dir}/
├── README.md              # Comprehensive documentation index (generated LAST in Phase 3)
├── SPECS_CHECKLIST.md     # Completion tracker
├── STRUCTURE.md           # Directory & route map
├── API.md                 # API endpoint inventory
├── TECH.md                # Technology inventory
├── ARCHITECTURE.md        # System architecture
├── constitution.md        # Project principles
├── overall-spec.md        # System-level spec
├── overall-plan.md        # System-level plan
├── overall-data-model.md  # Data model
├── overall-api.md         # Interface contracts
├── 001-{module}/
│   ├── spec.md            # Module specification
│   └── plan.md            # Module technical plan
├── 002-{module}/
│   ├── spec.md
│   └── plan.md
└── ...
```

Note: README.md is generated in Phase 3 by scanning all completed documents. It must reflect the actual directory contents, not a predicted structure.

---

## Quality Checklist

### Per-Document Checks

Before marking any document complete:

- [ ] Every claim traces to actual source code
- [ ] No placeholder content (`TODO`, `TBD`, `[fill in]`)
- [ ] spec.md contains zero implementation details (no framework names, no file paths)
- [ ] plan.md references real files with correct paths
- [ ] plan.md cross-references spec.md requirement IDs (FR-NNN-xxx)
- [ ] Module boundaries are consistent across spec and plan
- [ ] Every module has BOTH spec.md and plan.md generated
- [ ] SPECS_CHECKLIST.md updated

### README.md Checks (Phase 3)

Before marking README.md complete:

- [ ] Generated by scanning actual specs directory (not predicted structure)
- [ ] Contains all required sections: 文档总览, 项目级顶层文档, 模块文档, 模块编号一览, 模块文档结构规范, 快速导航
- [ ] Every link points to an existing file
- [ ] Module counts and categories match actual directory contents
- [ ] Document total counts are accurate (counted from actual files, not estimated)
- [ ] Module descriptions extracted from actual spec.md content

---

## Tips from Practice

1. **Read before you write.** Skim all files in a module before drafting. The first file you read often misleads about the module's true purpose.

2. **Module sizing matters.** A module with 1-2 files probably belongs inside a larger module. A module with 50+ files probably needs splitting. Aim for 3-40 files per module.

3. **Constitution emerges from code.** Don't invent principles — extract them. If every store follows the same pattern, that's a constitutional principle. If error handling is inconsistent, that's an observation, not a rule.

4. **spec.md is harder than plan.md.** Abstracting away implementation details while remaining accurate is the core challenge. When in doubt, describe the user-visible behavior.

5. **plan.md is more useful than spec.md.** For existing codebases, the technical plan is what developers actually reference. Invest more detail here.

6. **Parallel execution saves 70% time.** 16 modules sequentially = hours. 16 modules in 4 batches of 4 = fraction of the time. Always parallelize module-level work.

7. **Checklist-driven completion.** Without SPECS_CHECKLIST.md, you will lose track. Update it obsessively.
