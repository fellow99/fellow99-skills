# Development Phase — Detailed Guide

This phase implements the feature according to the specification documents. It uses `speckit-implement` as the primary execution engine, with live debugging via Playwright for frontend features.

## Goal

Transform `tasks.md` into working code, tracked via `DEV_CHECKLIST.md`.

## Step-by-Step

### 1. Context Loading

Read these documents before writing any code:

**Required:**
- `specs/<feature>/spec.md` — What to build
- `specs/<feature>/plan.md` — How to build it (tech stack, architecture, file structure)
- `specs/<feature>/tasks.md` — What order to build it in

**Optional (if they exist):**
- `specs/<feature>/data-model.md` — Entity definitions
- `specs/<feature>/contracts/` — API endpoint specs
- `specs/<feature>/research.md` — Technical decisions and rationale
- `specs/<feature>/quickstart.md` — Integration scenarios

Also scan the broader project for context:
- Existing code patterns (naming conventions, error handling, auth flow)
- Similar features already implemented (reference their structure)
- Project README for development conventions

### 2. Create Development Log Directory

```bash
# Determine the next sequence number for today
TODAY=$(date +%Y%m%d)
EXISTING=$(ls -d logs/${TODAY}-* 2>/dev/null | sort -r | head -1)
if [ -n "$EXISTING" ]; then
  LAST_NUM=$(echo "$EXISTING" | grep -oE '[0-9]+$')
  NEXT_NUM=$((LAST_NUM + 1))
else
  NEXT_NUM=1
fi
LOG_DIR="logs/${TODAY}-${NEXT_NUM}"
mkdir -p "$LOG_DIR"
```

### 3. Initialize DEV_CHECKLIST.md

Create `<LOG_DIR>/DEV_CHECKLIST.md` with this structure:

```markdown
# Development Checklist: <Feature Name>

**Date**: YYYY-MM-DD
**Branch**: <branch-name>
**Feature directory**: specs/<feature>/

## Progress

### Phase 1: Setup
- [ ] T001: <task description> — <file path>
- [ ] T002: <task description> — <file path>

### Phase 2: Foundational
- [ ] T003: <task description> — <file path>

### Phase 3: User Story 1 — <story title>
- [ ] T004: <task description> — <file path>

## Dev Log
| Time | Action | Result | Notes |
|------|--------|--------|-------|
| HH:MM | What I did | success/fail | Observations |
```

**Update this file as you work** — check off tasks, add log entries. This creates an audit trail.

### 4. Open Frontend with Playwright (If Applicable)

If the project has a frontend and the dev server is running:

1. Open the frontend URL in Playwright
2. Log in (use test credentials or ask the user)
3. Navigate to the home page
4. Take a screenshot to confirm the app loaded correctly

```python
# Playwright flow (conceptual)
navigate("http://localhost:XXXX")
fill("#username", "test_user")
fill("#password", "test_pass")
click("button[type=submit]")
wait_for_url("**/home")
screenshot("logs/home-before-dev.png")
```

**If login requires specific credentials:**
- Check README or `.env.example` for test user info
- Ask the user if no test credentials are documented
- Don't hardcode credentials — use environment variables or ask each time

### 5. Execute Implementation

Use `speckit-implement` to drive the implementation, or manually follow `tasks.md`.

**When using speckit-implement:**
- The skill will process tasks phase by phase
- It checks for checklist completion before starting
- It creates/verifies ignore files for the project
- It follows a TDD approach (tests before code) when applicable

**When implementing manually (or when speckit-implement needs guidance):**

Follow the task order from `tasks.md`:
1. **Setup phase**: Project configuration, dependencies, scaffolding
2. **Foundational phase**: Shared utilities, base classes, database migrations
3. **User story phases**: Feature implementation in priority order
4. **Polish phase**: Cross-cutting concerns, optimization, documentation

For each task:
1. Read the task description and file paths from `tasks.md`
2. Read the relevant section of `plan.md` for implementation guidance
3. Implement the code
4. Check off the task in `DEV_CHECKLIST.md`
5. If the task has tests, run them

### 6. Live Debugging with Playwright

During frontend development, use Playwright to verify changes in real-time.

**Debugging workflow:**
1. After making code changes, wait for hot-reload (or manually refresh)
2. Navigate to the relevant route in Playwright
3. Trigger the functionality you just implemented:
   - Fill forms and submit
   - Click buttons
   - Navigate between pages
4. Check the browser console for errors:
   ```
   # Get console messages
   playwright_browser_console_messages(level="error")
   ```
5. If errors appear:
   - Note the error in `DEV_CHECKLIST.md` dev log
   - Fix the error in code
   - Re-verify in Playwright
6. Take screenshots of working features for evidence

**Key debugging patterns:**
- **CRUD operations**: Create → Read → Update → Delete, verify each step
- **Form validation**: Submit with empty fields, invalid data, boundary values
- **Navigation**: Visit each new route, verify redirects work
- **Error states**: Trigger API errors, verify error messages display
- **Loading states**: Verify loading indicators appear during async operations

### 7. Backend Development Notes

For backend API development:

**If Java/Spring Boot:**
- Check if `spring-boot-devtools` is active (auto-restart on changes)
- If not active, manually restart the server after significant changes
- Use `mvn compile` to check for compilation errors before running

**If Node.js:**
- Most Node.js servers auto-restart with nodemon or ts-node-dev
- Check `package.json` scripts for the dev command

**API development workflow:**
1. Define the endpoint per `contracts/`
2. Implement the controller/route handler
3. Implement the service/business logic
4. Implement data access/repository layer
5. Test with curl:
   ```bash
   # Get auth token first if needed
   TOKEN=$(curl -s -X POST http://localhost:8080/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"test","password":"test"}' | jq -r '.token')
   
   # Test the new endpoint
   curl -v http://localhost:8080/api/resource \
     -H "Authorization: Bearer $TOKEN"
   ```

### 8. Handle Implementation Issues

If you encounter problems during development:

**Build errors:**
- Fix immediately — don't accumulate compilation errors
- Run the build after every significant change
- If a build error blocks progress for >3 attempts, consult Oracle or ask the user

**Design issues (the spec doesn't match reality):**
- Document the discrepancy in `DEV_CHECKLIST.md`
- If minor: make a reasonable adaptation and note it
- If major: pause and ask the user — the spec may need revision
- Don't silently deviate from the spec without documenting why

**Missing dependencies:**
- Check if the dependency is already in `package.json`/`pom.xml`
- If not, add it with the appropriate version
- Note the addition in `DEV_CHECKLIST.md`

### 9. Save Temporary Scripts

Any helper scripts created during development (data seeding, test data generation, migration scripts, etc.) should be saved to the log directory:

```
<project>/logs/<YYYYMMDD>-<N>/
├── seed-test-data.sh      # Script to seed test data
├── migrate-v2.sql          # Database migration
├── api-test.sh             # Quick API test script
└── DEV_CHECKLIST.md        # Development tracking
```

These scripts are useful for the testing phase and for future reference.

### 10. Commit Development Work

```bash
git add -A
git commit -m "development: implement <feature-name> — <brief description of what was built>"
```

If the development was large, consider committing in logical chunks:
- `development: add <feature> data model and migrations`
- `development: add <feature> API endpoints`
- `development: add <feature> frontend components`
- `development: integrate <feature> with existing modules`

### 11. Phase Report

```
## Development Phase Complete

**Feature**: <feature-name>
**Tasks completed**: X/Y (from tasks.md)

**Files created/modified:**
- <list key files>

**Dev log**: logs/<YYYYMMDD>-<N>/DEV_CHECKLIST.md

**Issues encountered:**
- <list any issues and how they were resolved>

**Known limitations:**
- <list anything incomplete or deferred>

**Next phase:** Testing
**What it will do:** Run test cases against the implementation, both API and UI

Proceed? (yes / skip / stop / modify)
```
