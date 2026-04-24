# openrouter-image-generation Skill

通过 OpenRouter API 生成图像的完整工具包。

## 文件结构

```
skills/openrouter-image-generation/
├── SKILL.md              # 技能文档和 API 参考
├── README.md             # 本文件
├── generate-image.sh     # Bash 命令行封装
└── generate-image.ps1    # PowerShell 命令行封装（Windows）
```

## 配置

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` | API 基础地址 |
| `OPENROUTER_API_KEY` | (必填) | OpenRouter API 密钥 |
| `OPENROUTER_MODEL` | `openai/gpt-5.4-image-2` | 模型名称 |

### 超时设置

脚本默认设置 **30 分钟（1800 秒）** 超时时间，以适应高分辨率图像生成可能需要的较长等待时间。
- Bash 脚本使用 `curl --max-time 1800`
- PowerShell 脚本使用 `Invoke-RestMethod -TimeoutSec 1800`

### 设置环境变量

**macOS / Linux (Bash/Zsh):**
```bash
export OPENROUTER_API_KEY="sk-or-v1-xxx"
export OPENROUTER_MODEL="google/gemini-2.5-flash-image"  # 可选
```

**Windows (PowerShell):**
```powershell
$env:OPENROUTER_API_KEY = "sk-or-v1-xxx"
$env:OPENROUTER_MODEL = "google/gemini-2.5-flash-image"  # 可选
```

## 快速开始

### Bash (macOS / Linux)

```bash
# 基本用法
./generate-image.sh "A beautiful sunset over mountains"

# 指定模型
./generate-image.sh "A futuristic city" "google/gemini-2.5-flash-image"

# 指定宽高比和分辨率
./generate-image.sh "A nano banana dish" "google/gemini-3-pro-image-preview" "16:9" "4K"
```

### PowerShell (Windows)

```powershell
# 基本用法
.\generate-image.ps1 -Prompt "A beautiful sunset over mountains"

# 指定模型
.\generate-image.ps1 -Prompt "A futuristic city" -Model "google/gemini-2.5-flash-image"

# 指定宽高比和分辨率
.\generate-image.ps1 -Prompt "A nano banana dish" -Model "google/gemini-3-pro-image-preview" -AspectRatio "16:9" -ImageSize "4K"
```

### 在 Agent 中使用

当安装了此技能后，Agent 会自动识别图像生成需求并调用 OpenRouter API。只需描述你想要的图像：

> 帮我生成一张日落山景的图片

> 用 Gemini 模型生成一张 16:9 的科幻城市图，4K 分辨率

Agent 会自动：
1. 读取环境变量配置
2. 构建 API 请求
3. 调用 OpenRouter API
4. 将返回的 base64 图像保存为 PNG 文件

## 支持的模型

| 模型 | 特点 |
|------|------|
| `openai/gpt-5.4-image-2` | 默认模型 |
| `google/gemini-2.5-flash-image` | 快速生成 |
| `google/gemini-3.1-flash-image-preview` | 支持扩展宽高比 |
| `google/gemini-3-pro-image-preview` | 高质量，支持 4K |
| `black-forest-labs/flux.2-pro` | Flux 专业版 |
| `sourceful/riverflow-v2-*` | 支持自定义字体 |

## 参数说明

### 宽高比

| 值 | 像素 | 场景 |
|----|------|------|
| `1:1` | 1024x1024 | 默认 |
| `16:9` | 1344x768 | 宽屏 |
| `9:16` | 768x1344 | 手机竖屏 |
| `4:3` | 1184x864 | 标准横版 |
| `3:4` | 864x1184 | 竖版 |

### 图像尺寸

| 值 | 说明 |
|----|------|
| `1K` | 标准（默认） |
| `2K` | 高分辨率 |
| `4K` | 最高分辨率 |

## 获取 OpenRouter API Key

1. 访问 [openrouter.ai](https://openrouter.ai)
2. 注册/登录账号
3. 进入 Keys 页面创建 API Key
4. 复制 Key 并设置为 `OPENROUTER_API_KEY` 环境变量

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| `OPENROUTER_API_KEY is not set` | 设置环境变量 |
| 响应中无图像 | 检查模型是否支持图像生成 |
| 401 错误 | 检查 API Key 是否正确 |
| 429 错误 | 请求过频，稍后重试 |

## 相关资源

- [OpenRouter 图像生成文档](https://openrouter.ai/docs/guides/overview/multimodal/image-generation)
- [OpenRouter 模型列表](https://openrouter.ai/models?output_modalities=image)
