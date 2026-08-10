# uitest Command Cheatsheet

Complete reference for `uitest`, the HarmonyOS on-device UI testing CLI. All commands run via `hdc shell "uitest ..."`.

---

## Subcommands Overview

```
uitest help                  Print all subcommands
uitest --version             Print tool version
uitest screenCap             Capture screenshot
uitest dumpLayout            Dump UI hierarchy as JSON
uitest uiInput               Inject simulated UI operations
uitest uiRecord              Record/replay UI operations
uitest start-daemon <token>  Start uitest daemon for IDE automation
```

---

## screenCap — Screenshot

```
uitest screenCap [-d <displayId>] -p <savePath>
```
| Flag | Description |
|---|---|
| `-p <savePath>` | On-device path for the screenshot file (required) |
| `-d <displayId>` | Target display (default: 0) |

Example:
```bash
hdc shell "uitest screenCap -p /data/local/tmp/screen.png"
```

---

## dumpLayout — UI Hierarchy Dump

```
uitest dumpLayout [-b <bundleName>] [-w <windowId>] [-d <displayId>]
                  [-i] [-a] [-m <true/false>] [-e <attribute>] -p <savePath>
```
| Flag | Description |
|---|---|
| `-p <savePath>` | On-device JSON output path (required) |
| `-b <bundleName>` | Limit to one app's windows (recommended) |
| `-w <windowId>` | Limit to one specific window |
| `-d <displayId>` | Target display |
| `-i` | Don't merge windows / don't filter nodes |
| `-a` | Include font attributes per node |
| `-m <true/false>` | Explicit merge-window toggle (default: true) |
| `-e <attribute>` | Extend each node with an extra attribute |

Output JSON structure:
```json
{
  "attributes": { "text": "Welcome", "bounds": "[1038,746][1522,878]", "type": "Text",
                  "id": "xxx", "clickable": true, "scrollable": false, "focused": false },
  "children": [ ... ]
}
```

Example full workflow:
```bash
hdc shell "uitest dumpLayout -b com.example.myapp -p /data/local/tmp/layout.json"
MSYS_NO_PATHCONV=1 hdc file recv /data/local/tmp/layout.json ./layout.json
```

---

## uiInput — Simulated Input

```
uitest uiInput <action> [args...]
```

### Taps
| Action | Args | Description |
|---|---|---|
| `click` | `<x> <y>` | Single tap at coordinates |
| `doubleClick` | `<x> <y>` | Double tap |
| `longClick` | `<x> <y>` | Long press |

```bash
hdc shell "uitest uiInput click 1280 800"
```

### Swipe / Drag
| Action | Args | Description |
|---|---|---|
| `swipe` | `<fx> <fy> <tx> <ty> [velocity]` | Ballistic swipe (releases at end) |
| `drag` | `<fx> <fy> <tx> <ty> [velocity]` | Drag (stays in contact at end) |

`velocity` range: 200–40000 px/s (default: 600)

```bash
hdc shell "uitest uiInput swipe 640 1200 640 400 2000"   # swipe up
hdc shell "uitest uiInput drag  100 500  900 500"         # drag right
```

### Fling
| Action | Args | Description |
|---|---|---|
| `dircFling` | `<direction> [velocity] [stepLength]` | Directional fling |
| `fling` | `<fx> <fy> <tx> <ty> [velocity] [stepLength]` | Free-form fling |

Direction values: `0`=left, `1`=right, `2`=up, `3`=down

```bash
hdc shell "uitest uiInput dircFling 2"             # fling up
hdc shell "uitest uiInput dircFling 3 3000 50"     # fling down, fast
hdc shell "uitest uiInput fling 640 1400 640 200 3000 60"
```

### Key Events
| Action | Args | Description |
|---|---|---|
| `keyEvent` | `<keyID\|Back\|Home\|Power>` | Single key event |
| `keyEvent` | `<keyID_0> <keyID_1> [keyID_2]` | Up to 3 simultaneous keys |

Mnemonic keys: `Back`, `Home`, `Power`

```bash
hdc shell "uitest uiInput keyEvent Back"
hdc shell "uitest uiInput keyEvent Home"
hdc shell "uitest uiInput keyEvent Power"
hdc shell "uitest uiInput keyEvent 2072 2047"   # Ctrl+A
```

### Text Input
| Action | Args | Description |
|---|---|---|
| `inputText` | `<x> <y> <text>` | Tap then type at coordinates |
| `text` | `<text>` | Type into currently focused input |

```bash
hdc shell "uitest uiInput inputText 800 600 hello"
hdc shell "uitest uiInput text 'hello world'"
```

---

## uiRecord — Event Recording

```
uitest uiRecord record [-W <true/false>] [-l] [-c <true/false>]
uitest uiRecord read
```
| Flag | Description |
|---|---|
| `-W <true/false>` | Save widget info per event (default: true) |
| `-l` | Save layout after each operation |
| `-c <true/false>` | Print events to console (default: true) |

`record` writes to a CSV inside `/data/local/tmp/layout/`. `read` prints the last recording to stdout. Kill the `record` process (Ctrl+C or `kill`) to stop.

```bash
hdc shell "uitest uiRecord record -W true -l -c true"
# ... interact with app ...
# Ctrl+C to stop
hdc shell "uitest uiRecord read"
```

---

## Common Keycodes (HarmonyOS Multimodal Input)

| Key | Code | Key | Code |
|---|---|---|---|
| **0** | 2007 | **A** | 2017 |
| **1** | 2008 | **B** | 2018 |
| **2** | 2009 | **C** | 2019 |
| **3** | 2010 | **D** | 2020 |
| **4** | 2011 | **E** | 2021 |
| **5** | 2012 | **F** | 2022 |
| **6** | 2013 | **G** | 2023 |
| **7** | 2014 | **H** | 2024 |
| **8** | 2015 | **I** | 2025 |
| **9** | 2016 | ... | ... |

| Modifier | Code | Function | Code |
|---|---|---|---|
| Ctrl (left) | 2072 | Enter | 2054 |
| Shift (left) | 2073 | Space | 2049 |
| Alt (left) | 2074 | Backspace | 2057 |
| Meta (left) | 2075 | Escape | 2070 |
| Ctrl (right) | 2082 | Tab | 2048 |
| Shift (right) | 2083 | Delete | 2055 |
| Arrow Up | 2065 | Arrow Down | 2066 |
| Arrow Left | 2067 | Arrow Right | 2068 |

Full list: `/data/service/el1/public/multimodalinput/multimodal_input_event_token.json` on-device, or the HarmonyOS documentation under "Multimodal Input → Key Event".

---

## start-daemon — Automation Daemon

```
uitest start-daemon <token>
```

Starts the uitest service in daemon mode, used by DevEco Studio's automated testing pipeline. The `<token>` is a session identifier. Typically only needed by IDE integrations — `dumpLayout` and `uiInput` work standalone without the daemon.