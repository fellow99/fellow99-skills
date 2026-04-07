# opencode-api Skill

通过 HTTP REST API 与 opencode 服务器交互的完整工具包。

## 📁 文件结构

```
skills/opencode-api/
├── SKILL.md           # 技能文档和 API 参考
├── README.md          # 本文件
├── opencode-api.sh    # Bash 命令行封装
├── opencode-api.js    # JavaScript/Node.js 客户端
└── opencode-api.py    # Python 客户端
```

## ⚙️ 配置

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `OPENCODE_SERVER_BASE_URL` | `http://127.0.0.1:4096` | API 基础 URL |
| `OPENCODE_SERVER_USERNAME` | `opencode` | 用户名 |
| `OPENCODE_SERVER_PASSWORD` | (空) | 密码（如果服务器启用了认证） |

### 在 TOOLS.md 中添加配置

```markdown
### opencode API

- **BASE_URL**: `http://127.0.0.1:4096`
- **USERNAME**: `opencode`
- **PASSWORD**: `$OPENCODE_SERVER_PASSWORD`
```

## 🚀 快速开始

### Bash

```bash
# 设置环境变量
export OPENCODE_SERVER_BASE_URL="http://127.0.0.1:4096"
export OPENCODE_SERVER_USERNAME="opencode"
export OPENCODE_SERVER_PASSWORD="your-password"

# 健康检查
./opencode-api.sh health

# 创建会话
./opencode-api.sh create-session "我的会话"

# 发送消息
./opencode-api.sh send ses_xxx "你好，请帮我分析一下这个代码"

# 列出文件
./opencode-api.sh files .
```

### Python

```python
import os
from opencode_api import OpenCodeAPI

client = OpenCodeAPI(
    base_url=os.getenv('OPENCODE_SERVER_BASE_URL', 'http://127.0.0.1:4096'),
    username=os.getenv('OPENCODE_SERVER_USERNAME', 'opencode'),
    password=os.getenv('OPENCODE_SERVER_PASSWORD', 'your-password')
)

# 健康检查
health = client.health()
print(health)

# 创建会话
session = client.create_session(title='我的会话')

# 发送消息
response = client.send_message(
    session['id'],
    parts=[{'type': 'text', 'text': '你好！'}],
    model={'providerID': 'modelstudio', 'modelID': 'qwen3.5-plus'}
)
print(response)
```

### JavaScript

```javascript
const { OpenCodeAPI } = require('./opencode-api.js');

const client = new OpenCodeAPI({
  baseURL: process.env.OPENCODE_SERVER_BASE_URL || 'http://127.0.0.1:4096',
  username: process.env.OPENCODE_SERVER_USERNAME || 'opencode',
  password: process.env.OPENCODE_SERVER_PASSWORD || 'your-password'
});

// 健康检查
const health = await client.health();
console.log(health);

// 创建会话
const session = await client.createSession({ title: '我的会话' });

// 发送消息
const response = await client.sendMessage(session.id, {
  parts: [{ type: 'text', text: '你好！' }]
});
console.log(response);
```

## 📋 常用操作

### 会话管理

```bash
# 列出所有会话
./opencode-api.sh sessions

# 获取会话详情
./opencode-api.sh get-session ses_xxx

# 删除会话
./opencode-api.sh delete-session ses_xxx

# 中止正在运行的会话
./opencode-api.sh abort ses_xxx
```

### 消息操作

```bash
# 获取消息历史
./opencode-api.sh messages ses_xxx 50

# 发送消息
./opencode-api.sh send ses_xxx "请帮我写一个函数"
```

### 文件操作

```bash
# 列出文件
./opencode-api.sh files .

# 读取文件
./opencode-api.sh read-file ./package.json

# 搜索文本
./opencode-api.sh search "TODO"

# 查找文件
./opencode-api.sh find-files "config"
```

### 项目和配置

```bash
# 列出项目
./opencode-api.sh projects

# 当前项目
./opencode-api.sh current-project

# 获取配置
./opencode-api.sh config

# 获取可用模型
./opencode-api.sh providers
```

## 🔌 API 端点分类

| 类别 | 端点 |
|------|------|
| **全局** | `/global/health`, `/global/config`, `/global/dispose` |
| **会话** | `/session`, `/session/{id}`, `/session/{id}/message`, `/session/{id}/abort` |
| **项目** | `/project`, `/project/current`, `/project/git/init` |
| **文件** | `/file`, `/file/content`, `/file/status` |
| **搜索** | `/find`, `/find/file`, `/find/symbol` |
| **配置** | `/config`, `/config/providers`, `/provider` |
| **MCP** | `/mcp`, `/mcp/{name}/connect` |
| **其他** | `/agent`, `/command`, `/skill`, `/lsp`, `/formatter` |

## 🔐 认证

如果 opencode 服务器设置了 `OPENCODE_SERVER_PASSWORD` 环境变量，所有请求都需要 HTTP Basic Auth：

```bash
# curl 示例
curl -u "$OPENCODE_SERVER_USERNAME:$OPENCODE_SERVER_PASSWORD" "$OPENCODE_SERVER_BASE_URL/global/health"
```

客户端库会自动处理认证：

```python
# Python
client = OpenCodeAPI(
    base_url=os.getenv('OPENCODE_SERVER_BASE_URL', 'http://127.0.0.1:4096'),
    username=os.getenv('OPENCODE_SERVER_USERNAME', 'opencode'),
    password=os.getenv('OPENCODE_SERVER_PASSWORD', 'your-password')
)
```

```javascript
// JavaScript
const client = new OpenCodeAPI({
  baseURL: process.env.OPENCODE_SERVER_BASE_URL || 'http://127.0.0.1:4096',
  username: process.env.OPENCODE_SERVER_USERNAME || 'opencode',
  password: process.env.OPENCODE_SERVER_PASSWORD || 'your-password'
});
```

## ⚠️ 注意事项

1. **默认 URL**：默认使用 `http://127.0.0.1:4096`，Docker 容器内可设置为 `http://host.docker.internal:4096`
2. **会话 ID 格式**：以 `ses_` 开头
3. **消息 ID 格式**：以 `msg_` 开头
4. **认证**：未设置密码时可省略认证参数
5. **流式响应**：当前客户端使用同步请求，如需流式请使用 SSE 端点 `/event`

## 🛠️ 故障排除

### 连接失败

```bash
# 检查服务器是否运行
curl "$OPENCODE_SERVER_BASE_URL/global/health"

# 检查端口
netstat -tlnp | grep 4096
```

### 认证失败

```bash
# 确认密码正确
echo $OPENCODE_SERVER_PASSWORD

# 测试认证
curl -u "$OPENCODE_SERVER_USERNAME:$OPENCODE_SERVER_PASSWORD" "$OPENCODE_SERVER_BASE_URL/global/health"
```

### 会话不存在

确保会话 ID 正确（以 `ses_` 开头），先列出会话确认：

```bash
./opencode-api.sh sessions
```

## 📚 完整文档

详细 API 参考请查看 [SKILL.md](./SKILL.md) 和原始文档 [opencode-server.md](../../opencode-server.md)。
