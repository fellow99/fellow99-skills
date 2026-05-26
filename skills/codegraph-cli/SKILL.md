---
name: codegraph-cli
description: Use the `codegraph` CLI to explore, search, and reason about a codebase via a pre-built semantic knowledge graph instead of grep/find/Read loops. Trigger whenever the task involves understanding how a codebase works ("how does X work?", "where is Y defined?", "what calls Z?", "trace the request flow", "what breaks if I change this function?"), finding symbols, mapping call graphs, analyzing change impact, or building task-focused context for a feature. Also trigger on explicit mentions of `codegraph`, `.codegraph/`, "knowledge graph", "code index", or when the user asks to initialize/index/sync the project. Prefer this skill over manual grep + Read whenever a project is (or can be) indexed — codegraph answers in a handful of calls what would otherwise take dozens of file reads.
license: MIT
allowed-tools: Bash
---

# CodeGraph CLI

## What this skill is for

`codegraph` is a CLI that builds a local semantic knowledge graph of a codebase (symbols, calls, imports, framework routes) and lets you query it in O(seconds) instead of scanning files. This skill teaches you when to reach for it, which subcommand fits which question, and how to compose them efficiently.

The mental model:

- `codegraph query` → "find me the symbol named X" (replaces `grep -r 'function X'`)
- `codegraph callers` / `callees` → "who calls X / what does X call" (replaces multi-file grep + Read)
- `codegraph impact` → "what breaks if I change X" (no grep equivalent — transitive)
- `codegraph context` → "give me everything relevant to this task as one markdown brief" (replaces an entire exploration session)
- `codegraph files` → fast indexed file tree (replaces `find` / `ls -R`)
- `codegraph affected` → "which tests are downstream of these changed files" (CI gold)

If `.codegraph/` exists in the project, **use codegraph first** for any exploration question. Falling back to grep + Read repeats work the index already did and burns tokens. Reach for raw file reads only to confirm a specific detail codegraph didn't surface.

## Decision flow

```
User asks something about the codebase
         │
         ▼
Does `.codegraph/` exist in the project?
         │
   ┌─────┴─────┐
   no          yes
   │           │
   │           ▼
   │     Is the question about a SPECIFIC symbol/file already known?
   │           │
   │     ┌─────┴─────┐
   │     yes         no (open-ended: "how does X work?", "trace Y", "what's affected")
   │     │           │
   │     │           ▼
   │     │     `codegraph context "<task description>"` first to map the area
   │     │           │
   │     ▼           ▼
   │   Use targeted commands: query / callers / callees / impact / files
   │
   ▼
Offer to initialize: `codegraph init -i` (init + index in one step)
Then proceed as above.
```

## Initial setup (per project)

Run these once per project. They're idempotent-ish — `init` is safe to re-run; `index --force` re-indexes everything.

```bash
# In the project root
codegraph init -i           # initialize .codegraph/ and run first index
# OR, if already initialized:
codegraph index             # full index
codegraph sync              # incremental update (cheap; run after pulls)
codegraph status            # sanity check: file count, symbol count, journal mode
```

**Check `codegraph status` first** when arriving at an unfamiliar project — it tells you whether the index exists, how fresh it is, and whether the SQLite journal is `wal` (good) vs something else (means concurrent reads may block; the project is likely on a network share or WSL2 `/mnt`).

If a previous run crashed and indexing complains about a lock, run `codegraph unlock`.

To remove the index entirely: `codegraph uninit -f`.

## Command reference

Every command accepts an optional `[path]` (or `-p, --path`) defaulting to the current directory. Most support `-j, --json` for scripting.

### Discovery

| Command | Use for | Key options |
|---|---|---|
| `codegraph query <search>` | Find symbols by name (FTS5). | `-k function\|class\|method\|...`, `-l <n>` limit, `-j` |
| `codegraph files` | Indexed file tree — faster than `find`. | `--filter <dir>`, `--pattern <glob>`, `--format tree\|flat\|grouped`, `--max-depth <n>`, `--no-metadata`, `-j` |
| `codegraph status` | Index health. | `-j` |

### Reasoning

| Command | Use for | Key options |
|---|---|---|
| `codegraph context <task>` | Build a markdown brief: entry points + related symbols + code snippets for a task. Best opening move for open-ended exploration. | `-n <n>` max nodes (default 50), `-c <n>` max code blocks (default 10), `--no-code`, `-f markdown\|json` |
| `codegraph callers <symbol>` | Who calls this. One hop. | `-l <n>`, `-j` |
| `codegraph callees <symbol>` | What this calls. One hop. | `-l <n>`, `-j` |
| `codegraph impact <symbol>` | Transitive blast radius — every symbol affected if `<symbol>` changes. Run before refactors. | `-d <depth>` (default 5), `-j` |
| `codegraph affected [files...]` | Which test files transitively import any of these changed files. CI use. | `--stdin`, `-d <n>`, `-f <glob>`, `-j`, `-q` |

### Lifecycle

| Command | Use for |
|---|---|
| `codegraph init [-i]` | Create `.codegraph/`; `-i` also indexes immediately. |
| `codegraph index [-f] [-q]` | Full (re-)index. `-f` forces re-index even if up-to-date; `-q` for less output. |
| `codegraph sync [-q]` | Incremental update since last index. Cheap; safe to run liberally. |
| `codegraph uninit [-f]` | Delete `.codegraph/`. |
| `codegraph unlock` | Clear stale lock file blocking index. |
| `codegraph serve --mcp` | Run as MCP server (stdio). Don't invoke from a skill — agents launch this themselves. |
| `codegraph install` / `uninstall` | Wire/unwire codegraph MCP into Claude Code / Cursor / Codex CLI / opencode / Hermes. Out of scope for this skill — the user runs this once. |

## Recipes

### "How does feature X work?" (open-ended)

Start broad, then narrow. Don't dive into `query` first — `context` composes search + relations + snippets and gives you a map.

```bash
codegraph context "how user authentication works" -n 40
# Read the markdown output. Pick the most relevant symbol.
codegraph callers AuthService.login -l 20
codegraph callees AuthService.login -l 20
```

### "Where is symbol X defined?"

```bash
codegraph query MyClass            # may return multiple matches across kinds
codegraph query handleSubmit -k function
codegraph query UserRepository -k class -j   # pipe to jq for scripts
```

### "What breaks if I change function X?"

```bash
codegraph impact validateEmail              # default depth 5
codegraph impact validateEmail -d 2         # narrower: direct + one hop
codegraph impact validateEmail -j | jq '.nodes | length'
```

Use this **before** refactors. The output tells you which call sites and downstream symbols are reachable from the symbol you're about to modify.

### "Which tests should I run after this change?"

```bash
# Explicit files:
codegraph affected src/utils.ts src/api/handlers.ts

# From a diff (typical CI/hook usage):
git diff --name-only HEAD~1 | codegraph affected --stdin --quiet

# Then feed straight into the test runner:
TESTS=$(git diff --name-only HEAD | codegraph affected --stdin --quiet)
[ -n "$TESTS" ] && npx vitest run $TESTS
```

`--filter` overrides the auto-detected test-file glob if the project's convention is unusual: `--filter "tests/e2e/**/*.spec.ts"`.

### "What's the structure of `src/`?"

```bash
codegraph files --filter src --max-depth 3
codegraph files --pattern '**/*.tsx' --format flat
codegraph files --format grouped               # grouped by language
```

Much faster than walking the filesystem, and includes per-file symbol counts.

### Scripting (JSON pipelines)

Every read command supports `-j` / `--json`. Pipe through `jq`:

```bash
codegraph query Service -j | jq -r '.[] | "\(.kind)\t\(.name)\t\(.file):\(.line)"'
codegraph callers handleRequest -j | jq '.[].name'
codegraph impact ApiClient -d 3 -j | jq '.nodes | group_by(.kind) | map({kind: .[0].kind, n: length})'
```

## Workflow when arriving at a new (or unfamiliar) project

1. `codegraph status` — is it indexed? Fresh? WAL mode?
2. If not initialized: ask the user, then `codegraph init -i`.
3. If stale (you just pulled, switched branches, etc.): `codegraph sync`.
4. Now answer the user's question via the recipes above.

Do **not** silently run `init` or `index --force` without telling the user — indexing can take noticeable time on large repos, and `uninit` is destructive.

## Combining with other tools

- **Found a symbol via codegraph, need its full source?** `codegraph query` returns `file:line`. Open it with Read for the surrounding context — but only that file, not a grep sweep.
- **Codegraph missed something?** Some languages or constructs may be partially supported. Fall back to `rg` / `grep` for that specific check, but don't abandon the index — re-query with a different name or use `codegraph files --pattern` to scope your fallback search.
- **Editing code?** After significant edits, `codegraph sync` keeps queries accurate. (The MCP server auto-syncs on a debounce; the CLI does not.)

## Failure modes & fixes

| Symptom | Fix |
|---|---|
| `CodeGraph not initialized` | `codegraph init -i` in the project root. |
| `database is locked` | Almost always WAL-disabled on a network/WSL2 filesystem. Confirm with `codegraph status` (Journal field). Move project to a local disk, or upgrade to ≥0.9 which bundles `node:sqlite` in WAL by default. |
| Stale lock blocks indexing | `codegraph unlock`. |
| Query returns nothing for a symbol you can see | Run `codegraph sync` — index may be behind. Then re-query. If still missing, the file may be `.gitignore`d or in a default-excluded dir (`node_modules`, `dist`, `vendor`, `.venv`, `build`, `target`, `.next`, `Pods`). To force inclusion, add a negation to `.gitignore`: `!vendor/`. |
| `codegraph` not on PATH | Reinstall: `curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh \| sh` or `npm i -g @colbymchenry/codegraph`. |

## What this skill does NOT do

- It does **not** invoke the MCP server (`codegraph serve --mcp`). That's an agent-level setup the user runs once via `codegraph install`.
- It does **not** modify project source code. All commands except `init`/`index`/`sync`/`uninit`/`unlock` are read-only.
- It does **not** replace human judgment for design decisions — codegraph answers structural questions, not "should I refactor this?"

## Quick reference: idiomatic one-liners

```bash
codegraph status                                # is the index alive?
codegraph init -i                               # first-time setup
codegraph sync                                  # after git pull / branch switch
codegraph context "implement password reset"    # opening move for a feature task
codegraph query handlePayment                   # find a symbol
codegraph callers chargeCard -l 30              # who calls it
codegraph impact chargeCard -d 3                # blast radius
git diff --name-only | codegraph affected --stdin -q   # tests to run
codegraph files --filter src/api --max-depth 2  # indexed tree
```
