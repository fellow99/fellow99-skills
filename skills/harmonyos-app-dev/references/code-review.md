# 代码评审清单（Code Review）

> **本文档是开发完成后的 Quality Gate**。在交付前对照本清单逐项检查，发现问题修正后再次评审，直到所有 🔴 关键问题清零、🟠 高优先级问题有处置方案。
>
> 内容融合自 harmonyos-review skill 的 checklist + 流程，并交叉引用 harmonyos-app-dev 各专题 reference 中的"正确做法"。

---

## 评审流程（3 步）

### Step 1: 快速扫描（自动化命令）

并行运行以识别明显问题：

```bash
# 🔴 硬编码凭据
grep -rn "password\|secret\|api[_-]key\|token" --include="*.json5" --include="*.ets" .

# 🔴 console 替代 hilog
grep -rn "console\." --include="*.ets" . | grep -v "hilog"

# 🔴 async forEach 反模式
grep -rn "forEach.*await\|forEach(.*async" --include="*.ets" .

# 🟠 API 版本检查
grep -rn "compileSdkVersion\|targetSdkVersion" --include="*.json5" .

# 🟠 已弃用 API
grep -rn "@Deprecated\|deprecated" --include="*.ets" .

# 🟠 空 catch 块
grep -rn "catch.*{\s*}" --include="*.ets" .

# 🟡 类型断言滥用
grep -rn "as any\|as unknown" --include="*.ets" .

# 🟡 magic numbers（>2 位数字）
grep -rnE "[^a-zA-Z0-9_][0-9]{3,}[^a-zA-Z0-9_]" --include="*.ets" .
```

### Step 2: 深度分析（按清单分类逐项检查）

逐条对照下方 10 个评审类别，每项标注：✅ 通过 / 🟡 待改进 / 🟠 应修复 / 🔴 必须修复。

### Step 3: 生成报告

使用 [`review-report-template.md`](review-report-template.md) 输出 markdown 报告，保存至 `docs/YYYY-MM-DD-review.md`。报告需包含：
- 摘要表（各类别问题数 + 风险等级）
- 详细问题（含 `file:line` 引用 + 代码片段 + 修复建议）
- 修复优先级建议（按 🔴/🟠/🟡 分组 + 预估工时）
- 整体评分（A-F 各维度评级）

---

## 问题优先级定义

| 等级 | 含义 | 处理时机 |
|------|------|---------|
| 🔴 关键 | 阻塞发布（安全、数据丢失、崩溃） | 立即修复 |
| 🟠 高 | 影响质量（性能、可维护性） | 当前迭代修复 |
| 🟡 中 | 技术债（代码风格、轻微优化） | 考虑修复 |
| ⚪ 低 | 可选优化 | 长期改进 |

---

## 0. 版本与兼容性

| # | 检查项 | 等级 | 参考 |
|---|--------|------|------|
| 0.1 | Target API 是否为推荐版本（API 20+ 对应 HarmonyOS 6.0.0） | 🟠 | [`extended.md`](extended.md) |
| 0.2 | DevEco Studio 版本是否兼容 target API | 🟠 | — |
| 0.3 | 弃用 API 是否有迁移计划 | 🟠 | — |
| 0.4 | 可选系统能力是否用 `canIUse()` 检测 | 🟠 | — |
| 0.5 | 使用 Stage 模型而非 FA 模型 | 🔴 | [`stage-model.md`](stage-model.md) |

---

## 1. 安全规范

| # | 检查项 | 等级 | 参考（正确做法） |
|---|--------|------|---------------|
| 1.1 | `build-profile.json5` 无硬编码签名密码 | 🔴 | [`security-and-permissions.md`](security-and-permissions.md) 规则1 |
| 1.2 | 代码无硬编码 API key / secret / token | 🔴 | 同上 |
| 1.3 | 敏感数据库启用 `encrypt: true` | 🔴 | [`data-persistence.md`](data-persistence.md) 规则1 |
| 1.4 | `securityLevel` 与数据敏感度匹配（个人信息 ≥ S3） | 🔴 | 同上 |
| 1.5 | 用户输入有边界校验 | 🟠 | [`security-and-permissions.md`](security-and-permissions.md) 规则4 |
| 1.6 | 错误消息不向 UI 暴露敏感信息 | 🟠 | [`security-and-permissions.md`](security-and-permissions.md) 规则2 |
| 1.7 | 全部使用 `hilog`，禁用 `console` | 🟠 | [`security-and-permissions.md`](security-and-permissions.md) 规则3 |

---

## 2. ArkTS 语言规范

| # | 检查项 | 等级 | 参考 |
|---|--------|------|------|
| 2.1 | 无 `any` / `as any` 类型逃逸 | 🟠 | [`arkts.md`](arkts.md)（Prohibited Features） |
| 2.2 | 同步 API 用 try-catch 包裹 | 🟠 | [`arkts.md`](arkts.md) Error Handling |
| 2.3 | 异步 await 的 API 用 try-catch 包裹 | 🟠 | 同上 |
| 2.4 | Promise 链有 `.catch()` 或 onRejected | 🟠 | 同上 |
| 2.5 | BusinessError 按 code 分支处理 | 🟡 | 同上 |
| 2.6 | catch 块非空（至少记录日志） | 🟠 | 同上 |
| 2.7 | 无 magic numbers（用常量替代） | 🟡 | [`arkts.md`](arkts.md) Best Practices |
| 2.8 | 单函数 ≤ 50 行 | 🟡 | — |
| 2.9 | 单文件 ≤ 800 行 | 🟡 | — |

---

## 3. 组件与生命周期

| # | 检查项 | 等级 | 参考 |
|---|--------|------|------|
| 3.1 | `WebviewController` 在 `aboutToDisappear` 释放 | 🔴 | [`stage-model.md`](stage-model.md) Memory Management |
| 3.2 | `setInterval` 在销毁时 `clearInterval` | 🔴 | 同上 |
| 3.3 | `eventHub.on()` 与 `off()` 配对 | 🔴 | 同上 |
| 3.4 | `emitter.on()` 与 `off()` 配对 | 🔴 | [`state-management.md`](state-management.md)（事件通信） |
| 3.5 | 事件订阅使用稳定引用（绑定函数） | 🟠 | [`stage-model.md`](stage-model.md) |
| 3.6 | 组件嵌套深度 ≤ 4 层 | 🟡 | — |

---

## 4. 状态管理

| # | 检查项 | 等级 | 参考 |
|---|--------|------|------|
| 4.1 | V1/V2 装饰器不混用 | 🟠 | [`state-management.md`](state-management.md) 版本选择指南 |
| 4.2 | `@ComponentV2` 不使用 `@StorageLink` | 🔴 | [`state-management.md`](state-management.md) 陷阱2 |
| 4.3 | `@State` 嵌套对象使用不可变更新（`{...obj}` 或 `[...arr]`） | 🔴 | [`state-management.md`](state-management.md) 陷阱3 |
| 4.4 | UI 响应数据未使用 getter（须用 `@Trace`/`@State` 直接持有） | 🟠 | [`state-management.md`](state-management.md) 陷阱1 |
| 4.5 | 并发状态更新无 race condition | 🟠 | — |

---

## 5. 数据库

| # | 检查项 | 等级 | 参考 |
|---|--------|------|------|
| 5.1 | 全部 `ResultSet` 在 try-finally 中关闭 | 🔴 | [`data-persistence.md`](data-persistence.md) 规则2 |
| 5.2 | 事务失败时 `rollBack()` + 错误向上传播 | 🔴 | [`data-persistence.md`](data-persistence.md) 规则3 |
| 5.3 | `onUpgrade` / `onDowngrade` 已实现 | 🟠 | [`data-persistence.md`](data-persistence.md) 规则4 |

---

## 6. 权限管理

| # | 检查项 | 等级 | 参考 |
|---|--------|------|------|
| 6.1 | 所需权限在 `module.json5` 声明 | 🔴 | [`security-and-permissions.md`](security-and-permissions.md) |
| 6.2 | 用网络则声明 `ohos.permission.INTERNET` | 🔴 | 同上 |
| 6.3 | 请求前用 `checkAccessToken` 检查状态 | 🟠 | 同上 |
| 6.4 | 用户拒绝有降级处理 | 🟠 | 同上 |
| 6.5 | 遵守最小权限原则 | 🟠 | 同上 |

---

## 7. 性能

| # | 检查项 | 等级 | 参考 |
|---|--------|------|------|
| 7.1 | 无 `forEach(async ...)` + `await` 反模式（用 `for...of` 或 `Promise.all`） | 🔴 | [`performance.md`](performance.md) |
| 7.2 | 长列表使用 `LazyForEach` | 🟠 | [`ui-components.md`](ui-components.md) |
| 7.3 | `ForEach` 提供 key 函数 | 🟠 | 同上 |
| 7.4 | 大文件操作使用 async API | 🟠 | [`network.md`](network.md) |
| 7.5 | 条件渲染优先用 `if` 而非 `visibility` | 🟡 | [`performance.md`](performance.md) |
| 7.6 | HTTP 实例调用 `destroy()` 释放 | 🟠 | [`network.md`](network.md) 最佳实践 |
| 7.7 | 文件操作错误向上传播（无静默失败） | 🟠 | [`arkts.md`](arkts.md) Error Handling |

---

## 8. Kit 使用规范

| # | 检查项 | 等级 | 参考 |
|---|--------|------|------|
| 8.1 | Kit 导入按需，无未使用依赖 | 🟡 | — |
| 8.2 | 元服务 API（`__元服务API__`）正确标注 | 🟠 | — |
| 8.3 | 在 ArkTS 卡片中检查卡片能力（`__卡片能力__`） | 🟠 | — |
| 8.4 | Ability Kit 生命周期正确 | 🔴 | [`stage-model.md`](stage-model.md) |
| 8.5 | ArkUI 组件按文档正确使用 | 🟠 | [`ui-components.md`](ui-components.md) |
| 8.6 | Network Kit 使用 async/await 模式 | 🟠 | [`network.md`](network.md) |
| 8.7 | Universal Keystore Kit 安全处理密钥 | 🔴 | [`security-and-permissions.md`](security-and-permissions.md) |

---

## 9. 代码质量

| # | 检查项 | 等级 | 参考 |
|---|--------|------|------|
| 9.1 | 核心逻辑有单元测试 | 🟠 | [`extended.md`](extended.md) Testing |
| 9.2 | 测试覆盖率 ≥ 80% | 🟡 | — |
| 9.3 | 关键流程有 UI 测试 | 🟡 | [`extended.md`](extended.md) Testing |
| 9.4 | 重复逻辑已抽取为共享函数 | 🟡 | — |
| 9.5 | 相关代码按模块组织 | 🟡 | [`templates/project-template.md`](../templates/project-template.md) |

---

## 退出条件

评审视为完成当且仅当：

- [ ] 全部 9 类别已逐条检查
- [ ] 报告已生成至 `docs/YYYY-MM-DD-review.md`
- [ ] 🔴 关键问题清零
- [ ] 🟠 高优先级问题有 `file:line` 引用和具体修复建议
- [ ] 整体评级 ≥ B（A-F 量表）