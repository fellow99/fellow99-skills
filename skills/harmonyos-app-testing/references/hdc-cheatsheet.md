# hdc Command Cheatsheet

Complete reference for `hdc` (OpenHarmony Device Connector), the device bridge for HarmonyOS / OpenHarmony. Grouped by category with flags and examples.

---

## Global Commands

| Command | Description |
|---|---|
| `hdc -h/help [verbose]` | Print help; `verbose` shows all commands |
| `hdc -v/version` | Print version |
| `hdc -l[0-6]` | Set runtime log level |
| `hdc -t <connectkey>` | Target a specific device by connect key |
| `hdc checkserver` | Check client-server version compatibility |

---

## Session Commands (server-side)

| Command | Description |
|---|---|
| `hdc list targets [-v]` | List all connected devices; `-v` shows details |
| `hdc tconn <key> [-remove]` | Connect to device. Key formats: TCP `ip:port`, USB auto, UART `COM5,921600`. `-remove` to disconnect |
| `hdc start [-r]` | Start hdc server; `-r` restarts |
| `hdc kill [-r]` | Stop hdc server; `-r` restarts after kill |
| `hdc -s [ip:]port` | Set server listen config |
| `hdc -e <ip>` | Set host IP for TCP forwarding (default 127.0.0.1) |
| `hdc -m` | Start server in foreground |
| `hdc -p` | Skip server start, single-client mode |

---

## Service Commands (daemon-side)

| Command | Description |
|---|---|
| `hdc target mount` | Remount /system /vendor read-write |
| `hdc target boot [-bootloader\|-recovery] [MODE]` | Reboot device or boot into bootloader/recovery |
| `hdc smode [-r]` | Restart daemon as root; `-r` cancels root |
| `hdc tmode usb` | Reboot device, listen on USB |
| `hdc tmode port [port]` | Reboot device, listen on TCP port |
| `hdc tmode port close` | Close TCP port |
| `hdc wait` | Block until device becomes available |

---

## File Commands

### Push (host → device)
```bash
hdc file send [-a] [-sync] [-z] [-m] [-cwd <dir>] [-b] <local> <remote>
```
| Flag | Effect |
|---|---|
| `-a` | Preserve target file timestamp |
| `-sync` | Only update newer files |
| `-z` | Compress transfer |
| `-m` | Mode sync |
| `-cwd <dir>` | Working directory for relative paths |
| `-b` | Send to debug application directory |

### Pull (device → host)
```bash
hdc file recv [-a] [-sync] [-z] [-m] [-cwd <dir>] [-b] <remote> <local>
```
Same flags as `send`. On Windows Git Bash, wrap with `MSYS_NO_PATHCONV=1` to avoid path mangling of leading `/` paths:
```bash
MSYS_NO_PATHCONV=1 hdc file recv /data/local/tmp/screen.jpeg ./screen.jpeg
```

---

## App Commands

### Install
```bash
hdc install [-r] [-s] [-cwd <dir>] ["-w <seconds>"] ["-u <userId>"] ["-p <path>"] <src>
```
| Flag | Effect |
|---|---|
| `-r` | Replace existing app |
| `-s` | Install as shared bundle |
| `-cwd <dir>` | Working directory |
| `-w <seconds>` | Wait timeout for install |
| `-u <userId>` | Target user ID |
| `-p <path>` | Specify bundle path |
| `-h` | Show `bm install` options |

`<src>` can be `.hap`, `.hsp`, `.app` files or directories containing packages.

### Uninstall
```bash
hdc uninstall [-k] [-s] ["-n <bundleName>"] ["-m <moduleName>"] ["-v <versionCode>"] ["-u <userId>"] <package>
```
| Flag | Effect |
|---|---|
| `-k` | Keep data/cache directories |
| `-s` | Remove shared bundle |
| `-n <bundleName>` | Uninstall by bundle name |
| `-m <moduleName>` | Uninstall module by name |
| `-v <versionCode>` | Uninstall shared lib by version |

---

## Forward Commands

| Command | Description |
|---|---|
| `hdc fport <localnode> <remotenode>` | Forward local → remote |
| `hdc rport <remotenode> <localnode>` | Reverse remote → local |
| `hdc fport ls` | List forward/reverse tasks |
| `hdc fport rm <taskstr>` | Remove a task |

Node format: `schema:content`
- `tcp:<port>`
- `jdwp:<pid>` (remote only)
- `ark:<pid>@<tid>@Debugger`
- `localfilesystem:...`, `localabstract:...`, `dev:<name>`

---

## Debug Commands

| Command | Description |
|---|---|
| `hdc hilog [-h\|parse]` | Show device logs; `-h` for hilog help; `parse` to parse local hilog files |
| `hdc shell [-b <bundleName>] [COMMAND...]` | Run shell command or interactive shell. `-b` runs in the app's debug sandbox directory |
| `hdc bugreport [FILE]` | Full device bug report, saved to FILE if specified |
| `hdc jpid` | List PIDs with JDWP transport |
| `hdc track-jpid [-a] [-p]` | Track debug PIDs live. `-a` includes release processes; `-p` hides debug tags |
| `hdc sideload [PATH]` | Sideload full OTA package |

---

## Flash Commands

| Command | Description |
|---|---|
| `hdc update <package>` | Update system by package |
| `hdc flash [-f] <partition> <image>` | Flash partition. `-f` forces |
| `hdc erase [-f] <partition>` | Erase partition |
| `hdc format [-f] <partition>` | Format partition |

---

## Security Commands

```bash
hdc keygen FILE          # Generate public/private key pair (FILE, FILE.pub)
```

---

## Environment Variables

| Variable | Effect | Default |
|---|---|---|
| `OHOS_HDC_SERVER_PORT` | Server listen port (1–65535) | 8710 |
| `OHOS_HDC_LOG_LEVEL` | Server log level (0–5) | 5 |
| `OHOS_HDC_HEARTBEAT` | `1` = disable heartbeat | enabled |
| `OHOS_HDC_CMD_RECORD` | `1` = enable cmd recording | disabled |
| `OHOS_HDC_ENCRYPT_CHANNEL` | `1` = encrypt TCP channel | disabled |