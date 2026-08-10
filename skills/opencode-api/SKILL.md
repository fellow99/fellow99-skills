---
name: opencode-api
description: Interact with an opencode server via its HTTP REST API — manage sessions, send messages, browse files, query configs, and list MCP servers, skills, and providers. Use when the user needs to programmatically control an opencode server, automate opencode workflows, or query its API from scripts. Covers health checks, session CRUD, message sending, file browsing, text search, MCP management, and provider listing. Do NOT use for general coding or debugging — this is purely the HTTP API client for the opencode server.
---

# opencode-api

HTTP REST API 客户端，用于与 opencode 服务器交互。提供 Bash、Python、JavaScript 三种语言的封装脚本。

## 配置

本 Skill 读取以下环境变量：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `OPENCODE_SERVER_BASE_URL` | `http://127.0.0.1:4096` | 服务器地址 |
| `OPENCODE_SERVER_USERNAME` | `opencode` | 用户名 |
| `OPENCODE_SERVER_PASSWORD` | (空) | 密码（服务器启用认证时必填） |

Docker 环境中将 `BASE_URL` 设为 `http://host.docker.internal:4096`。

## 快速开始

根据用户使用的语言选择对应脚本。三个脚本功能完全一致，选择用户环境中最方便的那个。

### Bash

```bash
./opencode-api.sh health                    # 健康检查
./opencode-api.sh sessions                  # 列出会话
./opencode-api.sh create-session "标题"      # 创建会话
./opencode-api.sh send ses_xxx "你好"        # 发送消息
./opencode-api.sh files .                   # 列出文件
./opencode-api.sh read-file ./path          # 读取文件
./opencode-api.sh search "TODO"             # 搜索文本
./opencode-api.sh config                    # 获取配置
./opencode-api.sh providers                 # 可用模型列表
./opencode-api.sh delete-session ses_xxx    # 删除会话
./opencode-api.sh abort ses_xxx             # 中止会话
./opencode-api.sh messages ses_xxx 50       # 消息历史
```

完整命令列表：运行 `./opencode-api.sh`（无参数）。

### Python

```python
from opencode_api import OpenCodeAPI

client = OpenCodeAPI(
    base_url="http://127.0.0.1:4096",
    username="opencode",
    password="your-password"
)

client.health()
session = client.create_session(title="我的会话")
client.send_message(session["id"], parts=[{"type": "text", "text": "你好"}])
client.list_files(".")
client.search("TODO")
client.get_config()
client.get_providers()
```

### JavaScript

```javascript
const { OpenCodeAPI } = require("./opencode-api.js");

const client = new OpenCodeAPI({
  baseURL: "http://127.0.0.1:4096",
  username: "opencode",
  password: "your-password"
});

await client.health();
const session = await client.createSession({ title: "我的会话" });
await client.sendMessage(session.id, { parts: [{ type: "text", text: "你好" }] });
await client.listFiles(".");
await client.search("TODO");
```

## 完整端点参考

以下端点均可通过脚本封装调用。原始 curl 用法见各脚本源码。

| 类别 | 方法 | 端点 | 说明 |
|------|------|------|------|
| **全局** | GET | `/global/health` | 健康检查 |
| | GET | `/global/config` | 全局配置 |
| | PATCH | `/global/config` | 更新配置 |
| **会话** | GET | `/session` | 列出所有会话 |
| | POST | `/session` | 创建会话 |
| | GET | `/session/{id}` | 会话详情 |
| | DELETE | `/session/{id}` | 删除会话 |
| | POST | `/session/{id}/message` | 发送消息 |
| | GET | `/session/{id}/message` | 消息历史 |
| | POST | `/session/{id}/abort` | 中止会话 |
| | POST | `/session/{id}/fork` | 分叉会话 |
| **项目** | GET | `/project` | 列出项目 |
| | GET | `/project/current` | 当前项目 |
| | POST | `/project/git/init` | 初始化 Git |
| **文件** | GET | `/file` | 列出文件 |
| | GET | `/file/content` | 读取文件 |
| | GET | `/file/status` | 文件状态 |
| | GET | `/find` | 搜索文本 |
| | GET | `/find/file` | 查找文件 |
| **配置** | GET | `/config` | 获取配置 |
| | GET | `/config/providers` | 提供商列表 |
| **MCP** | GET | `/mcp` | MCP 服务器状态 |
| | POST | `/mcp` | 添加 MCP 服务器 |
| **其他** | GET | `/agent` | 可用代理 |
| | GET | `/command` | 斜杠命令 |
| | GET | `/skill` | 可用技能 |

## 认证

服务器启用认证时，所有请求需要 HTTP Basic Auth。脚本自动从环境变量读取凭据，无需手动处理。

## 注意事项

- 会话 ID 以 `ses_` 开头，消息 ID 以 `msg_` 开头
- 未设置密码时可省略认证
- 流式响应使用 SSE 端点 `/event`（当前脚本使用同步请求）
