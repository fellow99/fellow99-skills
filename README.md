# fellow99-skills

fellow99 的技能集，用于日常工作自动化和提升效率。

## 可用技能

| 技能 | 说明 | 触发场景 |
|------|------|----------|
| **opencode-api** | 通过 HTTP REST API 与 opencode 服务器交互 | 需要操作 opencode 会话、发送消息、管理文件、查询配置等 |
| **千问 - 文生图** | 使用阿里云百炼千问 API 生成图像 | 需要生成图片、创建海报、插画、封面图等视觉内容 |
| **opus-specs-as-built** | 为已有代码库生成逆向规格文档（as-built spec） | 需要为现有项目编写 spec.md、plan.md、架构文档，或在重构前基线化系统 |
| **openrouter-image-generation** | 使用 OpenRouter API 生成图像 | 需要生成图片、创建海报、插画、封面图等视觉内容，支持 Gemini、Flux、Sourceful 等模型 |
| **codegraph-cli** | 使用 `codegraph` CLI 通过语义知识图谱探索、搜索和理解代码库 | 需要理解代码库结构、查找符号定义、分析调用关系、评估变更影响，替代繁琐的 grep/find/Read 循环 |
| **esp32-image-to-argb** | 将 PNG/JPG 图片转换为 ESP32 兼容的 C 头文件，支持 5 种像素格式（RGB565/ARGB1555/ARGB8888/ARGB_4444/ALPHA_8），生成 LVGL 或 TFT_eSPI 格式输出 | 需要将图片转为 ESP32 C 数组、嵌入式显示资源、LVGL 图像资产、TFT_eSPI 图像转换 |

> 💡 每个技能的详细用法请参考 `skills/<skill-name>/SKILL.md` 和 `skills/<skill-name>/README.md`

## 前置要求

- 已安装 Node.js 环境
- 能够运行 `npx bun` 命令

## 安装

### 快速安装（推荐）

```bash
npx skills add fellow99/fellow99-skills
```

### 发布到 ClawHub / OpenClaw

本仓库支持将每个 `skills/*` 目录作为独立 ClawHub skill 发布。

```bash
# 预览将要发布的变更
./scripts/sync-clawhub.sh --dry-run

# 发布 ./skills 下所有已变更的 skill
./scripts/sync-clawhub.sh --all
```

ClawHub 按"单个 skill"安装，不是把整个 marketplace 一次性装进去。发布后，用户可以按需安装：

```bash
clawhub install opencode-api
clawhub install qwen-image
clawhub install opus-specs-as-built
clawhub install openrouter-image-generation
clawhub install codegraph-cli
clawhub install esp32-image-to-argb
```

根据 ClawHub 的 registry 规则，发布到 ClawHub 的 skill 会以 `MIT-0` 许可分发。

### 注册插件市场

在 Claude Code 中运行：

```bash
/plugin marketplace add fellow99/fellow99-skills
```

### 安装技能

**方式一：通过浏览界面**

1. 选择 **Browse and install plugins**
2. 选择 **fellow99-skills**
3. 选择 **fellow99-skills** 插件
4. 选择 **Install now**

**方式二：直接安装**

```bash
# 安装 marketplace 中唯一的插件
/plugin install fellow99-skills@fellow99-skills
```

**方式三：告诉 Agent**

直接告诉 Claude Code：

> 请帮我安装 github.com/fellow99/fellow99-skills 中的 Skills

