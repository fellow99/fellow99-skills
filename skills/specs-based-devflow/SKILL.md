---
name: specs-based-devflow
description: >
  End-to-end development workflow from raw requirements to shipped code. Orchestrates the full
  pipeline: requirements gathering, specification (via speckit or custom tools), implementation,
  code review, testing, bug fixing, and regression testing. Use this skill whenever a user
  describes a new feature or requirement and wants to go through the complete development
  lifecycle — not just planning or just coding, but the full disciplined flow from spec to
  verified working software. Also trigger when the user mentions "dev flow", "development
  workflow", "full development process", "spec to code", "requirement to delivery", or wants
  to execute multiple phases (spec → dev → review → test → fix → regression) in sequence.
  Even if the user only mentions one phase, consider offering the full flow since the phases
  are designed to work together.
---

# Specs-Based Development Flow

A structured, phase-gated workflow that carries a feature from raw requirements through specification, development, code review, testing, bug fixing, and regression testing. Each phase produces artifacts the next phase consumes, creating a traceable chain from requirement to verified code.

## Why This Skill Exists

Most AI-assisted development jumps straight from "build X" to writing code, skipping specification, test design, and verification. This leads to half-built features, untested edge cases, and regressions. This skill enforces a disciplined pipeline where every phase has clear inputs, outputs, and completion criteria — the same way a mature engineering team ships software.

## Core Principles

- **Phase gates**: Each phase must complete and be confirmed before the next begins. This prevents accumulating technical debt.
- **Artifact-driven**: Every phase produces concrete files (spec.md, test-cases.md, DEV_CHECKLIST.md, REVIEW_REPORT.md, TEST_CHECKLIST.md, test reports). These are the source of truth, not conversation history.
- **Human in the loop**: By default, pause between phases for user confirmation. The user can opt into continuous execution if they trust the flow.
- **Tool-agnostic core**: The workflow works with speckit by default, but can adapt if the user specifies different specification tools.

## Workflow Overview

```
Preparation → Specification → Development → Code Review → Testing → Bug Fix → Regression
     ↓              ↓             ↓            ↓           ↓          ↓          ↓
  env check     spec.md       code +       review       test       fixes     final
  git setup     plan.md       DEV_LOG      report       report     report    report
                tasks.md
                test-cases.md
```

## Execution Flow

### Step 0: Environment Assessment

Before anything else, understand the project landscape. Do NOT ask the user to repeat information they already provided — infer from context where possible.

**0.1 Detect specification tools**

Check which speckit skills are available by examining the loaded skill list. Report what you find:

```
Available speckit skills:
- speckit-specify: Create feature specification
- speckit-clarify: Clarify ambiguous requirements
- speckit-plan: Generate implementation plan
- speckit-tasks: Generate task list
- speckit-implement: Execute implementation
- speckit-analyze: Cross-artifact consistency analysis
- speckit-checklist: Generate requirement checklists
- speckit-baseline: Spec from existing code
- speckit-constitution: Project governance
```

If the user wants to use different specification tools, record that preference — it affects how later phases run.

**0.1b Detect code review skills**

Check whether `requesting-code-review` and `receiving-code-review` are installed:

```bash
ls ~/.config/opencode/skills/requesting-code-review 2>/dev/null && echo "requesting-code-review: found"
ls ~/.config/opencode/skills/receiving-code-review 2>/dev/null && echo "receiving-code-review: found"
```

- Both installed → proceed. Code Review phase will use them.
- One or both missing → ask the user during setup:

```
Code review skills (requesting-code-review, receiving-code-review) are not installed.
These provide structured, categorized code review in the Code Review phase.

1. Auto-install now (recommended) — npx skills add from obra/superpowers
2. Use built-in fallback — simpler inline review, less rigorous than dedicated skills
3. Skip code review entirely — not recommended, removes a quality gate
```

Record the user's choice. This avoids surprises at Step 3.5.

**0.2 Confirm working directory**

Default: the current working directory. If the user specified a different path, use that.

Run a quick scan:
- Is this a git repository? (`git rev-parse --git-dir 2>/dev/null`)
- If yes, what branch are we on? (`git branch --show-current`)
- Is there a `specs/` directory? Look for `specs/`, `.specify/`, or any directory that contains spec-like markdown files.
- Is there a `README.md`?
- Are there build files? (`package.json`, `pom.xml`, `build.gradle`, `Makefile`, etc.)

Report findings to the user. If there's no git repo, warn that git-based features (branching, commits between phases) won't work unless initialized. If there's no specs directory, ask the user to specify where specification documents should live — this is required for speckit to function.

**0.3 Git branch handling**

If the user specified a target branch:
- Create and switch to it: `git checkout -b <branch-name>`
- If git isn't initialized, ask whether to run `git init`

Report the current branch to the user regardless.

**0.4 Compile the project**

If build files were detected, attempt a build:
- Node.js: `npm run build` or `yarn build`
- Java/Maven: `mvn compile`
- Java/Gradle: `gradle build`
- Go: `go build ./...`
- Python: skip (no standard compile step)
- If no build system detected, skip this step and note it.

If the build fails, report the error and ask the user whether to proceed anyway or fix it first.

**0.5 Start the development environment**

Try to start the project's dev server:
- Node.js: `npm run dev` or `npm start`
- Java/Spring: `mvn spring-boot:run` or check for `spring-boot-devtools`
- Go: `go run .`
- Python: `python manage.py runserver` or `flask run` or `uvicorn`

If startup requires configuration (database URLs, env vars), note what's missing and ask the user. Don't guess at sensitive configuration.

If the dev server starts, note the URL (typically `http://localhost:XXXX`) — this will be needed for Playwright-based testing and debugging in later phases.

### Step 1: Requirements Gathering

**Required inputs from the user — this is a hard gate, the workflow CANNOT proceed without them:**

| Input | Description | Example |
|---|---|---|
 | **需求编号** (Requirement ID) | Unique identifier for this requirement, used for spec subdirectory name, branch naming, and traceability. This becomes the subdirectory name under `specs/` — e.g., `specs/REQ-001/` | `REQ-001`, `2026-010`, `SPRINT3-5` |
| **需求名称** (Requirement Name) | Short descriptive name for the feature, used for spec directory and documentation | `用户认证`, `订单导出`, `权限管理` |
| **需求描述** (Requirement Description) | Detailed description of what needs to be built | User's feature description |

If the user has not provided all three, ask for the missing ones before proceeding. These are non-negotiable — they drive branch naming, spec directory structure, and artifact traceability throughout the entire workflow.

**If the requirement description is vague**, ask targeted follow-up questions:
- What is the core user-facing behavior?
- Who are the actors (user roles)?
- What data entities are involved?
- Are there specific constraints (performance, security, compatibility)?
- What existing features does this interact with?

Do NOT proceed to specification until all three inputs (编号, 名称, 描述) are confirmed by the user and you can state the requirement in a single coherent paragraph.

**After confirmation**, ask which phases the user wants to execute:

```
Available phases:
1. Specification — Generate spec.md, plan.md, tasks.md, test-cases.md
2. Development — Implement the feature per spec
3. Code Review — Review implemented code before testing
4. Testing — Run test cases (backend API + frontend UI)
5. Bug Fix — Fix issues found in testing
6. Regression — Re-test fixed issues

Which phases should I execute? (default: all, with confirmation between each)
```

Record the user's phase selection and whether they want continuous execution (no pauses) or gate-checked execution (pause between phases).

### Step 2: Specification Phase

Read the detailed instructions: `references/phase-specification.md`

Summary of the phase:

1. Scan existing project specs/documentation to understand the codebase
2. Analyze the new requirement against existing architecture
3. Execute speckit skills in order:
   - `speckit-specify` → generates `specs/<需求编号>/spec.md`
   - `speckit-clarify` → (optional) refines spec if ambiguities found
   - `speckit-plan` → generates `specs/<需求编号>/plan.md` + design artifacts
   - `speckit-tasks` → generates `specs/<需求编号>/tasks.md`
   - `speckit-analyze` → (optional) cross-artifact consistency check
 4. Generate `test-cases.md` from the spec and plan
 5. Commit all artifacts to git (if git is available)
 6. Report phase results and ask for confirmation before next phase

**Phase output**: `specs/<需求编号>/` directory containing spec.md, plan.md, tasks.md, test-cases.md, and any design artifacts. The subdirectory name is the requirement ID provided by the user — this overrides speckit's default `<number>-<short-name>` naming convention.

### Step 3: Development Phase

Read the detailed instructions: `references/phase-development.md`

Summary of the phase:

1. Scan project docs and the feature's specification documents
2. Create a development log directory: `<project>/logs/<YYYYMMDD>-<N>/`
3. Initialize `DEV_CHECKLIST.md` in that directory
4. If frontend exists, open it with Playwright and log in
5. Execute implementation using `speckit-implement` or manual development guided by tasks.md
6. During development, use Playwright for live debugging:
   - Navigate to relevant routes
   - Trigger CRUD operations
   - Watch console for errors and fix them
7. Commit completed work to git
8. Report phase results and ask for confirmation before next phase

**Phase output**: Implemented code + `<project>/logs/<YYYYMMDD>-<N>/DEV_CHECKLIST.md`

### Step 3.5: Code Review Phase

**Prerequisite**: This phase works best with the `requesting-code-review` and `receiving-code-review` skills from `obra/superpowers`. If they are not installed, a built-in fallback review will be used (less rigorous but functional).

Install with:
```bash
npx skills add https://github.com/obra/superpowers --skill requesting-code-review
npx skills add https://github.com/obra/superpowers --skill receiving-code-review
```

Read the detailed instructions: `references/phase-code-review.md`

Summary of the phase:

**If dedicated skills are available (preferred path):**
1. Load `requesting-code-review` skill → dispatch a reviewer subagent with:
   - Implementation summary (what was built and how)
   - Requirements/spec reference (`specs/<需求编号>/spec.md`)
   - Commit range (the diff since the previous phase)
   - Categorized output: **Critical** (fix immediately), **Important** (fix before proceeding), **Minor** (note for later)
2. Create `REVIEW_REPORT.md` in the log directory with the reviewer's findings
3. Load `receiving-code-review` skill → process feedback:
   - Verify each point against actual codebase behavior and test coverage
   - Ask for clarification on ambiguous items before implementing anything
   - Push back on suggestions that break functionality, lack context, violate YAGNI, or conflict with established decisions
   - Fix Critical and Important items in priority order, testing each fix individually
   - Acknowledge correct feedback through action (not gratitude)
4. If any Critical items were found and fixed, re-run step 1 (re-review) to confirm they're resolved
5. Commit fixes to git with a `code-review-fix` commit

**If dedicated skills are unavailable (built-in fallback):**
1. Manually construct a review prompt with: implementation summary, spec reference, and `git diff` output
2. Dispatch the review to a general-purpose agent (or yourself, as orchestrator) with explicit instruction to categorize findings as Critical / Important / Minor
3. Write findings into `REVIEW_REPORT.md`
4. For each finding: verify against codebase, fix Critical + Important items in priority order
5. No re-review step (fallback is intentionally lighter)
6. Commit fixes to git

**Phase gate (both paths):**
- Proceed to Testing only when no Critical items remain
- If unresolved Critical items exist, pause and ask the user for direction

**Phase output**: `<project>/logs/<YYYYMMDD>-<N>/REVIEW_REPORT.md` + code review fixes

### Step 4: Testing Phase

Read the detailed instructions: `references/phase-testing.md`

Summary of the phase:

1. Build the project (both frontend and backend if applicable)
2. Start the project (prefer spring-boot-devtools for Java backends)
3. Read `test-cases.md` thoroughly
4. Create `TEST_CHECKLIST.md` from test cases in the log directory
5. Backend testing via curl:
   - Get auth token if login exists (call login API, extract token)
   - Test each API endpoint from the spec with `authorization: Bearer <token>`
   - Record request/response for each test
6. Frontend testing via Playwright:
   - Navigate to each feature page
   - Execute each test case from test-cases.md
   - Capture screenshots and console output for failures
7. Generate test report: `<project>/logs/<YYYYMMDD>-<N>/TEST_REPORT.md`
8. Commit test artifacts to git
9. Report phase results (pass/fail counts, critical issues) and ask for confirmation

**Phase output**: `<project>/logs/<YYYYMMDD>-<N>/TEST_REPORT.md` + test evidence

### Step 5: Bug Fix Phase

Read the detailed instructions: `references/phase-bugfix.md`

Summary of the phase:

1. Read the test report and identify all failed test cases
2. Fix each bug, prioritizing by severity
3. Use Playwright for live debugging during fixes:
   - Navigate to affected pages
   - Trigger the failing functionality
   - Monitor console for errors
4. Update the test report with fix status for each bug
5. Commit fixes to git
6. Report which bugs were fixed and which remain (if any)

**Phase output**: Updated `TEST_REPORT.md` with fix annotations

### Step 6: Regression Testing Phase

Read the detailed instructions: `references/phase-regression.md`

Summary of the phase:

1. Read the updated test report (bugs marked as fixed)
2. Re-test each fixed bug:
   - Backend: re-run the curl commands that previously failed
   - Frontend: re-run the Playwright scenarios that previously failed
3. Also spot-check a few passing test cases to ensure no new regressions
4. Update the test report with regression results
5. Commit regression test results to git
6. Report final status

**Phase output**: Final `TEST_REPORT.md` with regression results

## Phase Gating Protocol

After each phase completes, report to the user:

```
## Phase Complete: [Phase Name]

**Artifacts produced:**
- [list files created/modified]

**Key findings:**
- [summary of what was discovered or accomplished]

**Issues requiring attention:**
- [any blockers, warnings, or decisions needed]

**Next phase:** [Phase Name]
**What it will do:** [brief description]

Proceed? (yes / skip / stop / modify)
```

Wait for the user's response:
- **yes** → Continue to next phase
- **skip** → Skip the next phase (user takes responsibility)
- **stop** → Halt the workflow entirely
- **modify** → User wants to adjust something before proceeding

If the user selected continuous execution at Step 1, skip the pause and auto-continue, but still output the phase report for visibility.

## Log Directory Convention

All phase artifacts (checklists, reports, scripts, evidence) go into:

```
<project-root>/logs/<YYYYMMDD>-<N>/
```

Where:
- `YYYYMMDD` = today's date
- `N` = sequence number (find the highest existing N for today, increment by 1)

Example: `logs/20260510-1/`, `logs/20260510-2/`

## Git Commit Protocol

After each phase, if git is available:

```bash
git add -A
git commit -m "<phase-name>: <brief description of what was accomplished>"
```

Use the phase name as a prefix:
- `specification: add user auth feature spec and test cases`
- `development: implement user auth login and registration`
- `code-review: review feedback — 2 critical, 3 important, 5 minor`
- `code-review-fix: fix token validation and null pointer in auth middleware`
- `testing: complete test report — 8 pass, 2 fail`
- `bugfix: fix token refresh and null user redirect`
- `regression: all 2 previously failed tests now pass`

## Error Handling

- **Build fails in preparation**: Report error, ask user whether to proceed or fix first
- **Dev server won't start**: Report error, ask user for configuration. Don't guess at credentials or env vars.
- **Speckit skill fails**: Report the error from the skill output. Suggest running the skill standalone for debugging. Ask whether to retry or skip.
- **Code review skills not installed**: Handled at Step 0.1b — user chooses auto-install, fallback, or skip before reaching Step 3.5. No surprise at phase execution time.
- **Code review reveals critical design flaw**: Pause the workflow. The spec may need revision before continuing development. Suggest going back to specification.
- **Test reveals critical design flaw**: Pause the workflow. The spec may need revision before continuing development. Suggest going back to specification.
- **Bug fix introduces new regressions**: Do NOT proceed to regression. Go back to bug fix phase. Report the regression.

## Quick Reference: Speckit Skill Chain

The canonical speckit execution order for the specification phase:

```
speckit-specify    → spec.md      (from raw requirement)
speckit-clarify    → spec.md      (refined, if ambiguities exist)
speckit-plan       → plan.md      (from spec.md)
speckit-tasks      → tasks.md     (from plan.md + spec.md)
speckit-analyze    → report       (optional consistency check)
speckit-checklist  → checklists/  (optional quality gates)
speckit-implement  → code         (from tasks.md)
```

Each skill depends on the output of the previous one. If a skill's prerequisite artifact is missing, the skill will error — that's expected and means you need to run the prior skill first.

## Quick Reference: Code Review Skills (obra/superpowers)

These skills handle the two sides of code review. Install once, use in the Code Review phase.

```bash
npx skills add https://github.com/obra/superpowers --skill requesting-code-review
npx skills add https://github.com/obra/superpowers --skill receiving-code-review
```

| Skill | Role | What it does |
|---|---|---|
| `requesting-code-review` | Dispatch | Sends code context to a reviewer subagent; returns feedback categorized as Critical / Important / Minor |
| `receiving-code-review` | Receive | Evaluates feedback with technical rigor; verifies against actual code; pushes back on invalid items; applies fixes in priority order |

**Design rationale**: These are separate skills because requesting and receiving review require opposite mindsets. Requesting is about precision of context (what to send). Receiving is about critical thinking (what to accept and how to fix). Keeping them independent lets each evolve on its own cadence and lets other workflows reuse them independently.

## When Things Go Off Track

This workflow is a guide, not a straitjacket. Use judgment:

- If the requirement is trivial (a one-line config change), don't generate a full spec → plan → tasks chain. Just do it and skip to testing.
- If the project has no `.specify/` directory, speckit skills may not work. Offer to set it up or fall back to manual specification.
- If the user wants to use a different tool (e.g., their own spec format), adapt. The phase structure still applies; just change how artifacts are produced.
- If a phase produces no findings (e.g., all tests pass on first run), report that clearly and ask whether to skip subsequent phases.

## Reference Files

- `references/phase-preparation.md` — Detailed preparation checklist and environment setup
- `references/phase-specification.md` — Specification phase step-by-step guide
- `references/phase-development.md` — Development phase with Playwright debugging
- `references/phase-code-review.md` — Code review phase: requesting and receiving review
- `references/phase-testing.md` — Testing phase with curl + Playwright
- `references/phase-bugfix.md` — Bug fix phase with live debugging
- `references/phase-regression.md` — Regression testing phase
