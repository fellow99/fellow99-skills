---
name: openrouter-image-generation
description: 使用 OpenRouter API 生成图像。当用户需要生成图片、创建图像、文生图、制作海报、生成插画、创建视觉内容时使用此技能。支持所有 OpenRouter 上的图像生成模型，包括 Gemini、Flux、Sourceful 等。默认使用 openai/gpt-5.4-image-2 模型。
compatibility: 需要环境变量 OPENROUTER_API_KEY（必填）、OPENROUTER_BASE_URL（可选）、OPENROUTER_MODEL（可选），curl 命令
---

# OpenRouter 图像生成技能

## 触发时机

当用户提到以下任何内容时，使用此技能：
- 生成图片/图像/画面
- 文生图、文字转图片
- 创建海报、插画、封面图
- 基于描述生成视觉内容
- 使用 OpenRouter 的图像生成模型（Gemini、Flux、Sourceful 等）

## 前置条件

1. **API Key**: 从环境变量 `OPENROUTER_API_KEY` 读取，或从用户输入中提取，**必填**
2. **Base URL**: 从环境变量 `OPENROUTER_BASE_URL` 读取，或从用户输入中提取，默认 `https://openrouter.ai/api/v1`
3. **模型**: 从环境变量 `OPENROUTER_MODEL` 读取，或从用户输入中提取，默认 `openai/gpt-5.4-image-2`
4. **提示词**: 用户需要提供图像生成的文本描述
5. **超时设置**: 脚本默认设置 30 分钟（1800 秒）超时，以应对高分辨率图像生成的长时间等待

## 支持的模型

通过 OpenRouter 可以使用多种图像生成模型，常见的包括：

| 模型 | 特点 |
|------|------|
| `openai/gpt-5.4-image-2` | 默认模型，高质量图像生成 |
| `google/gemini-2.5-flash-image` | 快速生成，支持文本+图像输出 |
| `google/gemini-3.1-flash-image-preview` | 支持扩展宽高比（1:4, 4:1, 1:8, 8:1）和 0.5K 分辨率 |
| `google/gemini-3-pro-image-preview` | 高质量，支持 4K 分辨率 |
| `black-forest-labs/flux.2-pro` | Flux 专业版 |
| `black-forest-labs/flux.2-flex` | Flux 灵活版 |
| `sourceful/riverflow-v2-standard-preview` | 支持自定义字体和超分辨率 |

可通过以下 API 查询所有支持图像生成的模型：
```bash
curl "https://openrouter.ai/api/v1/models?output_modalities=image"
```

## API 调用

### 基本调用

```bash
curl "$OPENROUTER_BASE_URL/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -d '{
  "model": "$OPENROUTER_MODEL",
  "messages": [
    {
      "role": "user",
      "content": "Generate a beautiful sunset over mountains"
    }
  ],
  "modalities": ["image", "text"]
}'
```

### 带图像配置的高级调用

```bash
curl "$OPENROUTER_BASE_URL/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -d '{
  "model": "$OPENROUTER_MODEL",
  "messages": [
    {
      "role": "user",
      "content": "Create a picture of a nano banana dish in a fancy restaurant"
    }
  ],
  "modalities": ["image", "text"],
  "image_config": {
    "aspect_ratio": "16:9",
    "image_size": "4K"
  }
}'
```

## 参数说明

### 必须参数

| 参数 | 说明 |
|------|------|
| `OPENROUTER_API_KEY` | API 密钥，必填 |
| `prompt` | 图像生成的文本描述 |

### 可选参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` | API 基础地址 |
| `OPENROUTER_MODEL` | `openai/gpt-5.4-image-2` | 模型名称 |
| `modalities` | `["image", "text"]` | 输出模态，根据模型能力设置 |
| `aspect_ratio` | `1:1` | 宽高比，见下方表格 |
| `image_size` | `1K` | 图像尺寸：0.5K/1K/2K/4K |

### 宽高比参考

| 宽高比 | 像素 | 适用场景 |
|--------|------|----------|
| `1:1` | 1024x1024 | 默认，正方形 |
| `2:3` | 832x1248 | 竖版肖像 |
| `3:2` | 1248x832 | 横版风景 |
| `3:4` | 864x1184 | 竖版 |
| `4:3` | 1184x864 | 标准横版 |
| `4:5` | 896x1152 | Instagram 竖版 |
| `5:4` | 1152x896 | 横版 |
| `9:16` | 768x1344 | 手机竖屏 |
| `16:9` | 1344x768 | 宽屏 |
| `21:9` | 1536x672 | 超宽屏 |

### 扩展宽高比（仅 `google/gemini-3.1-flash-image-preview`）

| 宽高比 | 适用场景 |
|--------|----------|
| `1:4` | 滚动轮播、垂直 UI 元素 |
| `4:1` | Hero Banner、水平布局 |
| `1:8` | 通知头部、窄垂直空间 |
| `8:1` | 宽幅 Banner、全景 |

### 图像尺寸

| 尺寸 | 说明 |
|------|------|
| `0.5K` | 低分辨率，优化效率（仅 Gemini 3.1） |
| `1K` | 标准分辨率（默认） |
| `2K` | 高分辨率 |
| `4K` | 最高分辨率 |

### 特殊配置（仅 Sourceful 模型）

**font_inputs**: 自定义字体渲染
```json
{
  "image_config": {
    "font_inputs": [
      {
        "font_url": "https://example.com/fonts/custom-font.ttf",
        "text": "Hello World"
      }
    ]
  }
}
```

**super_resolution_references**: 超分辨率参考图
```json
{
  "image_config": {
    "super_resolution_references": [
      "https://example.com/reference1.jpg",
      "https://example.com/reference2.jpg"
    ]
  }
}
```

## 响应格式

API 返回的图像为 base64 编码的 data URL：

```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "I've generated a beautiful sunset image for you.",
        "images": [
          {
            "type": "image_url",
            "image_url": {
              "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
            }
          }
        ]
      }
    }
  ]
}
```

### 图像格式

- **格式**: base64 编码的 data URL
- **类型**: 通常为 PNG (`data:image/png;base64,`)
- **多张图像**: 部分模型可一次生成多张图像

## 工作流程

1. **确认配置**: 检查 `OPENROUTER_API_KEY` 是否已设置
2. **收集提示词**: 获取详细的图像描述
3. **确认参数**: 询问是否需要自定义模型、宽高比、分辨率等
4. **执行调用**: 使用 curl 发起 API 请求
5. **保存图像**: 将 base64 数据解码并保存为 PNG 文件
6. **返回结果**: 展示生成的图像
7. **错误处理**: 如遇错误，解释原因并提供解决方案

## 最佳实践

### 提示词撰写

- **具体详细**: 描述主体、场景、风格、光照、构图
- **结构化**: 按"主体 + 场景 + 风格 + 细节"顺序
- **英文优先**: 使用英文提示词通常效果更好

### 参数建议

- **测试阶段**: 使用默认模型 + 1:1 宽高比 + 1K 尺寸
- **高质量输出**: 使用 `google/gemini-3-pro-image-preview` + 4K 尺寸
- **宽屏场景**: 使用 16:9 宽高比

### 模型选择

- **通用场景**: `openai/gpt-5.4-image-2`（默认）
- **快速生成**: `google/gemini-2.5-flash-image`
- **最高质量**: `google/gemini-3-pro-image-preview`
- **特殊宽高比**: `google/gemini-3.1-flash-image-preview`
- **文字渲染**: `sourceful/riverflow-v2-*`（支持 font_inputs）

### modalities 设置

- **输出文本+图像**的模型（如 Gemini）：使用 `["image", "text"]`
- **仅输出图像**的模型（如 Flux、Sourceful）：使用 `["image"]`

## 示例调用

### 示例 1：基本图像生成

```bash
export OPENROUTER_API_KEY="sk-or-v1-xxx"

curl "https://openrouter.ai/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -d '{
  "model": "openai/gpt-5.4-image-2",
  "messages": [
    {
      "role": "user",
      "content": "Generate a beautiful sunset over mountains"
    }
  ],
  "modalities": ["image", "text"]
}'
```

### 示例 2：自定义宽高比和分辨率

```bash
curl "https://openrouter.ai/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -d '{
  "model": "google/gemini-3-pro-image-preview",
  "messages": [
    {
      "role": "user",
      "content": "Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme"
    }
  ],
  "modalities": ["image", "text"],
  "image_config": {
    "aspect_ratio": "16:9",
    "image_size": "4K"
  }
}'
```

### 示例 3：仅图像输出模型

```bash
curl "https://openrouter.ai/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -d '{
  "model": "black-forest-labs/flux.2-pro",
  "messages": [
    {
      "role": "user",
      "content": "A futuristic cityscape at night with neon lights"
    }
  ],
  "modalities": ["image"]
}'
```

## 故障排除

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 响应中无图像 | 模型不支持图像输出 | 检查模型的 `output_modalities` |
| 响应中无图像 | `modalities` 参数设置错误 | 图像专用模型用 `["image"]`，混合模型用 `["image", "text"]` |
| 模型不存在 | 模型名错误 | 使用 Models API 查询可用模型 |
| 401 认证失败 | API Key 无效 | 检查 `OPENROUTER_API_KEY` |
| 429 限流 | 请求过频 | 降低请求频率，添加重试延迟 |

## 相关资源

- [OpenRouter 图像生成文档](https://openrouter.ai/docs/guides/overview/multimodal/image-generation)
- [OpenRouter 模型列表](https://openrouter.ai/models?output_modalities=image)
- [OpenRouter API 参考](https://openrouter.ai/docs/api/api-reference/chat/send-chat-completion-request)
