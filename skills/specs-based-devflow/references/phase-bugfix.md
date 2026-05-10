# Bug Fix Phase — Detailed Guide

This phase addresses all failed test cases from the test report. Each fix is verified immediately using Playwright or curl, and the test report is updated with fix status.

## Goal

Fix all failed test cases and update the test report to reflect which bugs are resolved, enabling the regression phase to re-verify them.

## Step-by-Step

### 1. Read the Test Report

Load `logs/<YYYYMMDD>-<N>/TEST_REPORT.md` and extract all failed test cases.

Prioritize by severity:
1. **P1 (Critical)**: Feature doesn't work at all, data loss, security issue
2. **P2 (High)**: Major feature broken but workaround exists
3. **P3 (Medium/Low)**: Minor issues, cosmetic, edge cases

Create a fix plan:
```
Bug Fix Plan:
1. [P1] TC-005: <description> — estimated root cause: <guess>
2. [P1] TC-008: <description> — estimated root cause: <guess>
3. [P2] TC-012: <description> — estimated root cause: <guess>
...
```

### 2. Fix Bugs in Priority Order

For each failed test case:

**2.1 Reproduce the bug:**
- Backend: Re-run the curl command that failed
- Frontend: Re-navigate to the page and perform the failing action
- Confirm the bug still exists

**2.2 Diagnose the root cause:**
- Read the error message carefully
- Check the relevant code (controller, service, component)
- Check the console output for errors
- Compare the code against the spec/contracts to find discrepancies

**2.3 Implement the fix:**
- Make the minimal change needed to fix the issue
- Don't refactor or improve unrelated code while fixing bugs
- If the fix requires a spec change (e.g., the test expectation was wrong), document it

**2.4 Verify the fix immediately:**

Use Playwright for frontend bugs:
```python
# Navigate to the affected page
navigate("http://localhost:3000/feature")

# Trigger the previously failing action
fill("#input", "test data")
click("button[type=submit]")

# Verify the fix works
wait_for_text("Expected success message")

# Check console for new errors
console_messages = playwright_browser_console_messages(level="error")
# Should be empty (or only pre-existing errors)
```

Use curl for backend bugs:
```bash
# Re-run the previously failing API call
curl -s -w "\nHTTP_CODE:%{http_code}" \
  -X POST http://localhost:8080/api/resource \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"field":"value"}'
# Verify the response now matches expectations
```

**2.5 Update the test report:**

For each fixed bug, update the `Fix status` field in `TEST_REPORT.md`:
```markdown
### TC-005: <Test Case Title>
**Priority**: P1
**Expected**: <what should happen>
**Actual**: <what actually happened>
**Root cause**: <what was wrong in the code>
**Fix applied**: <what was changed>
**Fix verified**: YES — <how it was verified>
**Fix status**: FIXED
```

For bugs that can't be fixed immediately:
```markdown
### TC-008: <Test Case Title>
**Fix status**: DEFERRED — <reason for deferring>
```

### 3. Live Debugging During Bug Fixes

Use Playwright to assist with debugging:

**Console-driven debugging:**
1. Open the affected page in Playwright
2. Trigger the failing functionality
3. Check the browser console for JavaScript errors
4. Fix the error in code
5. Refresh and re-test

**Network-driven debugging:**
1. Open the affected page
2. Trigger the API call
3. Check the network response (status code, body)
4. If the API returns an error, fix the backend
5. If the API succeeds but the UI is wrong, fix the frontend

**Common bug patterns and fixes:**
- **401 Unauthorized**: Token expired or not sent — check auth header
- **404 Not Found**: Wrong API path — check route configuration
- **422 Validation Error**: Missing or invalid request body — check field names and types
- **500 Internal Server Error**: Backend exception — check server logs for stack trace
- **UI not updating**: State management issue — check reactivity or re-rendering
- **CORS error**: Backend not allowing frontend origin — check CORS configuration

### 4. Handle Unfixable Bugs

If a bug can't be fixed in this phase:

**Root cause is a design flaw:**
- The spec itself may be wrong
- Document the issue and suggest going back to specification
- Mark the test case as `SPEC_ISSUE` in the report

**Root cause is an external dependency:**
- Third-party service is down or has a bug
- Document the dependency issue
- Mark the test case as `EXTERNAL_BLOCKER`

**Root cause is too complex to fix quickly:**
- The fix requires architectural changes
- Document the proposed fix approach
- Mark the test case as `DEFERRED` with a note explaining why

### 5. Update DEV_CHECKLIST.md

If a `DEV_CHECKLIST.md` exists from the development phase, add a bug fix section:

```markdown
## Bug Fixes
- [x] BF-001: Fix TC-005 — <description of the fix>
- [x] BF-002: Fix TC-008 — <description of the fix>
- [ ] BF-003: Fix TC-012 — <deferred, reason>
```

### 6. Commit Bug Fixes

```bash
git add -A
git commit -m "bugfix: fix X of Y test failures for <feature-name>

Fixed:
- TC-005: <short description>
- TC-008: <short description>

Deferred:
- TC-012: <reason>"
```

### 7. Phase Report

```
## Bug Fix Phase Complete

**Bugs fixed**: X/Y
**Deferred**: Z

**Fixed test cases:**
- TC-005: <description> — FIXED
- TC-008: <description> — FIXED

**Remaining failures:**
- TC-012: <description> — DEFERRED (reason)

**Updated test report**: logs/<YYYYMMDD>-<N>/TEST_REPORT.md

**Next phase:** Regression Testing
**What it will do:** Re-test all fixed bugs to confirm they're resolved, and spot-check passing tests for regressions

Proceed? (yes / skip / stop / modify)
```
