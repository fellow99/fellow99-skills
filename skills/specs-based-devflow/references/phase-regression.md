# Regression Testing Phase — Detailed Guide

This phase re-tests all bugs that were marked as FIXED in the bug fix phase, and spot-checks a selection of previously passing tests to ensure no new regressions were introduced by the fixes.

## Goal

Confirm that all bug fixes work correctly and that no previously working functionality was broken by the fixes.

## Step-by-Step

### 1. Read the Updated Test Report

Load `logs/<YYYYMMDD>-<N>/TEST_REPORT.md` and extract:

- All test cases with `Fix status: FIXED` — these must be re-tested
- All test cases with `Fix status: PENDING` or `DEFERRED` — these are still broken, skip them
- A selection of previously PASS test cases — spot-check these for regressions

Create a regression test plan:
```
Regression Test Plan:
MUST RE-TEST (previously FIXED):
- TC-005: <description>
- TC-008: <description>

SPOT-CHECK (previously PASS):
- TC-001: <description> — sanity check
- TC-003: <description> — related to fixed area
- TC-007: <description> — core functionality
```

**How many spot-checks?** At minimum, re-test:
- All test cases in the same feature area as the bug fixes
- All P1 test cases (even if they previously passed)
- Any test cases that exercise code modified during bug fixes

### 2. Verify Environment

Ensure the project is still running:
```bash
# Check backend
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/

# Check frontend
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/
```

If either is down, restart them (see the testing phase guide for startup commands).

If bug fixes changed backend code:
- For Spring Boot with devtools: the server should have auto-restarted
- For Spring Boot without devtools: restart manually: `mvn spring-boot:run`
- For Node.js: the server should have auto-restarted via nodemon

### 3. Re-test Fixed Bugs

For each test case marked as FIXED:

**Backend API regression:**
```bash
# Re-run the exact same curl command that originally failed
# Then verify it now passes

# Example: TC-005 originally returned 500, now should return 201
curl -s -w "\nHTTP_CODE:%{http_code}" \
  -X POST http://localhost:8080/api/resource \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"field":"value"}'
# Expected: HTTP_CODE:201 (previously was 500)
```

**Frontend UI regression:**
```python
# Navigate to the affected page
navigate("http://localhost:3000/feature")

# Re-execute the failing scenario
fill("#input", "test data")
click("button[type=submit]")

# Verify the fix is still working
wait_for_text("Expected success message")

# Check for new console errors
console_messages = playwright_browser_console_messages(level="error")
# Record any new errors
```

**For each re-tested case, record:**
- Original failure description
- Fix that was applied
- Regression test result: PASS (fix confirmed) / FAIL (fix didn't work or regressed)

### 4. Spot-Check Previously Passing Tests

Select a subset of previously PASS test cases and re-run them:

**Backend spot-checks:**
```bash
# Run a few key API calls that should still work
curl -s -w "\nHTTP_CODE:%{http_code}" \
  http://localhost:8080/api/resource \
  -H "Authorization: Bearer $TOKEN"
# Should still return 200 with data
```

**Frontend spot-checks:**
```python
# Navigate to key pages and verify they still load
navigate("http://localhost:3000/home")
wait_for_text("Dashboard")

navigate("http://localhost:3000/feature")
wait_for_text("Feature Title")

# Try a basic CRUD operation
click("button.add-new")
wait_for_text("Create New")
```

**If a previously passing test now fails:**
- This is a REGRESSION — a bug fix introduced a new bug
- Document it immediately
- This takes priority: the bug fix that caused the regression should be revisited
- Do NOT proceed past this phase with known regressions

### 5. Update Test Report

Update `TEST_REPORT.md` with regression results:

```markdown
### TC-005: <Test Case Title>
**Priority**: P1
**Original failure**: <description>
**Fix applied**: <description>
**Fix verified**: YES
**Fix status**: FIXED
**Regression test**: PASS ✓

### TC-008: <Test Case Title>
**Priority**: P1
**Original failure**: <description>
**Fix applied**: <description>
**Fix verified**: YES
**Fix status**: FIXED
**Regression test**: PASS ✓

## Regression Test Results

| Test Case | Original | After Fix | Regression | Notes |
|-----------|----------|-----------|------------|-------|
| TC-005    | FAIL     | PASS      | PASS ✓     | Fix confirmed |
| TC-008    | FAIL     | PASS      | PASS ✓     | Fix confirmed |
| TC-001    | PASS     | —         | PASS ✓     | Spot-check, no regression |
| TC-003    | PASS     | —         | PASS ✓     | Spot-check, no regression |

**New regressions found**: 0
```

If regressions were found:
```markdown
### NEW REGRESSION: TC-003
**Previously**: PASS
**Now**: FAIL
**Likely cause**: Bug fix for TC-008 modified shared utility
**Action needed**: Revisit BF-002 fix
```

### 6. Handle Regressions

If any regressions are found:

1. **STOP** — do not proceed past this phase
2. Go back to the bug fix phase
3. Re-examine the fix that caused the regression
4. Apply a more targeted fix that doesn't break existing functionality
5. Re-run the regression tests

If after 3 attempts the regression can't be resolved without breaking the original fix:
- Report the situation to the user
- This may indicate a design conflict that requires spec revision
- Let the user decide: accept the regression, revise the spec, or redesign the fix

### 7. Commit Regression Results

```bash
git add -A
git commit -m "regression: complete regression testing for <feature-name> — all X fixed bugs confirmed, 0 new regressions"
```

### 8. Final Phase Report

```
## Regression Testing Phase Complete

**Fixed bugs re-tested**: X
**Confirmed fixed**: X
**Still broken**: 0
**New regressions**: 0

**Spot-checks performed**: Y
**Spot-check results**: All PASS

**Overall test status**:
- Total test cases: Z
- PASS: X
- FAIL: 0 (or remaining deferred issues)
- SKIP: 0

**Updated test report**: logs/<YYYYMMDD>-<N>/TEST_REPORT.md

---
## 🎉 Full Development Flow Complete

**Feature**: <feature-name>
**Branch**: <branch-name>
**Phases completed**: Specification → Development → Testing → Bug Fix → Regression

**Final artifacts:**
- specs/<feature>/spec.md
- specs/<feature>/plan.md
- specs/<feature>/tasks.md
- specs/<feature>/test-cases.md
- logs/<YYYYMMDD>-<N>/DEV_CHECKLIST.md
- logs/<YYYYMMDD>-<N>/TEST_REPORT.md

**All test cases pass.** The feature is ready for code review and merge.
```

If there are still deferred bugs:
```
**Remaining known issues:**
- TC-012: <description> — DEFERRED (reason)

These should be tracked as follow-up work items.
```
