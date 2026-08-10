# 状态管理参考

> **内容合并自** harmonyos-app 的 V1 装饰器模式 + harmonyos-dev 的 V2 装饰器模式和常见陷阱。
>
> 官方文档：
> - 状态管理概述: https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-state-management-overview
> - V1 装饰器: https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-state-decorators
> - V2 @ObservedV2/@Trace: https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-observedV2-trace
> - 组件生命周期: https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-page-life-cycle

## 版本选择指南

| 场景 | 装饰器版本 | 说明 |
|------|-----------|------|
| 新项目 (API 20+) | **V2 优先** | 更好的性能，细粒度响应 |
| 已有项目 (API 12+) | V1 保持 | 逐步迁移到 V2 |
| 需向后兼容 | V1 | API 12 最低支持 |

---

# 第一部分：V2 装饰器（API 20+，推荐）

来源: [状态变量装饰器](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-state-decorators)

## V2 装饰器速查

| 装饰器 | 作用 | 对比 V1 | 适用场景 |
|--------|------|---------|----------|
| `@ObservedV2` | 标记类为可观察 | `@Observed` | 需要深度响应式的类 |
| `@Trace` | 标记字段为可追踪 | —（V2 新增） | 精细控制哪些字段触发更新 |
| `@Local` | 组件内部状态 | `@State` | 组件私有数据 |
| `@Param` | 从父组件传入 | `@Prop` | 父到子单向传递 |
| `@Provider` | 向子组件提供状态 | `@Provide` | 跨层级状态共享 |
| `@Consumer` | 从祖先消费状态 | `@Consume` | 跨层级状态消费 |
| `@ComponentV2` | V2 组件声明 | `@Component` | V2 风格组件 |

## 基本用法

来源: [@ObservedV2/@Trace](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-observedV2-trace)

```typescript
@ObservedV2
export class User {
  @Trace name: string = '';
  @Trace age: number = 0;
  avatar: string = '';  // 未标记 @Trace，修改不触发更新
}

@ComponentV2
struct UserProfile {
  @Local user: User = new User();

  build() {
    Column() {
      Text(this.user.name)  // name 变化会触发重渲染
      Text(this.user.age)   // age 变化会触发重渲染
      // avatar 变化不触发重渲染（未标记 @Trace）
    }
  }
}
```

## 组件内状态与传递

来源: [状态管理概述](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-state-management-overview)

### @Local — 组件内部使用

```typescript
@ComponentV2
struct Counter {
  @Local count: number = 0;

  build() {
    Button(`Count: ${this.count}`)
      .onClick(() => { this.count++; })
  }
}
```

### @Param — 从父组件传入（单向）

```typescript
// 父组件
@ComponentV2
struct Parent {
  @Local message: string = 'Hello';
  build() { Child({ msg: this.message }) }
}

// 子组件
@ComponentV2
struct Child {
  @Param msg: string = '';
  build() { Text(this.msg) }
}
```

### @Provider + @Consumer — 跨层级共享

来源: [状态同步](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-state-synchronization)

```typescript
// 祖先组件
@ComponentV2
struct Ancestor {
  @Provider theme: string = 'light';

  build() {
    Column() {
      // 所有后代都可以通过 @Consumer 访问 theme
      MiddleComponent()
    }
  }
}

// 深层的后代组件
@ComponentV2
struct DeepChild {
  @Consumer theme: string = 'light';

  build() {
    Text(`Current theme: ${this.theme}`)
  }
}
```

## 事件通信（非响应式）

来源: [Emitter使用指南](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-common-emitter)

```typescript
import { emitter } from '@kit.BasicServicesKit';

// 发送事件
emitter.emit('eventName', { data: {} });

// 订阅事件
emitter.on('eventName', (data: emitter.EventData) => {
  // 处理事件
});
```

---

# 第二部分：V1 装饰器（API 12+）

来源: [V1 状态装饰器](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-state-decorators)

## V1 装饰器速查

| 装饰器 | 机制 | 适用场景 |
|--------|------|----------|
| `@State` | 组件拥有状态，触发重渲染 | 计数器、表单输入 |
| `@Prop` | 父传子，子接收副本（单向） | 只读子组件数据 |
| `@Link` | 父传引用，子可修改（双向） | 共享可变状态 |
| `@Provide` | 祖先向所有后代提供值 | 主题、用户上下文 |
| `@Consume` | 后代从祖先消费值 | 主题、用户上下文 |
| `@StorageLink` | 与 AppStorage 双向绑定 | 全局持久化状态 |
| `@StorageProp` | 与 AppStorage 单向绑定 | 只读全局状态 |
| `@Observed` | 类装饰器，标记为可观察 | 嵌套对象更新 |
| `@ObjectLink` | 链接到父组件的 @Observed 对象 | 复杂嵌套状态 |

## 核心模式

### @State + @Prop + @Link 示例

```typescript
@Component
struct Parent {
  @State selectedId: string = '';

  build() {
    Column() {
      Child({ id: this.selectedId })              // 单向：传递给子
      ChildTwo({ selectedId: $selectedId })        // 双向：$ 语法建立引用
    }
  }
}

@Component
struct Child {
  @Prop id: string = '';
  build() { Text(`Selected: ${this.id}`) }
}

@Component
struct ChildTwo {
  @Link selectedId: string;
  build() {
    Button('Select B')
      .onClick(() => { this.selectedId = 'B'; })  // 修改会回传到父
  }
}
```

### ViewModel 模式（V1）

```typescript
@Observed
export class ProductViewModel {
  products: Product[] = [];
  isLoading: boolean = false;
  errorMessage: string = '';

  private repository: ProductRepository = new ProductRepository();

  async loadProducts(): Promise<void> {
    this.isLoading = true;
    this.errorMessage = '';
    try {
      this.products = await this.repository.getProducts();
    } catch (error) {
      this.errorMessage = `Failed to load: ${(error as Error).message}`;
    } finally {
      this.isLoading = false;
    }
  }

  async addProduct(product: Product): Promise<void> {
    const created = await this.repository.createProduct(product);
    this.products = [...this.products, created];  // 不可变更新
  }
}

// 使用
@Entry
@Component
struct ProductPage {
  @State viewModel: ProductViewModel = new ProductViewModel();

  aboutToAppear(): void { this.viewModel.loadProducts(); }

  build() {
    Column() {
      if (this.viewModel.isLoading) {
        LoadingProgress()
      } else if (this.viewModel.errorMessage) {
        Text(this.viewModel.errorMessage).fontColor(Color.Red)
      } else {
        ForEach(this.viewModel.products, (product: Product) => {
          ProductCard({ product: product })
        }, (product: Product) => product.id)
      }
    }
  }
}
```

## 全局状态

### AppStorage — 应用级状态

```typescript
// 在 EntryAbility 中初始化
export default class EntryAbility extends UIAbility {
  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
    AppStorage.setOrCreate('isLoggedIn', false);
    AppStorage.setOrCreate('currentUser', null);
    AppStorage.setOrCreate('theme', 'light');
  }
}

// 组件中访问
@Entry
@Component
struct ProfilePage {
  @StorageLink('isLoggedIn') isLoggedIn: boolean = false;
  @StorageLink('currentUser') currentUser: User | null = null;
  @StorageProp('theme') theme: string = 'light';  // 只读

  build() {
    Column() {
      if (this.isLoggedIn && this.currentUser) {
        Text(`Welcome, ${this.currentUser.name}`)
      } else {
        Button('Login').onClick(() => {
          this.isLoggedIn = true;
          this.currentUser = { id: '1', name: 'John' };
        })
      }
    }
  }
}
```

### PersistentStorage — 持久化存储

```typescript
// 初始化持久化
PersistentStorage.persistProp('userSettings', {
  notifications: true,
  darkMode: false,
  language: 'zh-CN'
});

@Entry
@Component
struct SettingsPage {
  @StorageLink('userSettings') settings: UserSettings = {
    notifications: true, darkMode: false, language: 'zh-CN'
  };

  build() {
    Column() {
      Toggle({ type: ToggleType.Switch, isOn: this.settings.notifications })
        .onChange((isOn: boolean) => {
          this.settings = { ...this.settings, notifications: isOn };  // 不可变更新
        })
    }
  }
}
```

---

# 第三部分：常见陷阱与调试

## 陷阱1: Getter 不是响应式的

**问题**: UI 不会因 getter 返回值变化而重新渲染。

```typescript
// ❌ 错误：getter 返回值变化不会触发 UI 更新
get isLargeScreen(): boolean {
  return AppStorage.get('currentBreakpoint') === 'lg';
}

// ✅ 正确：使用 @Trace 装饰属性，通过方法主动更新
@Trace isLargeScreen: boolean = false;

updateLargeScreen(breakpoint: string): void {
  this.isLargeScreen = breakpoint === BreakpointTypeEnum.LG;
}
```

**原因**: ArkUI 响应式系统基于属性变化检测，而非计算属性依赖追踪。

## 陷阱2: @ComponentV2 不支持 @StorageLink

**问题**: `@StorageLink` 只能用于 `@Component`，不能用于 `@ComponentV2`。

```typescript
// ❌ 编译错误
@ComponentV2
struct MyView {
  @StorageLink('key') value: string = '';  // 报错！
}

// ✅ 替代方案：手动获取
@ComponentV2
struct MyView {
  @Local value: string = '';

  aboutToAppear() {
    this.value = AppStorage.get<string>('key') ?? '';
  }
}
```

## 陷阱3: V1 直接状态修改不触发更新

```typescript
// ❌ 禁止：直接修改
@State user: User = { name: 'John', age: 25 };
this.user.age = 26;  // UI 不更新！

// ✅ 必须：不可变更新
this.user = { ...this.user, age: 26 };

// ❌ 禁止：数组直接操作
@State items: string[] = ['a', 'b'];
this.items.push('c');  // UI 不更新！

// ✅ 必须
this.items = [...this.items, 'c'];
```

## 调试检查清单

当发现"数据变了但 UI 没变"时，按顺序检查：

| 检查项 | V1 | V2 |
|--------|----|----|
| 装饰器 | 属性有 `@State`/`@Prop`/`@Link`？ | 属性有 `@Trace`/`@Local`？类有 `@ObservedV2`？ |
| 更新方式 | 是直接赋值还是 getter 计算？ | 是直接赋值还是 getter 计算？ |
| 引用变更 | 嵌套对象是否创建了新引用？ | @Trace 字段是否直接赋值？ |
| 生命周期 | 监听器是否已注册？ | 监听器是否已注册？ |
| 初始化 | 是否在正确时机获取初始值？ | 是否在正确时机获取初始值？ |

## 架构分层建议

将"监听变化"与"响应变化"分离，通过 AppStorage 作为中间层解耦：

```
监听层 (MediaQuery / BreakpointSystem)
      ↓ AppStorage.setOrCreate()
状态层 (ViewModel) ← updateXxx() 方法
      ↓ @Trace / @State 属性
UI层 (View) ← onAreaChange() 等事件触发检查
```

---

## 性能优化

来源: [状态管理最佳实践](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-state-management-best-practices)

- **V2**: 使用 `@Trace` 精确追踪变化字段，未标记的字段修改不触发渲染
- **V1**: 使用 `@Observed`/`@ObjectLink` 精确控制嵌套对象更新
- 避免深层嵌套对象，非必要时扁平化数据结构
- 按需更新：仅标记必要的响应式字段

## 生命周期

来源: [组件生命周期](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-page-life-cycle)

- `aboutToAppear()` — 组件即将出现，在此初始化状态和注册监听
- `aboutToDisappear()` — 组件即将销毁，在此释放资源和取消订阅