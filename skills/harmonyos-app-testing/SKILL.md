---
name: harmonyos-app-testing
description: Drive HarmonyOS / OpenHarmony apps via the `hdc` CLI toolchain — build, install, launch, inspect, and interact with apps on emulators or devices without DevEco Studio GUI. Use when the task involves `hdc`, `uitest`, `hilog`, `aa start`, `bm install`, `snapshot_display`, `hvigorw`, running a HarmonyOS emulator, installing `.hap` files, dumping UI trees, injecting gestures, taking screenshots, or any HarmonyOS app testing, automation, or QA work. Also trigger on well-known tooling errors like `ERR_WORKER_INVALID_EXEC_ARGV` or `NODE_OPTIONS` issues. Do NOT use for writing ArkTS/ArkUI code or Android/adb tasks — this is purely the host-side CLI toolchain.
---

# HarmonyOS App Testing

End-to-end toolkit for interacting with a HarmonyOS / OpenHarmony app running on an emulator or physical device, using only the HarmonyOS SDK CLI tools (`hdc`, `uitest`, `hilog`, `aa`, `bm`, `snapshot_display`). No DevEco Studio GUI required.

Everything here works against any HarmonyOS target reachable through `hdc` — physical phones in USB debug mode, the official HarmonyOS Emulator, OpenHarmony devices, any screen resolution, any device form factor. Resolve tool paths from the user's environment; **never hardcode** SDK / DevEco install paths.

### When to use this skill

Trigger when the user mentions any of these tools, actions, or error patterns:

- **Tools**: `hdc`, `uitest`, `hilog`, `aa start`, `bm install`, `snapshot_display`, `hvigorw`, `Emulator -list`
- **Actions**: launching a HarmonyOS emulator, installing/starting a HAP, dumping the UI tree, viewing/filtering logs, injecting taps/swipes/drags/flings/multi-finger gestures/key events/text, taking screenshots, recording video
- **Keywords**: "HarmonyOS emulator", "OpenHarmony device", `.hap` files, `EntryAbility`, `com.example.*` bundle names
- **Error patterns**: `ERR_WORKER_INVALID_EXEC_ARGV`, `--openssl-legacy-provider`, `NODE_OPTIONS` errors from `hvigorw`, `hdc file recv` pulling garbled files on Git Bash/MSYS, `hilog` blocking forever in a script, `aa start`/`bm install` "multiple targets" errors

### When NOT to use this skill

- Writing ArkTS/ArkUI application code → use `harmonyos-app-dev` instead
- Designing HarmonyOS components or configuring `module.json5` → use `harmonyos-app-dev` instead
- Android/adb tasks → this is `hdc`, not `adb`

---

## Setup: making the CLI tools callable

The HarmonyOS SDK ships two key binary directories:

1. **SDK toolchains** (contains `hdc`, `idl`, `restool`, …) — under the OpenHarmony SDK, typically `<sdk-root>/default/openharmony/toolchains/` (or a versioned subfolder for newer SDKs). Find it by searching for `hdc` (`hdc.exe` on Windows) under the user's SDK location.
2. **Emulator** binary (`Emulator` / `Emulator.exe`) — under DevEco Studio install, typically `<deveco-root>/tools/emulator/`.

Discover the paths once, then put both on `PATH` for the current shell session. The exact discovery method depends on the host OS:

| Host | Discovery hint |
|---|---|
| Windows (Git Bash / MSYS) | Look in `C:/Users/<user>/AppData/Local/Huawei/Sdk` (default SDK root from DevEco Studio) and `C:/Program Files/Huawei/DevEco Studio/tools/...` / `D:\…\DevEco Studio\tools\…`. Honour the user's actual install path if different. |
| macOS | `~/Library/Huawei/Sdk` for SDK; `/Applications/DevEco-Studio.app/Contents/tools/...` for Emulator. |
| Linux | `~/.huawei/sdk` (or similar) for SDK; DevEco Studio install path varies. |

If the user has already told you where these live (e.g. via `local.properties`, env vars, or earlier in the conversation), use that. Otherwise ask, or run a quick `find` / `where hdc` / `which hdc` first.

For the rest of this document, assume `hdc`, `Emulator`, and `snapshot_display` are callable. Examples are written with bare command names; substitute full paths when not on `PATH`.

### One-time environment gotchas

- **`NODE_OPTIONS`** containing `--openssl-legacy-provider` breaks any DevEco command that spawns Node 18+ (e.g. `hvigorw`). If you hit `ERR_WORKER_INVALID_EXEC_ARGV`, prepend `unset NODE_OPTIONS &&` to the failing command (or unexport it for the session).
- On Windows under Git Bash / MSYS, paths starting with `/` are mangled. When passing remote (on-device) paths to `hdc` (e.g. `/data/local/tmp/...`), prefix with `MSYS_NO_PATHCONV=1` to disable path translation: `MSYS_NO_PATHCONV=1 hdc file recv /data/local/tmp/screen.jpeg ./screen.jpeg`.
- `hdc shell "<cmd with quotes/spaces>"` — always wrap the remote command in **one** quoted string. The shell on the device is a single command-line.

---

## Quick reference: tool roles

| Tool | Runs on | Purpose |
|---|---|---|
| `Emulator` | Host | Start / stop / list emulator instances, configure image root |
| `hdc` | Host | The device bridge. List devices, install/uninstall apps, push/pull files, run shell commands, pipe logs |
| `aa` | Device shell | Ability Assistant — start abilities, stop services, force-stop apps, dump ability info |
| `bm` | Device shell | Bundle Manager — install / uninstall / inspect bundles (lower level than `aa`) |
| `uitest` | Device shell | UI inspector + input injector. Dump layout JSON, simulate clicks / swipes / keys / text |
| `uinput` | Device shell | Lower-level input injection (touch screen, mouse, keyboard events) |
| `hilog` | Device shell or `hdc hilog` | The HarmonyOS log system. Filter by tag / pid / level / domain |
| `snapshot_display` | Device shell | Take a screenshot to a file on-device |
| `hvigorw` | Host (project) | Build HAP packages from a HarmonyOS project source tree |

---

## Workflow 1 — Get a HarmonyOS app running on an emulator

This is the canonical happy path: source project → built HAP → installed and launched on a running emulator.

```bash
# 0. Ensure tools are on PATH (see Setup).

# 1. Build the HAP (debug, unsigned — fine for emulator).
#    Run from the HarmonyOS project root (the directory with build-profile.json5).
#    `unset NODE_OPTIONS` is the workaround for the openssl-legacy-provider issue.
unset NODE_OPTIONS && hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon
# Artefact lands at: entry/build/default/outputs/default/entry-default-unsigned.hap
# (path varies if the module is not named `entry` or the product is not `default`)

# 2. Configure the Emulator image root ONCE per machine (points at the SDK images
#    Huawei downloads via DevEco Studio's SDK Manager). Skip if already configured.
Emulator -config -imageRoot "<path-to-sdk-root-containing-emulator-images>"

# 3. List available emulator instances, then start one in the background.
Emulator -list
nohup Emulator -start <instance-name> >/dev/null 2>&1 &   # detach so the shell returns

# 4. Wait until `hdc` sees the emulator (typically within a few seconds).
#    On the emulator transport, devices appear as 127.0.0.1:5555 (or similar).
for i in 1 2 3 4 5 6 7 8 9 10; do
  if hdc list targets | grep -v '\[Empty\]' | grep -q .; then break; fi
  sleep 2
done
hdc list targets
hdc shell echo ready   # final sanity check — should print "ready"

# 5. Install the HAP. `-r` replaces any existing copy.
hdc app install -r entry/build/default/outputs/default/entry-default-unsigned.hap

# 6. Launch the main ability.
hdc shell aa start -a EntryAbility -b com.example.myapplication
```

The ability name and bundle name come from the project's `AppScope/app.json5` and `entry/src/main/module.json5`. For a fresh DevEco template they default to `EntryAbility` and `com.example.<projectname>`.

To switch to a specific device when several are connected: `hdc -t <connectkey> <subcommand>` — the connectkey is the value shown by `hdc list targets`.

---

## Workflow 2 — Inspect the running app (UI tree, logs, screenshots)

### Dump the UI tree

`uitest dumpLayout` writes a JSON description of the currently visible UI hierarchy — every component, its bounds, text, accessibility ID, `clickable`/`scrollable`/`focused` flags, etc.

```bash
# Dump the merged window tree of a specific bundle. -p is the on-device save path.
hdc shell "uitest dumpLayout -b com.example.myapplication -p /data/local/tmp/layout.json"

# Pull it to the host for inspection. MSYS_NO_PATHCONV avoids Windows path mangling.
MSYS_NO_PATHCONV=1 hdc file recv /data/local/tmp/layout.json ./layout.json
```

The output JSON has a recursive `children` array. Each node carries `attributes` like `text`, `bounds` (`[x1,y1][x2,y2]`), `type`, `id`, `clickable`. To click a known component, compute its centre from `bounds` and feed it to `uitest uiInput click`.

Useful flags:
- `-b <bundleName>` — limit the dump to one app's window (recommended; otherwise you also get the system status bar etc.).
- `-w <windowId>` — limit to one window when an app has multiple.
- `-a` — include font attributes.
- `-i` — don't merge windows / don't filter nodes (more verbose but exposes overlays).
- `-e <attributeName>` — extend with an extra attribute the default dump omits.

### View logs (hilog)

```bash
# Tail the last N lines and exit (non-blocking — what you want from a script).
hdc shell "hilog -x -z 200"

# Filter by tag (e.g. JSAPP for console.log output from ArkTS).
hdc shell "hilog -x -z 200 -T JSAPP"

# Filter by pid. Get the app's pid from `aa dump -a` or by parsing `ps -A`.
hdc shell "hilog -x -z 500 -P <pid>"

# Filter by level (D/I/W/E/F or DEBUG/INFO/WARN/ERROR/FATAL).
hdc shell "hilog -x -z 500 -L E,F"

# Combine with a regex on the message body.
hdc shell "hilog -x -z 1000 -T JSAPP -e 'login|auth'"

# Live streaming straight to the host stdout (blocks until you cancel).
hdc hilog
# Stop streaming and print recent app+core+init logs at warn+ severity:
hdc hilog -x -z 500 -L W,E,F
```

`hilog` is sensitive to flag combinations — when in doubt, run it via `hdc shell "hilog ..."` rather than `hdc hilog ...`, which sometimes complains about "Multi commands can't be used in combination".

### Take a screenshot

```bash
# 1. Capture on-device into a temp file.
hdc shell "snapshot_display -f /data/local/tmp/screen.jpeg"

# 2. Pull it to the host.
MSYS_NO_PATHCONV=1 hdc file recv /data/local/tmp/screen.jpeg ./screen.jpeg
```

For a one-shot helper, `uitest screenCap -p /data/local/tmp/screen.png` does the same thing (and is what UIs like DevEco Studio's "Take Screenshot" button use internally). `-d <displayId>` selects a specific display on multi-display devices.

### Record screen video

HarmonyOS exposes screen recording via `hdc shell snapshot_display` for stills only — for video, use the on-device `screen_record` command if available (`hdc shell "which screen_record"` to check; this is image/version dependent). When unavailable, the practical fallback is a loop of `snapshot_display` snapshots + post-process into a video with `ffmpeg`:

```bash
# Capture 60 frames at ~5fps (~12s) into /data/local/tmp/frames/, then pull and stitch.
hdc shell "mkdir -p /data/local/tmp/frames"
for i in $(seq -w 1 60); do
  hdc shell "snapshot_display -f /data/local/tmp/frames/f${i}.jpeg"
  sleep 0.2
done
MSYS_NO_PATHCONV=1 hdc file recv /data/local/tmp/frames ./frames
ffmpeg -framerate 5 -i ./frames/f%02d.jpeg -c:v libx264 -pix_fmt yuv420p out.mp4
```

If the user has the DevEco Studio CLI image-recording tooling (`hiprofiler_cmd` or similar) available, prefer that — it's lower overhead than snapshot polling. Check `<sdk-root>/.../toolchains/` and DevEco Studio's `tools/profiler/` for `trace_streamer.exe`, `hiprofiler_cmd`, etc.

---

## Workflow 3 — Drive the app (taps, swipes, gestures, keys, text)

All interaction goes through `uitest uiInput` (newer, friendlier) or `uinput` (lower level, supports raw events). Prefer `uitest uiInput` unless you specifically need raw multi-touch.

```bash
# --- Taps -------------------------------------------------------------------
hdc shell "uitest uiInput click 1280 800"
hdc shell "uitest uiInput doubleClick 1280 800"
hdc shell "uitest uiInput longClick 1280 800"

# --- Swipes / drags --------------------------------------------------------
# swipe: ballistic, releases at end. drag: stays in contact at end.
# velocity in px/s, range 200–40000 (default 600).
hdc shell "uitest uiInput swipe 1280 1200 1280 400 2000"   # swipe up
hdc shell "uitest uiInput drag  100 500  900 500  600"     # drag horizontally

# --- Directional fling (great for paginated content) -----------------------
# direction: 0=left 1=right 2=up 3=down
hdc shell "uitest uiInput dircFling 2"               # fling up
hdc shell "uitest uiInput dircFling 3 3000 50"       # fling down, fast, long step

# --- Free-form fling -------------------------------------------------------
hdc shell "uitest uiInput fling 1280 1400 1280 200 3000 60"

# --- Key events ------------------------------------------------------------
# Mnemonic keys:
hdc shell "uitest uiInput keyEvent Back"     # Back navigation
hdc shell "uitest uiInput keyEvent Home"     # Go to Home (background the app)
hdc shell "uitest uiInput keyEvent Power"    # Sleep / wake screen
# Numeric keycodes (HarmonyOS Multimodal Input keycodes). Up to 3 keys, all
# pressed simultaneously — handy for shortcuts.
hdc shell "uitest uiInput keyEvent 2072 2047"   # e.g. Ctrl+A (2072=Ctrl, 2047=A)

# --- Text input ------------------------------------------------------------
# At a specific coordinate (taps it first, then types):
hdc shell "uitest uiInput inputText 800 600 hello"
# Into whatever input is currently focused:
hdc shell "uitest uiInput text 'hello world'"
```

For gestures that `uitest uiInput` doesn't cover (multi-finger pinch / zoom / rotate), drop to `uinput`:

```bash
# uinput -T -m <x1> <y1> <x2> <y2> [duration_ms] — single-finger swipe via touchscreen.
hdc shell "uinput -T -m 1280 1200 1280 400 400"
# uinput supports -K (keyboard), -M (mouse), -S (stylus) etc. Run `uinput -h` on the
# device for the full surface.
```

### Picking coordinates from the UI tree

The robust pattern is: dump the UI tree → find the target component by `text` / `id` / `type` → compute the centre of its `bounds` → tap that. The dumpLayout JSON's `bounds` field is `[x1,y1][x2,y2]`. Centre = `((x1+x2)/2, (y1+y2)/2)`.

```bash
# Concrete example: tap a button whose text is "Login".
hdc shell "uitest dumpLayout -b com.example.myapp -p /data/local/tmp/l.json"
MSYS_NO_PATHCONV=1 hdc file recv /data/local/tmp/l.json ./l.json
# Then: parse l.json (Python / jq), find node where attributes.text == "Login",
# read bounds, compute centre, call uitest uiInput click <cx> <cy>.
```

For repeatable scripts, write a small Python helper (no extra deps — only the stdlib `json` module) that does the parse-and-tap dance. Keep it in the project, not in this skill.

---

## Workflow 4 — Lifecycle commands

```bash
# List installed bundles (filter to your org).
hdc shell "bm dump -a" | grep -i myapp

# Inspect a specific bundle.
hdc shell "bm dump -n com.example.myapplication"

# Force-stop a running app.
hdc shell "aa force-stop com.example.myapplication"

# Uninstall.
hdc app uninstall com.example.myapplication
# Or via bm (lower level): hdc shell "bm uninstall -n com.example.myapplication"

# Get pid of the running app — `aa dump -a` lists ability records with pids.
hdc shell "aa dump -a" | grep -A2 com.example.myapplication

# Capture a full bug report (lots of useful diagnostics — slow).
hdc bugreport ./bugreport-$(date +%s).zip
```

### Recording an interaction session

`uitest uiRecord record` writes every UI event the user performs (taps, swipes, key events) into a CSV — handy for replaying or for capturing reproductions of a bug.

```bash
# Start recording. -W true also saves widget info per event; -l also saves layout.
hdc shell "uitest uiRecord record -W true -l -c true"
# Press Ctrl+C / kill the process on-device to stop, then pull whatever CSV it wrote
# (path printed in its own log output — typically /data/local/tmp/layout/).
hdc shell "uitest uiRecord read"   # prints the captured CSV to stdout
```

---

## Workflow 5 — Multi-device targeting

If `hdc list targets` shows more than one device (typical when an emulator runs alongside a USB-connected phone), every subsequent `hdc` call must specify which one:

```bash
hdc list targets -v                 # verbose listing with device names
hdc -t 127.0.0.1:5555 shell echo from-emulator
hdc -t <phone-connect-key> shell echo from-phone
```

For batch scripting, set `HDC_UTILITY_ENCODED_PREFIX` or pin the target with a wrapper function in your shell.

---

## Anti-patterns to avoid

- **Hardcoding install paths.** SDK and DevEco Studio locations differ per machine (Windows / macOS / Linux, different drives, custom installs). Always resolve from the user's environment or from `local.properties`.
- **Assuming a specific emulator instance.** Use `Emulator -list` and pick whatever exists, or create one only if the list is empty.
- **Insisting the user open DevEco Studio to start the emulator.** The `Emulator` CLI works standalone — `Emulator -list` + `Emulator -start <name>` is sufficient. DevEco Studio is *not* required for any step in this skill.
- **Running `hdc hilog` inside a non-streaming script.** It blocks. Use `hdc shell "hilog -x -z N"` for one-shot dumps.
- **Forgetting `-r` on `hdc app install`.** Without it, reinstalling the same bundle fails with "already exists".
- **Using `hdc file recv` with a `/data/...` path on Git Bash without `MSYS_NO_PATHCONV=1`.** The leading slash gets rewritten to a Windows path and the command silently sends garbage.
- **Tapping coordinates blindly.** Resolutions vary (phone vs tablet vs foldable). Dump the UI tree, then compute centres.
- **Using outdated `uitest` syntax.** Legacy guides show `uitest click x y` or `uitest dump`. The current API is `uitest uiInput click x y` and `uitest dumpLayout -b <bundle> -p <path>`. Always use the `uiInput` / `dumpLayout` subcommand form.
- **Using `hdc -s <id>` for device targeting.** That's an adb flag and does not exist in `hdc`. The correct flag is `hdc -t <connectkey>` — read connectkey from `hdc list targets`.
- **Invoking `setenforce` or other SELinux tweaks.** HarmonyOS Emulator does not require disabling SELinux to install or run unsigned HAPs. If you reach for `setenforce 0`, you have the wrong mental model — emulator targets accept unsigned HAPs out of the box.

---

## Reference files

- `references/hdc-cheatsheet.md` — exhaustive `hdc` subcommand reference grouped by category (transport, app, file, debug, forward, flash, service).
- `references/uitest-cheatsheet.md` — every `uitest` subcommand and `uiInput` action with concrete examples and the full HarmonyOS Multimodal Input keycode list.

Read these only when the cheatsheet here doesn't cover what you need — they're loaded on demand to keep this file lean.
