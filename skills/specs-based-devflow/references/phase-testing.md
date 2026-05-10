# Testing Phase — Detailed Guide

This phase systematically verifies the implementation against the test cases. It produces a test report documenting pass/fail status for every test case, which drives the bug fix and regression phases.

## Goal

Execute all test cases from `test-cases.md` and produce a detailed `TEST_REPORT.md`.

## Step-by-Step

### 1. Build the Project

Ensure the project is compiled and ready:

**Frontend (if applicable):**
```bash
# Node.js
npm run build

# Verify build succeeded
echo $?  # Should be 0
```

**Backend (if applicable):**
```bash
# Java/Maven
mvn compile -q

# Java/Gradle
gradle build -x test
```

If the build fails, fix it before continuing. A failing build means no testable software.

### 2. Start the Project

Start both frontend and backend servers (if the project has both).

**Backend startup (Java/Spring Boot specific):**

Check for `spring-boot-devtools` in the project:
```bash
# Check if devtools is a dependency
grep -r "spring-boot-devtools" pom.xml build.gradle 2>/dev/null
```

If devtools is present:
- The server may already be running from the development phase
- If not, start with: `mvn spring-boot:run`
- Devtools enables automatic restart on code changes

If devtools is not present:
- Start normally: `mvn spring-boot:run`
- Code changes require manual restart

**Frontend startup:**
```bash
npm run dev
# Note the URL (typically http://localhost:3000 or similar)
```

**Verify both are running:**
```bash
# Backend health check
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/actuator/health 2>/dev/null || \
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/ 2>/dev/null

# Frontend health check
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/ 2>/dev/null
```

### 3. Read Test Cases

Read `specs/<feature>/test-cases.md` thoroughly. Understand:
- Total number of test cases
- Priority distribution (P1/P2/P3)
- Types of tests (API, UI, integration)
- Required preconditions
- Dependencies between test cases

### 4. Create Test Log Directory

```bash
# Use the same LOG_DIR from development, or create a new one
TODAY=$(date +%Y%m%d)
EXISTING=$(ls -d logs/${TODAY}-* 2>/dev/null | sort -r | head -1)
if [ -n "$EXISTING" ]; then
  LAST_NUM=$(echo "$EXISTING" | grep -oE '[0-9]+$')
  NEXT_NUM=$((LAST_NUM + 1))
else
  NEXT_NUM=1
fi
TEST_DIR="logs/${TODAY}-${NEXT_NUM}"
mkdir -p "$TEST_DIR"
```

### 5. Create TEST_CHECKLIST.md

Generate `<TEST_DIR>/TEST_CHECKLIST.md` from test cases:

```markdown
# Test Checklist: <Feature Name>

**Date**: YYYY-MM-DD
**Tester**: AI-assisted
**Environment**: <backend URL> / <frontend URL>

## Backend API Tests
- [ ] TC-001: <test case title>
- [ ] TC-002: <test case title>

## Frontend UI Tests
- [ ] TC-010: <test case title>
- [ ] TC-011: <test case title>

## Integration Tests
- [ ] TC-020: <test case title>

## Summary
| Category | Total | Pass | Fail | Skip |
|----------|-------|------|------|------|
| Backend  | X     | X    | X    | X    |
| Frontend | X     | X    | X    | X    |
| Integration | X  | X    | X    | X    |
```

### 6. Backend API Testing via Curl

**Step 6.1: Obtain Auth Token (If Applicable)**

First, determine the authentication mechanism:
- Check `contracts/` for auth endpoints
- Check the spec for login flow
- Look at existing API tests or documentation

```bash
# Common login patterns:

# JWT token login
TOKEN=$(curl -s -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}' | jq -r '.token')

# If the response wraps the token differently, adapt:
# jq -r '.data.token'
# jq -r '.access_token'

echo "Token obtained: ${TOKEN:0:20}..."
```

**If no auth endpoint exists**, skip the token step and test without authorization headers.

**If the login requires specific credentials**, ask the user for test account details.

**Step 6.2: Test Each API Endpoint**

For each backend test case in `test-cases.md`:

```bash
# GET request
curl -s -w "\nHTTP_CODE:%{http_code}" \
  http://localhost:8080/api/resource \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"

# POST request
curl -s -w "\nHTTP_CODE:%{http_code}" \
  -X POST http://localhost:8080/api/resource \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"field1":"value1","field2":"value2"}'

# PUT request
curl -s -w "\nHTTP_CODE:%{http_code}" \
  -X PUT http://localhost:8080/api/resource/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"field1":"updated"}'

# DELETE request
curl -s -w "\nHTTP_CODE:%{http_code}" \
  -X DELETE http://localhost:8080/api/resource/1 \
  -H "Authorization: Bearer $TOKEN"
```

**For each test case, record:**
- Request: method + URL + body
- Response: status code + response body
- Expected vs Actual: does the response match the expected result?
- Status: PASS / FAIL

**Save API test results** to `<TEST_DIR>/api-test-results.json`:
```json
{
  "test_case": "TC-001",
  "method": "POST",
  "url": "/api/resource",
  "request_body": {"field1": "value1"},
  "expected_status": 201,
  "actual_status": 201,
  "expected_body_contains": "id",
  "actual_body": {"id": 1, "field1": "value1"},
  "status": "PASS"
}
```

**Test all endpoints from `contracts/`** (if available):
- Each CRUD endpoint: create, read, update, delete
- Validation: submit invalid data, verify error responses
- Authorization: test without token, test with wrong role
- Edge cases: empty lists, not-found resources, duplicate entries

### 7. Frontend UI Testing via Playwright

For each frontend test case in `test-cases.md`:

**Step 7.1: Navigate to Feature Page**

```python
# Navigate to the feature's route
navigate("http://localhost:3000/feature-route")
wait_for_text("Expected Page Title")
```

**Step 7.2: Execute Test Scenario**

For each test case:
1. Set up preconditions (navigate, fill form, etc.)
2. Perform the test action
3. Verify the expected result
4. Check console for errors
5. Take a screenshot (especially for failures)

**Common test patterns:**

```python
# Form submission test
fill("#name", "Test Name")
fill("#email", "test@example.com")
click("button[type=submit]")
wait_for_text("Success")  # or expected error message
screenshot("logs/TC-010-form-submit.png")

# List view test
navigate("http://localhost:3000/items")
wait_for_text("Items List")
# Verify list items appear
snapshot()  # Get accessibility snapshot to verify content

# Delete confirmation test
click("button.delete")
wait_for_text("Are you sure?")
click("button.confirm")
wait_for_text("Deleted successfully")

# Error state test
fill("#email", "invalid-email")
click("button[type=submit]")
wait_for_text("Invalid email")
screenshot("logs/TC-012-validation-error.png")
```

**Step 7.3: Capture Console Errors**

After each test action, check for console errors:
```python
console_messages = playwright_browser_console_messages(level="error")
# If errors found, record them in the test results
```

**Step 7.4: Save Evidence**

For each test case, save:
- Screenshot of the final state (or error state)
- Console errors (if any)
- Network errors (if any)

### 8. Generate Test Report

After all test cases are executed, generate `<TEST_DIR>/TEST_REPORT.md`:

```markdown
# Test Report: <Feature Name>

**Date**: YYYY-MM-DD
**Environment**: Backend at <URL>, Frontend at <URL>
**Test cases executed**: X/Y

## Summary

| Category | Total | Pass | Fail | Skip |
|----------|-------|------|------|------|
| Backend API | X | X | X | X |
| Frontend UI | X | X | X | X |
| Integration | X | X | X | X |
| **Total** | **X** | **X** | **X** | **X** |

## Failed Test Cases

### TC-005: <Test Case Title>
**Priority**: P1
**Type**: Functional
**Expected**: <what should happen>
**Actual**: <what actually happened>
**Error details**: <error message, stack trace, or observation>
**Evidence**: <screenshot or API response>
**Fix status**: PENDING

### TC-012: <Test Case Title>
...

## Passed Test Cases

- TC-001: <title> — PASS
- TC-002: <title> — PASS
...

## Skipped Test Cases

- TC-020: <title> — SKIP (reason: <why skipped>)

## Recommendations

1. <any patterns noticed across failures>
2. <suggested prioritization for bug fixes>
```

### 9. Save Test Evidence

All test evidence goes in `<TEST_DIR>/`:
```
logs/<YYYYMMDD>-<N>/
├── TEST_CHECKLIST.md
├── TEST_REPORT.md
├── api-test-results.json
├── screenshots/
│   ├── TC-010-pass.png
│   ├── TC-012-fail-validation.png
│   └── ...
└── console-errors.log
```

### 10. Commit Test Artifacts

```bash
git add logs/<YYYYMMDD>-<N>/
git commit -m "testing: complete test report for <feature-name> — X pass, Y fail"
```

### 11. Phase Report

```
## Testing Phase Complete

**Test cases executed**: X/Y
**Results**: X PASS, Y FAIL, Z SKIP

**Critical failures (P1):**
- TC-005: <description>
- TC-008: <description>

**High failures (P2):**
- TC-012: <description>

**Test report**: logs/<YYYYMMDD>-<N>/TEST_REPORT.md

**Next phase:** Bug Fix
**What it will do:** Fix all failed test cases, prioritized by severity

Proceed? (yes / skip / stop / modify)
```
