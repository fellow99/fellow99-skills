# harmonyos-app-dev Extended Reference

本文档保留特定主题的详细内容，这些内容已从 `SKILL.md` 移出以实现渐进式披露。仅当当前任务需要具体示例时加载。

> 原有的 State Management、Navigation、Network、Distributed 等章节已提取到独立的专题 reference 文件中。见下方索引。

---

## Testing

### Unit Testing

```typescript
import { describe, it, expect, beforeEach } from '@ohos/hypium';
import { ProductViewModel } from '../viewmodel/ProductViewModel';

export default function ProductViewModelTest() {
  describe('ProductViewModel', () => {
    let viewModel: ProductViewModel;

    beforeEach(() => {
      viewModel = new ProductViewModel();
    });

    it('should load products successfully', async () => {
      await viewModel.loadProducts();

      expect(viewModel.products.length).assertLarger(0);
      expect(viewModel.isLoading).assertFalse();
      expect(viewModel.errorMessage).assertEqual('');
    });

    it('should add product to list', async () => {
      const initialCount = viewModel.products.length;
      const newProduct: Product = { id: 'test', name: 'Test Product', price: 99 };

      await viewModel.addProduct(newProduct);

      expect(viewModel.products.length).assertEqual(initialCount + 1);
    });
  });
}
```

### UI Testing

```typescript
import { describe, it, expect } from '@ohos/hypium';
import { Driver, ON } from '@ohos.UiTest';

export default function ProductPageUITest() {
  describe('ProductPage UI', () => {
    it('should display product list', async () => {
      const driver = Driver.create();
      await driver.delayMs(1000);

      const list = await driver.findComponent(ON.type('List'));
      expect(list).not().assertNull();

      const items = await driver.findComponents(ON.type('ListItem'));
      expect(items.length).assertLarger(0);
    });

    it('should navigate to detail on tap', async () => {
      const driver = Driver.create();

      const card = await driver.findComponent(ON.type('ProductCard'));
      await card.click();

      await driver.delayMs(500);

      const detailTitle = await driver.findComponent(ON.text('Product Detail'));
      expect(detailTitle).not().assertNull();
    });
  });
}
```

---

## Checklist

```markdown
## Project Setup
- [ ] Stage model used (not FA model)
- [ ] module.json5 properly configured
- [ ] Permissions declared in module.json5
- [ ] Resource files organized (strings, images)

## Code Quality
- [ ] No `any` types in codebase
- [ ] All state decorated with proper decorators
- [ ] No direct mutation of @State objects
- [ ] Components extracted for reusability
- [ ] Lifecycle methods used appropriately

## UI/UX
- [ ] LazyForEach used for long lists
- [ ] Loading states implemented
- [ ] Error handling with user feedback
- [ ] Multi-device layouts with GridRow/GridCol
- [ ] Accessibility attributes added

## State Management
- [ ] Clear state ownership (component vs global)
- [ ] V2: @ObservedV2/@Trace for deep reactivity
- [ ] V1: @Observed/@ObjectLink for nested objects
- [ ] V2: @Provider/@Consumer for cross-component
- [ ] PersistentStorage for user preferences
- [ ] AppStorage for app-wide state

## Performance
- [ ] Images optimized and cached
- [ ] Unnecessary re-renders avoided
- [ ] Network requests with proper error handling
- [ ] Background tasks properly managed

## Testing
- [ ] Unit tests for ViewModels
- [ ] UI tests for critical flows
- [ ] Edge cases covered
```

---

## Theme Index — 所有专题 Reference 文件

| 文件 | 内容 | 来源 |
|------|------|------|
| [`arkts.md`](arkts.md) | ArkTS 语言：禁止的特性、类型系统、类、泛型、异步、模块、**错误处理生产规范**（同步/异步/Promise/BusinessError） | harmonyos-app + harmonyos-review |
| [`state-management.md`](state-management.md) | V1 + V2 装饰器完整指南：速查表、ViewModel 模式、全局状态、常见陷阱 | 合并 |
| [`ui-components.md`](ui-components.md) | ArkUI 组件：基础/布局/列表/自定义组件/@Builder/动画/手势/对话框/响应式 | 合并 |
| [`stage-model.md`](stage-model.md) | Stage 模型：AbilityStage、UIAbility 生命周期、启动类型、Navigation、Context | harmonyos-app |
| [`data-persistence.md`](data-persistence.md) | 数据持久化：Preferences、RDB（含 **ResultSet 关闭强制**、**事务回滚**、**数据库加密**）、分布式数据、文件存储 | 合并 + harmonyos-review |
| [`network.md`](network.md) | 网络通信：HTTP/HttpClient/WebSocket/TCP/UDP/上传下载/网络状态 | 合并 |
| [`distributed.md`](distributed.md) | 分布式能力：KV Store、分布式对象、设备发现、跨设备调用、任务接续 | harmonyos-app |
| [`security-and-permissions.md`](security-and-permissions.md) | **安全开发规范**（硬编码凭据、输入校验、hilog vs console、错误泄漏） + 权限管理（system_grant/user_grant、运行时请求、检查） | harmonyos-dev + harmonyos-review |
| [`performance.md`](performance.md) | 性能优化：渲染、内存、网络缓存、启动、动画、Profiler | harmonyos-dev |
| [`extended.md`](extended.md) | （本文件）Testing、Checklist、索引 | 合并裁剪 |
| [`code-review.md`](code-review.md) | **代码评审清单**：10 大类约 50 项检查、自动化扫描命令、优先级标记、退出标准 | harmonyos-review |
| [`review-report-template.md`](review-report-template.md) | 评审报告模板：摘要表、问题详情、修复建议、A-F 评级 | harmonyos-review |
| [`../templates/project-template.md`](../templates/project-template.md) | 完整项目模板：目录结构、配置文件、核心文件骨架 | harmonyos-app |