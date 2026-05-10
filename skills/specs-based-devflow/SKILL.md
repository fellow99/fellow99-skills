---
name: specs-based-devflow
description: >
  End-to-end development workflow from raw requirements to shipped code. Orchestrates the full
  pipeline: requirements gathering, specification (via speckit or custom tools), implementation,
  testing, bug fixing, and regression testing. Use this skill whenever a user describes a new
  feature or requirement and wants to go through the complete development lifecycle — not just
  planning or just coding, but the full disciplined flow from spec to verified working software.
  Also trigger when the user mentions "dev flow", "development workflow", "full development
  process", "spec to code", "requirement to delivery", or wants to execute multiple phases
  (spec → dev → test → fix → regression) in sequence. Even if the user only mentions one phase,
  consider offering the full flow since the phases are designed to work together.
---

# Specs-Based Development Flow

A structured, phase-gated workflow that carries a feature from raw requirements through specification, development, testing, bug fixing, and regression testing. Each phase produces artifacts the next phase consumes, creating a traceable chain from requirement to verified code.

## Why This Skill Exists

Most AI-assisted development jumps straight from "build X" to writing code, skipping specification, test design, and verification. This leads to half-built features, untested edge cases, and regressions. This skill enforces a disciplined pipeline where every phase has clear inputs, outputs, and completion criteria — the same way a mature engineering team ships software.

## Core Principles

- **Phase gates**: Each phase must complete and be confirmed before the next begins. This prevents accumulating technical debt.
- **Artifact-driven**: Every phase produces concrete files (spec.md, test-cases.md, DEV_CHECKLIST.md, TEST_CHECKLIST.md, test reports). These are the source of truth, not conversation history.
- **Human in the loop**: By default, pause between phases for user confirmation. The user can opt into continuous execution if they trust the flow.
- **Tool-agnostic core**: The workflow works with speckit by default, but can adapt if the user specifies different specification tools.

## Workflow Overview

```
Preparation → Specification → Development → Testing → Bug Fix → Regression
     ↓              ↓             ↓            ↓          ↓          ↓
  env check     spec.md       code +        test       fixes     final
  git setup     plan.md       DEV_LOG       report     report    report
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

**If the user already provided a clear requirement**, confirm your understanding and proceed.

**If the requirement is missing or vague**, ask targeted questions:
- What is the core user-facing behavior?
- Who are the actors (user roles)?
- What data entities are involved?
- Are there specific constraints (performance, security, compatibility)?
- What existing features does this interact with?

Do NOT proceed to specification until you can state the requirement in a single coherent paragraph that the user confirms.

**After confirmation**, ask which phases the user wants to execute:

```
Available phases:
1. Specification — Generate spec.md, plan.md, tasks.md, test-cases.md
2. Development — Implement the feature per spec
3. Testing — Run test cases (backend API + frontend UI)
4. Bug Fix — Fix issues found in testing
5. Regression — Re-test fixed issues

Which phases should I execute? (default: all, with confirmation between each)
```

Record the user's phase selection and whether they want continuous execution (no pauses) or gate-checked execution (pause between phases).

### Step 2: Specification Phase

Read the detailed instructions: `references/phase-specification.md`

Summary of the phase:

1. Scan existing project specs/documentation to understand the codebase
2. Analyze the new requirement against existing architecture
3. Execute speckit skills in order:
   - `speckit-specify` → generates `specs/<feature>/spec.md`
   - `speckit-clarify` → (optional) refines spec if ambiguities found
   - `speckit-plan` → generates `specs/<feature>/plan.md` + design artifacts
   - `speckit-tasks` → generates `specs/<feature>/tasks.md`
   - `speckit-analyze` → (optional) cross-artifact consistency check
4. Generate `test-cases.md` from the spec and plan
5. Commit all artifacts to git (if git is available)
6. Report phase results and ask for confirmation before next phase

**Phase output**: `specs/<feature>/` directory containing spec.md, plan.md, tasks.md, test-cases.md, and any design artifacts.

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
- `testing: complete test report — 8 pass, 2 fail`
- `bugfix: fix token refresh and null user redirect`
- `regression: all 2 previously failed tests now pass`

## Error Handling

- **Build fails in preparation**: Report error, ask user whether to proceed or fix first
- **Dev server won't start**: Report error, ask user for configuration. Don't guess at credentials or env vars.
- **Speckit skill fails**: Report the error from the skill output. Suggest running the skill standalone for debugging. Ask whether to retry or skip.
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
- `references/phase-testing.md` — Testing phase with curl + Playwright
- `references/phase-bugfix.md` — Bug fix phase with live debugging
- `references/phase-regression.md` — Regression testing phase
