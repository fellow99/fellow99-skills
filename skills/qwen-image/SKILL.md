---
name: 千问 - 文生图
description: 使用阿里云百炼千问文生图 API 生成图像。当用户需要生成图片、创建图像、文生图、制作海报、生成插画、创建视觉内容时使用此技能。支持 qwen-image-2.0、qwen-image-plus、wan2.7-image-pro 等模型。必须显式指定 model 参数，默认生成 1 张图片，其他参数使用模型默认值但允许用户自定义。
compatibility: 需要环境变量 DASHSCOPE_API_KEY，curl 命令
---

# 千问 - 文生图技能

## 触发时机

当用户提到以下任何内容时，使用此技能：
- 生成图片/图像/画面
- 文生图、文字转图片
- 创建海报、插画、封面图
- 基于描述生成视觉内容
- 使用 qwen-image、wan2.7-image 等模型

## 前置条件

1. **API Key**: 从环境变量 `DASHSCOPE_API_KEY` 读取
2. **模型指定**: 用户必须显式指定要使用的模型
3. **提示词**: 用户需要提供图像生成的文本描述

## 支持的模型

### 千问系列（同步调用）
- `qwen-image-2.0-pro` - 擅长文本渲染，适合海报、PPT、图表（推荐测试使用）
- `qwen-image-2.0` - 标准版本
- `qwen-image-plus` - 增强版
- `qwen-image-max` - 旗舰版

### 万相系列（异步调用）
- `wan2.7-image-pro` - 功能最全，支持 4K 分辨率、组图生成
- `wan2.7-image` - 标准版
- `wan2.6-image` - 旧版本

## API 调用流程

### 千问系列（同步）

```bash
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation' \
--header 'Content-Type: application/json' \
--header "Authorization: Bearer $DASHSCOPE_API_KEY" \
--data '{
    "model": "<MODEL_NAME>",
    "input": {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "text": "<PROMPT_TEXT>"
                    }
                ]
            }
        ]
    },
    "parameters": {
        "negative_prompt": "低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感，人脸无细节，过度光滑，画面具有 AI 感。构图混乱。文字模糊，扭曲。",
        "prompt_extend": true,
        "watermark": false,
        "size": "2048*2048"
    }
}'
```

### 万相系列（异步）

**步骤 1：创建任务**

```bash
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/image-generation/generation' \
--header 'Content-Type: application/json' \
--header "Authorization: Bearer $DASHSCOPE_API_KEY" \
--header "X-DashScope-Async: enable" \
--data '{
    "model": "<MODEL_NAME>",
    "input": {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"text": "<PROMPT_TEXT>"}
                ]
            }
        ]
    },
    "parameters": {
        "size": "2K",
        "n": 1,
        "watermark": false,
        "thinking_mode": true
    }
}'
```

**步骤 2：查询结果**

使用返回的 `task_id` 查询：

```bash
curl -X GET "https://dashscope.aliyuncs.com/api/v1/tasks/<TASK_ID>" \
--header "Authorization: Bearer $DASHSCOPE_API_KEY"
```

## 参数说明

### 必须参数

| 参数 | 说明 |
|------|------|
| `model` | 模型名称，用户必须显式指定 |
| `prompt` | 图像生成的文本描述 |

### 可选参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `n` | 1 | 生成图片数量 |
| `size` | 模型默认 | 分辨率，格式："宽*高" |
| `watermark` | false | 是否添加水印 |
| `prompt_extend` | true | 是否智能改写提示词（千问系列） |
| `negative_prompt` | 见上方 | 反向提示词（千问系列） |
| `thinking_mode` | true | 思考模式（万相系列） |
| `enable_sequential` | false | 组图模式（万相系列） |

### 分辨率参考

**千问 qwen-image-2.0 系列**：
- 默认：`2048*2048`
- 范围：`512*512` – `2048*2048`

**万相 wan2.7-image-pro**：
- `1K` = 1024*1024
- `2K` = 2048*2048
- `4K` = 4096*4096

## 输出处理

API 返回的图像 URL 有效期为 **24 小时**，必须：

1. 立即展示给用户
2. 提示用户及时下载保存
3. 建议用户转存到持久化存储

### 响应解析

**成功响应**：
```json
{
    "output": {
        "choices": [
            {
                "message": {
                    "content": [
                        {
                            "image": "https://..."
                        }
                    ]
                }
            }
        ]
    },
    "status_code": 200
}
```

**错误处理**：
- `DataInspectionFailed`: 提示词触发内容安全审核，需修改文本
- `Throttling` / HTTP 429: 触发限流，稍后重试
- 其他错误：参考 [错误码文档](https://help.aliyun.com/zh/model-studio/developer-reference/error-code)

## 工作流程

1. **确认模型**: 询问用户或使用默认测试模型 `qwen-image-2.0-pro`
2. **收集提示词**: 获取详细的图像描述
3. **确认参数**: 询问是否需要自定义分辨率、数量等
4. **执行调用**: 使用 curl 发起 API 请求
5. **返回结果**: 展示生成的图像 URL，提醒 24 小时有效期
6. **错误处理**: 如遇错误，解释原因并提供解决方案

## 最佳实践

### 提示词撰写

- **具体详细**: 描述主体、场景、风格、光照、构图
- **结构化**: 按"主体 + 场景 + 风格 + 细节"顺序
- **避免歧义**: 不使用模糊词汇

### 参数建议

- **测试阶段**: 使用 `qwen-image-2.0-pro` + `2048*2048`
- **生产环境**: 根据需求选择模型和分辨率
- **批量生成**: 万相系列支持组图模式（`enable_sequential=true`）

### 内容安全

- 避免生成涉及品牌商标、名人肖像、版权 IP 的内容
- 确保提示词符合法律法规
- 如遇审核失败，调整措辞后重试

## 示例调用

### 示例 1：生成写实人像

```bash
export DASHSCOPE_API_KEY="sk-xxx"

curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation' \
--header 'Content-Type: application/json' \
--header "Authorization: Bearer $DASHSCOPE_API_KEY" \
--data '{
    "model": "qwen-image-2.0-pro",
    "input": {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "text": "一位约 20 岁的亚洲年轻女性，齐刘海乌黑长直发，身穿浅绿色马海毛毛衣，坐于复古碎花沙发上，手持红色番茄，背景为做旧青绿色墙面，自然光束斜射，胶片颗粒感，复古文艺风格"
                    }
                ]
            }
        ]
    },
    "parameters": {
        "negative_prompt": "低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感",
        "prompt_extend": true,
        "watermark": false,
        "size": "2048*2048"
    }
}'
```

### 示例 2：生成电商海报

```bash
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation' \
--header 'Content-Type: application/json' \
--header "Authorization: Bearer $DASHSCOPE_API_KEY" \
--data '{
    "model": "qwen-image-2.0-pro",
    "input": {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "text": "C4D 风格电商海报，清新蓝色调，立体艺术字体展示促销信息，主体为宠物粮产品，3D 建模小猫点缀，科技感机械装置，明亮商业灯光，超高清渲染"
                    }
                ]
            }
        ]
    },
    "parameters": {
        "watermark": false,
        "size": "2048*2048"
    }
}'
```

## 故障排除

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| URL 失效 | 超过 24 小时 | 重新生成或提前下载保存 |
| 审核失败 | 提示词违规 | 修改敏感内容后重试 |
| 限流错误 | 请求过频 | 降低频率，添加重试延迟 |
| 模型不存在 | 模型名错误 | 检查模型名称拼写 |

## 相关资源

- [千问 API 文档](https://help.aliyun.com/zh/model-studio/qwen-image-api)
- [万相 API 文档](https://help.aliyun.com/zh/model-studio/wan-image-generation-and-editing-api-reference)
- [错误码参考](https://help.aliyun.com/zh/model-studio/developer-reference/error-code)
- [Prompt 指南](https://help.aliyun.com/zh/model-studio/text-to-image-prompt)
