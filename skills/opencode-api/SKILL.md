# opencode-api Skill

通过 HTTP REST API 与 opencode 服务器交互。

## 配置

本 Skill 默认读取以下环境变量：

- **OPENCODE_SERVER_BASE_URL**: opencode 服务器地址（默认：`http://127.0.0.1:4096`）
- **OPENCODE_SERVER_USERNAME**: 用户名（默认：`opencode`）
- **OPENCODE_SERVER_PASSWORD**: 密码（如果服务器启用了认证）

### 示例（在 shell 中设置）

```bash
export OPENCODE_SERVER_BASE_URL="http://127.0.0.1:4096"
export OPENCODE_SERVER_USERNAME="opencode"
export OPENCODE_SERVER_PASSWORD="your_password"
```

## 认证

如果 opencode 服务器设置了认证，所有请求都需要 HTTP Basic Auth：

- 用户名：`OPENCODE_SERVER_USERNAME` 的值（默认：`opencode`）
- 密码：`OPENCODE_SERVER_PASSWORD` 的值

## 核心 API 封装

### 1. 检查服务器健康状态

```bash
curl -u "$OPENCODE_SERVER_USERNAME:$OPENCODE_SERVER_PASSWORD" "$OPENCODE_SERVER_BASE_URL/global/health"
```

响应：
```json
{"healthy": true, "version": "0.0.3"}
```

### 2. 列出所有会话

```bash
curl -u "$OPENCODE_SERVER_USERNAME:$OPENCODE_SERVER_PASSWORD" "$OPENCODE_SERVER_BASE_URL/session"
```

### 3. 创建新会话

```bash
curl -u "$OPENCODE_SERVER_USERNAME:$OPENCODE_SERVER_PASSWORD" -X POST "$OPENCODE_SERVER_BASE_URL/session" \
  -H "Content-Type: application/json" \
  -d '{"title": "我的会话"}'
```

### 4. 发送消息（Prompt）

```bash
curl -u "$OPENCODE_SERVER_USERNAME:$OPENCODE_SERVER_PASSWORD" -X POST "$OPENCODE_SERVER_BASE_URL/session/{sessionID}/message" \
  -H "Content-Type: application/json" \
  -d '{
    "parts": [
      {"type": "text", "text": "你的问题或指令"}
    ],
    "model": {
      "providerID": "modelstudio",
      "modelID": "qwen3.5-plus"
    }
  }'
```

### 5. 获取会话消息历史

```bash
curl -u "$OPENCODE_SERVER_USERNAME:$OPENCODE_SERVER_PASSWORD" "$OPENCODE_SERVER_BASE_URL/session/{sessionID}/message?limit=50"
```

### 6. 列出所有项目

```bash
curl -u "$OPENCODE_SERVER_USERNAME:$OPENCODE_SERVER_PASSWORD" "$OPENCODE_SERVER_BASE_URL/project"
```

### 7. 获取当前项目

```bash
curl -u "$OPENCODE_SERVER_USERNAME:$OPENCODE_SERVER_PASSWORD" "$OPENCODE_SERVER_BASE_URL/project/current"
```

### 8. 文件操作

**列出文件：**
```bash
curl -u "$OPENCODE_SERVER_USERNAME:$OPENCODE_SERVER_PASSWORD" "$OPENCODE_SERVER_BASE_URL/file?path=."
```

**读取文件内容：**
```bash
curl -u "$OPENCODE_SERVER_USERNAME:$OPENCODE_SERVER_PASSWORD" "$OPENCODE_SERVER_BASE_URL/file/content?path=./package.json"
```

**搜索文本：**
```bash
curl -u "$OPENCODE_SERVER_USERNAME:$OPENCODE_SERVER_PASSWORD" "$OPENCODE_SERVER_BASE_URL/find?pattern=TODO"
```

### 9. 会话管理

**删除会话：**
```bash
curl -u "$OPENCODE_SERVER_USERNAME:$OPENCODE_SERVER_PASSWORD" -X DELETE "$OPENCODE_SERVER_BASE_URL/session/{sessionID}"
```

**中止正在运行的会话：**
```bash
curl -u "$OPENCODE_SERVER_USERNAME:$OPENCODE_SERVER_PASSWORD" -X POST "$OPENCODE_SERVER_BASE_URL/session/{sessionID}/abort"
```

**分叉会话：**
```bash
curl -u "$OPENCODE_SERVER_USERNAME:$OPENCODE_SERVER_PASSWORD" -X POST "$OPENCODE_SERVER_BASE_URL/session/{sessionID}/fork" \
  -H "Content-Type: application/json" \
  -d '{"messageID": "msg_xxx"}'
```

### 10. 获取配置和提供商

```bash
# 获取配置
curl -u "$OPENCODE_SERVER_USERNAME:$OPENCODE_SERVER_PASSWORD" "$OPENCODE_SERVER_BASE_URL/config"

# 获取可用提供商和模型
curl -u "$OPENCODE_SERVER_USERNAME:$OPENCODE_SERVER_PASSWORD" "$OPENCODE_SERVER_BASE_URL/config/providers"
```

## 使用示例

### 示例 1：创建会话并发送消息

```bash
# 1. 创建会话
SESSION=$(curl -s -u "$OPENCODE_SERVER_USERNAME:$OPENCODE_SERVER_PASSWORD" -X POST "$OPENCODE_SERVER_BASE_URL/session" \
  -H "Content-Type: application/json" \
  -d '{"title": "测试会话"}' | jq -r '.id')

# 2. 发送消息
curl -s -u "$OPENCODE_SERVER_USERNAME:$OPENCODE_SERVER_PASSWORD" -X POST "$OPENCODE_SERVER_BASE_URL/session/$SESSION/message" \
  -H "Content-Type: application/json" \
  -d '{
    "parts": [{"type": "text", "text": "你好，请介绍一下你自己"}]
  }' | jq .
```

### 示例 2：查看当前工作区文件状态

```bash
curl -s -u "$OPENCODE_SERVER_USERNAME:$OPENCODE_SERVER_PASSWORD" "$OPENCODE_SERVER_BASE_URL/file/status" | jq .
```

### 示例 3：搜索代码中的特定模式

```bash
curl -s -u "$OPENCODE_SERVER_USERNAME:$OPENCODE_SERVER_PASSWORD" "$OPENCODE_SERVER_BASE_URL/find?pattern=console.log" | jq .
```

## 完整端点参考

| 类别 | 方法 | 端点 | 描述 |
|------|------|------|------|
| **全局** | GET | `$OPENCODE_SERVER_BASE_URL/global/health` | 健康检查 |
| | GET | `$OPENCODE_SERVER_BASE_URL/global/config` | 获取全局配置 |
| | PATCH | `$OPENCODE_SERVER_BASE_URL/global/config` | 更新全局配置 |
| **会话** | GET | `$OPENCODE_SERVER_BASE_URL/session` | 列出所有会话 |
| | POST | `$OPENCODE_SERVER_BASE_URL/session` | 创建会话 |
| | GET | `$OPENCODE_SERVER_BASE_URL/session/{id}` | 获取会话详情 |
| | DELETE | `$OPENCODE_SERVER_BASE_URL/session/{id}` | 删除会话 |
| | POST | `$OPENCODE_SERVER_BASE_URL/session/{id}/message` | 发送消息 |
| | GET | `$OPENCODE_SERVER_BASE_URL/session/{id}/message` | 获取消息列表 |
| | POST | `$OPENCODE_SERVER_BASE_URL/session/{id}/abort` | 中止会话 |
| | POST | `$OPENCODE_SERVER_BASE_URL/session/{id}/fork` | 分叉会话 |
| **项目** | GET | `$OPENCODE_SERVER_BASE_URL/project` | 列出项目 |
| | GET | `$OPENCODE_SERVER_BASE_URL/project/current` | 当前项目 |
| | POST | `$OPENCODE_SERVER_BASE_URL/project/git/init` | 初始化 git |
| **文件** | GET | `$OPENCODE_SERVER_BASE_URL/file` | 列出文件 |
| | GET | `$OPENCODE_SERVER_BASE_URL/file/content` | 读取文件 |
| | GET | `$OPENCODE_SERVER_BASE_URL/file/status` | 文件状态 |
| | GET | `$OPENCODE_SERVER_BASE_URL/find` | 搜索文本 |
| | GET | `$OPENCODE_SERVER_BASE_URL/find/file` | 查找文件 |
| **配置** | GET | `$OPENCODE_SERVER_BASE_URL/config` | 获取配置 |
| | GET | `$OPENCODE_SERVER_BASE_URL/config/providers` | 获取提供商列表 |
| **MCP** | GET | `$OPENCODE_SERVER_BASE_URL/mcp` | MCP 服务器状态 |
| | POST | `$OPENCODE_SERVER_BASE_URL/mcp` | 添加 MCP 服务器 |
| **代理** | GET | `$OPENCODE_SERVER_BASE_URL/agent` | 列出可用代理 |
| **命令** | GET | `$OPENCODE_SERVER_BASE_URL/command` | 列出斜杠命令 |
| **技能** | GET | `$OPENCODE_SERVER_BASE_URL/skill` | 列出可用技能 |

## 注意事项

1. **环境变量**：确保在使用前设置好 `OPENCODE_SERVER_BASE_URL`、`OPENCODE_SERVER_USERNAME` 和 `OPENCODE_SERVER_PASSWORD`
2. **默认 URL**：默认使用 `http://127.0.0.1:4096`，Docker 环境中可设置为 `http://host.docker.internal:4096`
3. **认证**：如果服务器未设置密码，可以省略 `-u` 参数
4. **会话 ID 格式**：以 `ses_` 开头
5. **消息 ID 格式**：以 `msg_` 开头
6. **流式响应**：`/session/{id}/message` 默认返回完整响应，如需流式可使用 SSE 端点

## 错误处理

- `400` - 请求格式错误
- `401` - 认证失败（检查用户名/密码）
- `404` - 资源不存在（会话 ID、文件路径等）
- `500` - 服务器内部错误
