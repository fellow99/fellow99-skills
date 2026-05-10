# Specification Phase — Detailed Guide

This phase transforms a raw requirement into a complete set of specification documents that drive implementation and testing. The output is a `specs/<feature>/` directory containing all necessary artifacts.

**Prerequisite**: The user must have already provided the **需求编号** (requirement ID) and **需求名称** (requirement name) during the requirements gathering step. These are used for branch naming and spec directory structure throughout this phase.

## Goal

Produce these artifacts in order:
1. `spec.md` — Feature specification (WHAT to build)
2. Clarified spec (if ambiguities found)
3. `plan.md` — Technical implementation plan (HOW to build it)
4. `tasks.md` — Dependency-ordered task list (WHAT ORDER to build it in)
5. `test-cases.md` — Test cases for validation (HOW to verify it works)
6. Optional: `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

## Step-by-Step

### 1. Scan Existing Project Documentation

Before generating new specs, understand what already exists. This prevents duplicating existing features and ensures the new spec fits the architecture.

Read these files (if they exist):
- `README.md` — Project overview
- `specs/` — Any existing feature specs
- `.specify/memory/constitution.md` — Project governance principles
- Architecture or design docs in `docs/`

Extract:
- What the project does (core features)
- Tech stack and architectural patterns
- Data models and API patterns already in use
- Any constraints or conventions from the constitution

### 2. Analyze the New Requirement

Given the user's requirement, identify:

**Actors**: Who uses this feature? (user roles, system actors)
**Actions**: What can they do? (CRUD operations, workflows, triggers)
**Data**: What entities are involved? (new models, extensions to existing models)
**Constraints**: What limits exist? (permissions, performance, compatibility, security)
**Integration points**: How does this connect to existing features?

Map the requirement to existing project context:
- Does this extend an existing feature? → Reference existing spec
- Is this a new standalone feature? → Create fresh spec
- Does this replace something? → Note the migration path

### 3. Execute Speckit Specify

Invoke the `speckit-specify` skill to create the initial feature specification.

**What happens:**
1. A short name is generated for the feature (e.g., "user-auth")
2. A new branch is created (e.g., `1-user-auth`)
3. `.specify/scripts/bash/create-new-feature.sh` is run to scaffold the feature directory
4. The spec template is loaded and filled based on the requirement analysis
5. `specs/<feature>/spec.md` is written

**Your role during specify:**
- Ensure the requirement description is passed accurately
- If the skill asks clarification questions, relay them to the user
- Verify the generated spec covers all aspects of the requirement
- If the spec has `[NEEDS CLARIFICATION]` markers, note them for the clarify step

### 4. Execute Speckit Clarify (Recommended)

If the spec has ambiguities or `[NEEDS CLARIFICATION]` markers, invoke `speckit-clarify`.

**What happens:**
1. The spec is scanned across 10+ taxonomy categories (functional scope, data model, UX flow, security, etc.)
2. Up to 5 targeted clarification questions are presented one at a time
3. Each answer is integrated into the spec immediately
4. A `## Clarifications` section is added to spec.md

**Your role during clarify:**
- Present each question to the user with the recommended answer
- The user can accept the recommendation or provide their own answer
- Don't skip questions — each one exists because the spec has a real gap
- If the user says "skip clarification", warn that rework risk increases but proceed

### 5. Execute Speckit Plan

Invoke `speckit-plan` to generate the technical implementation plan.

**What happens:**
1. `.specify/scripts/bash/setup-plan.sh --json` is run
2. The spec and constitution are loaded
3. Phase 0: `research.md` is generated to resolve technical unknowns
4. Phase 1: `data-model.md`, `contracts/`, `quickstart.md` are generated
5. `plan.md` is filled with technical context, architecture, and file structure
6. Constitution check is performed and documented

**Your role during plan:**
- Verify the plan's tech stack matches the project's actual stack
- Check that the file structure in the plan aligns with the existing project layout
- If `research.md` identifies technology choices, confirm they're appropriate
- Review `contracts/` for API design — ensure endpoints follow existing patterns

### 6. Execute Speckit Checklist (Optional)

If quality gates are desired, invoke `speckit-checklist` to validate requirements quality.

**What happens:**
- A checklist is generated in `specs/<feature>/checklists/<domain>.md`
- Each item is a "unit test for English" — checking whether the spec is well-written, not whether the code works

**When to use:**
- For complex features where spec quality matters
- When the team has had issues with ambiguous requirements in the past
- Skip for simple, well-understood features

### 7. Execute Speckit Tasks

Invoke `speckit-tasks` to generate the dependency-ordered task list.

**What happens:**
1. `.specify/scripts/bash/check-prerequisites.sh --json` is run
2. All design documents (spec, plan, data model, contracts) are loaded
3. Tasks are organized by user story priority (P1, P2, P3)
4. Each task has: checkbox, ID, labels, file paths, dependencies
5. `tasks.md` is written with phases: Setup → Foundational → User Stories → Polish

**Your role during tasks:**
- Verify task file paths match the actual project structure
- Check that dependencies make sense (no circular dependencies)
- Ensure the MVP scope (typically User Story 1) is clearly identified

### 8. Execute Speckit Analyze (Optional)

If cross-artifact consistency is a concern, invoke `speckit-analyze`.

**What happens:**
- A read-only analysis runs across spec.md, plan.md, and tasks.md
- Checks for: duplication, ambiguity, underspecification, constitution alignment, coverage gaps, inconsistency
- Severity is assigned: CRITICAL → HIGH → MEDIUM → LOW

**When to use:**
- For complex features with many artifacts
- When the spec went through multiple clarification rounds
- Skip for simple features

**If CRITICAL issues are found:**
- Fix them before proceeding to development
- The analyze skill will suggest specific remediations

### 9. Generate Test Cases

After all specification artifacts are complete, generate `test-cases.md`.

This is NOT a speckit skill — you generate this directly based on the spec and plan.

**Test case format:**
```markdown
# Test Cases: <Feature Name>

## TC-001: <Test Case Title>
**Priority**: P1/P2/P3
**Type**: Functional / Edge Case / Security / Performance
**Precondition**: <What must be true before testing>
**Steps**:
1. <step>
2. <step>
**Expected Result**: <what should happen>
**Actual Result**: <filled during testing>
**Status**: PASS / FAIL / SKIP

## TC-002: ...
```

**Coverage areas to test:**
- **Backend API tests** (from `contracts/` if available):
  - Each endpoint: success case, validation errors, auth errors, edge cases
  - CRUD operations for each entity
  - Authorization boundaries (who can access what)
- **Frontend UI tests** (from spec user stories):
  - Page rendering and navigation
  - Form submissions (valid + invalid input)
  - Error states and empty states
  - Cross-feature interactions
- **Integration tests**:
  - End-to-end user journeys
  - Data consistency between frontend and backend

**Where to save**: `specs/<feature>/test-cases.md`

### 10. Commit Specification Artifacts

```bash
git add specs/<feature>/
git commit -m "specification: add <feature-name> spec, plan, tasks, and test cases"
```

### 11. Phase Report

Present the completion report:

```
## Specification Phase Complete

**Feature**: <feature-name>
**Branch**: <branch-name>

**Artifacts produced:**
- specs/<feature>/spec.md
- specs/<feature>/plan.md
- specs/<feature>/tasks.md
- specs/<feature>/test-cases.md
- [other artifacts: research.md, data-model.md, contracts/, quickstart.md]

**Key decisions:**
- <list 2-3 important technical or design decisions made>

**Ambiguities resolved:**
- <list clarifications made during the clarify step>

**Test coverage:**
- <N> test cases generated (P1: X, P2: Y, P3: Z)

**Next phase:** Development
**What it will do:** Implement the feature per spec, using tasks.md as the execution guide

Proceed? (yes / skip / stop / modify)
```
