# fellow99-skills

fellow99 的技能集，用于日常工作自动化和提升效率。

## 可用技能

| 技能 | 说明 | 触发场景 |
|------|------|----------|
| **opencode-api** | 通过 HTTP REST API 与 opencode 服务器交互 | 需要操作 opencode 会话、发送消息、管理文件、查询配置等 |
| **千问 - 文生图** | 使用阿里云百炼千问 API 生成图像 | 需要生成图片、创建海报、插画、封面图等视觉内容 |
| **opus-specs-as-built** | 为已有代码库生成逆向规格文档（as-built spec） | 需要为现有项目编写 spec.md、plan.md、架构文档，或在重构前基线化系统 |
| **openrouter-image-generation** | 使用 OpenRouter API 生成图像 | 需要生成图片、创建海报、插画、封面图等视觉内容，支持 Gemini、Flux、Sourceful 等模型 |
| **specs-based-devflow** | 全流程开发工作流：需求 → 规约 → 开发 → Code Review → 测试 → 缺陷修复 → 回归测试 | 需要从需求到交付完整地完成一个功能开发，涉及多阶段、多 artifact 的规范化流程 |
| **codegraph-cli** | 使用 `codegraph` CLI 通过语义知识图谱探索、搜索和理解代码库 | 需要理解代码库结构、查找符号定义、分析调用关系、评估变更影响，替代繁琐的 grep/find/Read 循环 |
| **esp32-image-to-argb** | 将 PNG/JPG 图片转换为 ESP32 兼容的 C 头文件，支持 5 种像素格式（RGB565/ARGB1555/ARGB8888/ARGB_4444/ALPHA_8），生成 LVGL 或 TFT_eSPI 格式输出 | 需要将图片转为 ESP32 C 数组、嵌入式显示资源、LVGL 图像资产、TFT_eSPI 图像转换 |
| **harmonyos-app-dev** | 鸿蒙应用开发全流程：从项目搭建、ArkTS/ArkUI 编码、Stage 模型到发布前代码审查与安全审计 | 需要开发鸿蒙应用、编写 ArkTS/ArkUI 代码、使用 Stage 模型、鸿蒙代码审查、安全审计、质量门禁 |
| **harmonyos-app-testing** | 通过 `hdc` 工具链驱动 HarmonyOS/OpenHarmony 应用：构建→安装→启动→检查→交互，无需 DevEco Studio GUI | 需要启动鸿蒙模拟器、安装/启动 HAP、查看 UI 树、过滤 hilog 日志、注入点击/滑动/手势/按键、截图、录屏、鸿蒙应用自动化测试 |

> 💡 每个技能的详细用法请参考 `skills/<skill-name>/SKILL.md` 和 `skills/<skill-name>/README.md`

## 前置要求

- 已安装 Node.js 环境
- 能够运行 `npx` 命令

## 安装

### 快速安装（推荐）

```bash
npx skills add https://github.com/fellow99/fellow99-skills
```

### 按需安装单个技能

`npx skills add` 支持安装本仓库中的单个技能：

```bash
npx skills add https://github.com/fellow99/fellow99-skills --skill opencode-api
npx skills add https://github.com/fellow99/fellow99-skills --skill qwen-image
npx skills add https://github.com/fellow99/fellow99-skills --skill opus-specs-as-built
npx skills add https://github.com/fellow99/fellow99-skills --skill openrouter-image-generation
npx skills add https://github.com/fellow99/fellow99-skills --skill specs-based-devflow
npx skills add https://github.com/fellow99/fellow99-skills --skill codegraph-cli
npx skills add https://github.com/fellow99/fellow99-skills --skill esp32-image-to-argb
npx skills add https://github.com/fellow99/fellow99-skills --skill harmonyos-app-dev
npx skills add https://github.com/fellow99/fellow99-skills --skill harmonyos-app-testing
```

### 告诉 AI Agent

直接告诉你的 AI Agent（OpenCode / Claude Code / Codex 等）：

> 请帮我安装 github.com/fellow99/fellow99-skills 中的 Skills

