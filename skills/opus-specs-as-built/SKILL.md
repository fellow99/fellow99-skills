---
name: opus-specs-as-built
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

Update this after every document is created.

### 11. README.md — Documentation Index

A navigation page linking to all documents with brief descriptions.

---

## Phase 2: Module-Level spec.md

For each functional module identified in Phase 0, generate a `spec.md`.

### Reading Source Code First

Before writing any module spec, read the actual source files:

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

## Phase 3: Module-Level plan.md

For each module, generate a `plan.md` — the technical counterpart to spec.md.

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

---

## Execution Strategy

### Parallelization

When generating module-level documents, parallelize aggressively:

- Fire 4-8 background agents simultaneously, each handling one module
- Each agent reads its own source files independently
- Collect and verify results as they complete

### Delegation Prompt Template

When delegating module documentation to a subagent:

```
TASK: Generate {spec.md | plan.md} for module {NNN-name}.

CONTEXT:
- Project: {project name and brief description}
- Module source: {path to module directory}
- File list: {enumerate key files}
- Project-level docs already exist at: {path}
- Constitution: {path to constitution.md}

REQUIREMENTS:
1. Read ALL source files in {module path} before writing
2. Follow the {spec.md | plan.md} structure from the skill
3. spec.md: Technology-agnostic, focus on WHAT and WHY
4. plan.md: Implementation-specific, focus on HOW
5. Write in {language preference, e.g., Chinese with English technical terms}
6. Output to: {exact output path}

MUST NOT:
- Speculate about code you haven't read
- Include features not present in the source
- Use placeholder content
```

### Verification

After each document is generated:

1. Confirm the file exists and has content (`ls -la`, `wc -l`)
2. Spot-check that key modules/features mentioned match actual source code
3. Update SPECS_CHECKLIST.md

### Layered Document Strategy

Always generate documents in this order:

1. **Project-level first** — constitution and architecture establish the frame
2. **All spec.md second** — WHAT/WHY layer complete before HOW
3. **All plan.md third** — HOW layer references the specs

This prevents forward references to nonexistent documents.

---

## Output Structure

```
{output-dir}/
├── README.md              # Documentation index
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

---

## Quality Checklist

Before marking any document complete:

- [ ] Every claim traces to actual source code
- [ ] No placeholder content (`TODO`, `TBD`, `[fill in]`)
- [ ] spec.md contains zero implementation details (no framework names, no file paths)
- [ ] plan.md references real files with correct paths
- [ ] Module boundaries are consistent across spec and plan
- [ ] SPECS_CHECKLIST.md updated
- [ ] README.md index updated if new documents added

---

## Tips from Practice

1. **Read before you write.** Skim all files in a module before drafting. The first file you read often misleads about the module's true purpose.

2. **Module sizing matters.** A module with 1-2 files probably belongs inside a larger module. A module with 50+ files probably needs splitting. Aim for 3-40 files per module.

3. **Constitution emerges from code.** Don't invent principles — extract them. If every store follows the same pattern, that's a constitutional principle. If error handling is inconsistent, that's an observation, not a rule.

4. **spec.md is harder than plan.md.** Abstracting away implementation details while remaining accurate is the core challenge. When in doubt, describe the user-visible behavior.

5. **plan.md is more useful than spec.md.** For existing codebases, the technical plan is what developers actually reference. Invest more detail here.

6. **Parallel execution saves 70% time.** 16 modules sequentially = hours. 16 modules in 4 batches of 4 = fraction of the time. Always parallelize module-level work.

7. **Checklist-driven completion.** Without SPECS_CHECKLIST.md, you will lose track. Update it obsessively.
