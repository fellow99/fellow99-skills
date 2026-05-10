# Preparation Phase — Detailed Guide

This phase establishes the environment, verifies tools, and ensures the project is ready for the specification-development-testing pipeline. Completing this phase thoroughly prevents blockers later.

## Checklist

Run through each item. If any check fails, report it to the user and ask how to proceed before continuing.

### 1. Speckit Tool Verification

List all available speckit skills and confirm they're accessible. The canonical set is:

| Skill | Purpose | Required? |
|---|---|---|
| `speckit-specify` | Create feature spec from requirement | Yes |
| `speckit-clarify` | Reduce ambiguity in spec | Recommended |
| `speckit-plan` | Generate technical plan | Yes |
| `speckit-tasks` | Generate task list | Yes |
| `speckit-implement` | Execute implementation | Yes |
| `speckit-analyze` | Cross-artifact consistency check | Optional |
| `speckit-checklist` | Requirements quality checklists | Optional |
| `speckit-constitution` | Project governance setup | Optional |
| `speckit-baseline` | Spec from existing code | Situational |
| `speckit-taskstoissues` | Convert tasks to GitHub issues | Optional |

**If the user specified alternative specification tools** (not speckit), record which tools they want and adapt the specification phase accordingly. The phase structure remains the same; only the tool invocations change.

Report to the user:
```
Speckit skills available: [list what was found]
Missing: [list any gaps, or "none"]
Using: speckit / [alternative tool name]
```

### 2. Working Directory

Default: current working directory. User override takes precedence.

Verify:
- [ ] Directory exists and is accessible
- [ ] Read/write permissions are available

### 3. Git Status

```bash
# Check if git repo exists
git rev-parse --git-dir 2>/dev/null

# If yes, get current branch
git branch --show-current

# Get remote info
git remote -v

# Check for uncommitted changes
git status --short
```

Report:
```
Git repository: yes/no
Current branch: <name>
Remote: <url> or "none"
Uncommitted changes: <count> files
```

If no git repo:
- Warn the user that phase commits won't work
- Ask: "Should I initialize a git repo? (yes/no)"
- If yes: `git init && git add -A && git commit -m "initial: existing project state"`

If the user specified a target branch:
```bash
git fetch --all --prune
git checkout -b <branch-name>  # Create new branch
# OR
git checkout <branch-name>     # Switch to existing branch
```

If there are uncommitted changes:
- Warn the user
- Ask whether to commit them first or stash them

### 4. Specs Directory

Look for specification directories in this order:
1. `specs/` — standard speckit location
2. `.specify/` — speckit configuration directory (indicates speckit is set up)
3. `docs/specs/` — alternative common location
4. Any directory containing `spec.md` files

```bash
# Check for specs directory
ls -d specs/ .specify/ docs/specs/ 2>/dev/null

# Search for existing spec files
find . -name "spec.md" -type f 2>/dev/null | head -20
```

Report:
```
Specs directory: <path> or "not found"
.specify directory: <path> or "not found"
Existing specs: <count> feature specs found
```

If no specs directory exists:
- **This is a blocker for speckit-based workflow.** The `speckit-specify` skill requires `.specify/scripts/bash/create-new-feature.sh` and `.specify/templates/spec-template.md` to function.
- Ask the user: "No specs directory found. Speckit requires a `.specify/` setup. Should I:"
  1. Set up `.specify/` (if the project supports it)
  2. Use a different specification approach
  3. Specify a custom directory path

### 5. README Review

If `README.md` exists, read it and extract:
- Project name and purpose
- Tech stack (languages, frameworks, databases)
- How to build and run
- Project structure overview
- Any development conventions mentioned

Summarize findings for context — this informs later phases.

### 6. Build Verification

Detect and run the build system:

| Build File | Command | Notes |
|---|---|---|
| `package.json` | `npm run build` | Check `scripts.build` field first |
| `pom.xml` | `mvn compile -q` | Skip tests with `-DskipTests` for speed |
| `build.gradle` | `gradle build -x test` | Exclude tests for initial build check |
| `Makefile` | `make` | Standard make |
| `go.mod` | `go build ./...` | Build all packages |
| `Cargo.toml` | `cargo build` | Rust build |
| `pyproject.toml` | Skip | Python doesn't have a standard compile step |

If the build fails:
- Report the error output
- Ask: "Build failed. Should I (1) proceed anyway, (2) fix the build first, or (3) stop?"
- If the user says proceed, note that the build is broken — testing phase may be affected

### 7. Development Environment Startup

Try starting the dev server. This is needed for Playwright-based testing and debugging in later phases.

| Project Type | Start Command | Notes |
|---|---|---|
| Node.js (React, Vue, etc.) | `npm run dev` or `npm start` | Usually hot-reload on port 3000/5173/8080 |
| Java/Spring Boot | `mvn spring-boot:run` | Check for devtools dependency first |
| Java/Spring Boot + Devtools | `mvn spring-boot:run` with devtools in pom.xml | Auto-restart on changes — preferred for development |
| Go | `go run .` | Hot-reload via air if configured |
| Python/Django | `python manage.py runserver` | Default port 8000 |
| Python/FastAPI | `uvicorn main:app --reload` | Hot-reload enabled |
| Python/Flask | `flask run --debug` | Debug mode |

**For Java/Spring Boot specifically:**
1. Check `pom.xml` for `spring-boot-devtools` dependency
2. If present, prefer this mode — it enables hot reload
3. If not present, note that code changes require server restart

**If startup requires environment variables or credentials:**
- Do NOT guess at values
- Ask the user for: database URLs, API keys, secret keys, etc.
- Check for `.env.example` or `.env.template` files that document required variables

**If the dev server starts successfully:**
- Note the URL (e.g., `http://localhost:3000`)
- Verify it responds: `curl -s -o /dev/null -w "%{http_code}" <URL>`
- This URL will be used for Playwright testing and debugging

**If the dev server fails to start:**
- Report the error
- Ask the user for help
- The development and testing phases will be blocked until the server runs

### 8. Summary Report

After all checks, present a summary:

```
## Preparation Complete

**Project**: <name from README or directory>
**Working directory**: <path>
**Git**: <branch> on <remote>
**Specs directory**: <path> / not found
**Build**: passing / failing / skipped
**Dev server**: running at <URL> / not started / failed

**Ready for**: Specification phase
**Blockers**: <list any, or "none">
```

If there are blockers, resolve them before proceeding. If everything is green, transition to the specification phase automatically (or ask for confirmation, depending on user preference).
