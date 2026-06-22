# Code Review Phase — Detailed Guide

This phase inserts a quality gate between development and testing. It uses two independent skills from `obra/superpowers`: `requesting-code-review` to dispatch a reviewer subagent, and `receiving-code-review` to process the feedback with technical rigor. The result is a REVIEW_REPORT.md that categorizes issues by severity and ensures no Critical items remain before testing begins.

## Core Principle

**Review early, review often.** Catch issues before they compound. A review at this stage catches pattern violations, architectural drift, and edge cases that automated tests would miss — and it costs far less to fix now than during testing.

## Prerequisites

These skills should be installed for the full review experience (they are external dependencies, not inlined):

```bash
npx skills add https://github.com/obra/superpowers --skill requesting-code-review
npx skills add https://github.com/obra/superpowers --skill receiving-code-review
```

### If skills are not installed

The phase supports two modes depending on skill availability:

| Mode | Quality | When to use |
|---|---|---|
| **Dedicated skills** (preferred) | High — structured reviewer agent, categorized output | Skills installed via `npx skills add` |
| **Built-in fallback** | Medium — manual prompt-based review, same categorisation | Skills not available; user chose fallback over skip |

The choice is made in Step 0.1b (Environment Assessment). If you reach this phase without a decision, check skill availability and fall back accordingly — never skip silently.

## Step-by-Step

### 1. Load Development Context

Before dispatching the review, gather the context the reviewer needs:

**Required context:**
- `specs/<需求编号>/spec.md` — The original requirements (what was supposed to be built)
- `specs/<需求编号>/plan.md` — Architecture decisions and design (how it was supposed to be built)
- The git diff or commit range since the specification phase (what was actually built)
- A brief implementation summary in your own words (1-3 paragraphs covering what changed, which files, and any deviation from spec)

**Why this matters**: The reviewer gets precisely crafted context — never your session history. This keeps the reviewer focused on the work product, not your thought process.

### 2. Dispatch Review

**Dedicated skill path** — load `requesting-code-review` skill and invoke the reviewer subagent. The skill's prompt must include:

- **Implementation summary**: What was built, what approach was taken
- **Requirements reference**: Link to spec.md
- **Commit range**: The specific diff to review (e.g., `git diff <spec-commit>..HEAD`)
- **Description**: Any tricky areas or design decisions worth highlighting

**Built-in fallback path** — if the skill is not installed, construct your own prompt manually:

```
You are reviewing code for a feature implementation.

Implementation summary: <1-3 paragraphs>
Requirements: <specs/REQ-XXX/spec.md>
Diff:
<git diff output>

Categorize each finding as:
- Critical: Bug, security issue, or spec violation
- Important: Maintainability concern, missing edge case, pattern inconsistency
- Minor: Style nit, naming suggestion, optional improvement

Return findings grouped by severity.
```

Dispatch this to a general-purpose subagent (or conduct the review yourself as orchestrator). The fallback lacks the dedicated skill's optimized reviewer persona and context-compression, but applies the same categorisation scheme and severity thresholds.

The reviewer returns feedback categorized as:

| Severity | Meaning | Action |
|---|---|---|
| **Critical** | Bug, security issue, or spec violation | Must fix before any further work |
| **Important** | Maintainability concern, missing edge case, pattern inconsistency | Fix before proceeding to testing |
| **Minor** | Style nit, naming suggestion, optional improvement | Note for later; can defer |

### 3. Create REVIEW_REPORT.md

Write the reviewer's feedback into the log directory:

```markdown
# Code Review Report: <Feature Name>

**Date**: YYYY-MM-DD
**Reviewer**: request-code-review (obra/superpowers)

## Summary

- **Critical**: 2
- **Important**: 3
- **Minor**: 5
- **Total**: 10

## Critical (fix immediately)

### C-1: [Short title]
- **File**: `src/path/to/file.ts:L42`
- **Issue**: What the reviewer found
- **Verdict**: ✅ Confirmed / ❌ Rejected (after verification)
- **Fix**: What was done (leave blank until fixed)

### C-2: ...

## Important (fix before proceeding)

### I-1: ...

## Minor (note for later)

- M-1: ...
```

**Do NOT copy feedback verbatim without analysis.** Every item must go through verification first (step 4).

### 4. Process Feedback

This step is **identical for both paths** — whether the findings came from the dedicated skill or the fallback, they must be processed with the same rigor.

Load the `receiving-code-review` skill (or follow its principles manually in the fallback path). For each item in the review report:

**4.1 Verify against actual code**
- Is the reviewer's claim actually true? Check the codebase.
- Does existing test coverage contradict the reviewer?
- Does the broader architecture context invalidate the concern?

**4.2 Clarify before acting**
- If an item is unclear or lacks context, do NOT implement blindly.
- Either re-read the relevant code to understand the concern, or ask for clarification (via the user if human review is involved).

**4.3 Push back when appropriate**
Reasons to push back (i.e., mark as "Won't Fix" with reasoning):

| Reason | Example |
|---|---|
| **Breaks functionality** | Reviewer suggests extracting a shared utility, but the two callers have divergent semantics |
| **Lacks context** | Reviewer flags missing null check, but the value is guaranteed non-null by a type guard above |
| **Violates YAGNI** | Suggests adding abstraction for a use case that doesn't exist yet |
| **Conflicts with spec** | Reviewer suggests a different approach than what spec/plan explicitly decided |
| **Out of scope** | Reviewer flags pre-existing code that this feature didn't touch |

When pushing back, write the reasoning into REVIEW_REPORT.md (e.g., "❌ Rejected — type guard at line 38 already guarantees non-null").

**4.4 Fix in priority order**

Fix all items in this strict order:
1. Critical items first (all of them)
2. Important items (all of them)
3. Minor items (optional — only if time permits and the fix is trivial)

For each fix:
- Make the minimal change required (no refactoring while fixing)
- Verify the fix works (run the relevant test or check behavior)
- Do NOT batch multiple fixes into one edit without individual verification

**4.5 Acknowledge through action**
- Do NOT say "thanks" or "good catch" — just fix the issue and describe what changed.
- Update REVIEW_REPORT.md with the fix description for each item.

### 5. Re-review (dedicated skill path only)

This step requires the `requesting-code-review` skill. If using the built-in fallback, skip re-review — the fallback is intentionally lighter. The phase gate (no Critical items remaining) still applies.

If any Critical items were found and fixed, re-run the dispatch step with the updated diff to confirm fixes.

- If re-review returns zero Critical items → proceed
- If re-review still finds Critical items → loop back to step 4
- After 3 re-review cycles without clearing all Critical items → pause and ask the user

### 6. Commit

```bash
git add -A
git commit -m "code-review-fix: <summary of what was fixed>"
```

If no issues were found (clean review), commit the REVIEW_REPORT.md separately:
```bash
git add -A
git commit -m "code-review: clean review — no issues found"
```

### 7. Phase Gate

Before declaring this phase complete, confirm:

- [ ] All Critical items resolved (fixed or explicitly rejected with reasoning)
- [ ] All Important items resolved
- [ ] REVIEW_REPORT.md written and committed
- [ ] Re-review passed (if applicable)
- [ ] No uncommitted changes

**Output artifacts:**
- `<project>/logs/<YYYYMMDD>-<N>/REVIEW_REPORT.md`
- Code fixes from review feedback

## When to Skip Code Review

Code review adds value in proportion to code complexity. Skip or simplify in these scenarios:

- **Trivial change** (one-line config change, typo fix): skip entirely
- **Generated boilerplate** (scaffolding, CRUD templates): quick scan only, skip detailed review
- **Hotfix in production**: review after deploy, not before

## Common Pitfalls

| Pitfall | How to avoid |
|---|---|
| **Blindly accepting all feedback** | Every item must be verified against actual code before acting |
| **Reviewing too late** | Review after each task, not just at feature completion |
| **Reviewing too much code at once** | If the diff exceeds ~500 lines, split into logical chunks and review each |
| **Debating minor items** | If a Minor item has no clear correctness argument, defer it — don't spend time arguing |
| **Treating reviewer as authority** | The reviewer is a peer providing a second opinion. You own the code. |
