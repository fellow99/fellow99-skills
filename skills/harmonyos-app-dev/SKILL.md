---
name: harmonyos-app-dev
description: End-to-end HarmonyOS application development skill — covers the full lifecycle from greenfield setup through implementation to pre-release code review. Use when building, iterating, debugging, or **auditing** HarmonyOS apps with ArkTS, ArkUI, and Stage model. Includes ready-to-run security/quality scan commands and a graded code-review checklist that catches hardcoded credentials, unencrypted databases, ResultSet leaks, `async forEach`, `console` vs `hilog`, V1/V2 decorator mixing, and other production-blocking issues. Covers API 12+ (V1 decorators) and API 20+ (V2 decorators). Triggers on mentions of HarmonyOS, ArkTS, ArkUI, Stage model, UIAbility, .ets files, HarmonyOS project setup, **code review**, **security audit**, **quality gate**, or any HarmonyOS development or review task.
---

# HarmonyOS Application Development

## Core Principles

- **ArkTS First** — Use ArkTS with strict type safety, no `any` or dynamic types
- **Declarative UI** — Build UI with ArkUI's declarative components and state management
- **Stage Model** — Use modern Stage model (UIAbility), not legacy FA model
- **Distributed by Design** — Leverage cross-device capabilities from the start
- **One-time Development** — Design for multi-device adaptation (phone, tablet, 2in1, car)
- **Documentation-Driven** — Every API usage, pattern, and claim must be traceable to official Huawei docs
- **Source Attribution** — Cite documentation sources; never fabricate APIs or behavior

---

## Pre-Development Checklist

Before starting any project or feature, confirm:

- **API version**: Default API 20+; state explicitly if backward compatibility needed (API 12 minimum for Stage Model)
- **Target device**: PC / Phone / Tablet / Wearable / Multi-device
- **Scenario**: Greenfield / Iteration / Architecture design
- **Project structure**: HAP package layout, module organization
- **State decorator version**: V1 (`@State`, `@Prop`, `@Link`) for API 12+; V2 (`@Local`, `@Provider`, `@Consumer`, `@ObservedV2`, `@Trace`) for API 20+

---

## Source Attribution (MANDATORY)

**You MUST NOT fabricate or hallucinate any information.** Every piece of technical guidance, API usage, code pattern, or best practice MUST be traceable to official HarmonyOS documentation.

### Mandatory Rules

1. **Always cite sources**: Include the official documentation URL or reference path
2. **No guessing**: If information cannot be found in official docs, explicitly state "未在官方文档中找到相关说明" and suggest manual search
3. **Verify before claiming**: Never claim an API exists without verification from official sources
4. **Distinguish facts from suggestions**: Clearly mark:
   - 官方文档规定 (official docs requirement)
   - 推荐实践 (recommended practice)
   - 常见模式 (common pattern)

### Citation Format

```
来源: [文档标题](URL)
> 引用原文（如适用）
```

### When Documentation is Unavailable

If information is not found in official docs:
1. State clearly: "⚠️ 未在官方文档中找到关于 [topic] 的明确说明"
2. Suggest checking: official docs, DevEco Studio hints, or community resources
3. Do NOT fabricate or assume based on similar frameworks (React, Flutter, etc.)

---

## Hard Rules

### No Dynamic Types

ArkTS prohibits dynamic typing. Never use `any`, type assertions, or dynamic property access.

```typescript
// ❌ FORBIDDEN
let data: any = fetchData();
let obj: object = {};
obj['dynamicKey'] = value;
(someVar as SomeType).method();

// ✅ REQUIRED
interface UserData {
  id: string;
  name: string;
}
let data: UserData = fetchData();

// Use Record for dynamic keys
let obj: Record<string, string> = {};
obj['key'] = value;  // OK with Record type
```

### No Direct State Mutation

Never mutate `@State`/`@Prop`/`@Local` variables directly in nested objects. Use immutable updates.

```typescript
// ❌ FORBIDDEN: Direct mutation
@State user: User = { name: 'John', age: 25 };
this.user.age = 26;  // UI won't update!

// ✅ REQUIRED: Immutable update
this.user = { ...this.user, age: 26 };

// For arrays
// ❌ FORBIDDEN
this.items.push('c');  // UI won't update

// ✅ REQUIRED
this.items = [...this.items, 'c'];
```

### Stage Model Only

Always use Stage model (UIAbility). Never use deprecated FA model (PageAbility).

```typescript
// ❌ FORBIDDEN: FA Model (deprecated)
// config.json with "pages" array
export default { onCreate() { ... } }

// ✅ REQUIRED: Stage Model
import { UIAbility } from '@kit.AbilityKit';

export default class EntryAbility extends UIAbility {
  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { }

  onWindowStageCreate(windowStage: window.WindowStage): void {
    windowStage.loadContent('pages/Index');
  }
}
```

### Component Reusability

Extract reusable UI into `@Component`. No inline complex UI in `build()` methods.

```typescript
// ❌ FORBIDDEN: Monolithic build method (200+ lines inline)
// ✅ REQUIRED: Extract components
@Component
struct UserCard {
  @Prop user: User;
  build() {
    Row() {
      Image($r('app.media.avatar'))
      Column() { Text(this.user.name); Text(this.user.email) }
    }
  }
}

@Entry
@Component
struct MainPage {
  @State user: User = { name: 'John', email: 'john@example.com' };
  build() { Column() { UserCard({ user: this.user }) } }
}
```

---

## State Management

### V1 Decorators (API 12+)

| Decorator | Mechanism | Use Case |
|-----------|-----------|----------|
| `@State` | Component owns state, triggers re-render | Counter, form inputs |
| `@Prop` | Parent passes value, child gets copy (one-way) | Read-only child data |
| `@Link` | Parent passes reference, child can modify (two-way) | Shared mutable state |
| `@Provide` | Ancestor provides value to all descendants | Theme, user context |
| `@Consume` | Descendant consumes value from ancestor | Theme, user context |
| `@StorageLink` | Syncs with AppStorage, two-way | Global persistent state |
| `@StorageProp` | Syncs with AppStorage, one-way | Read-only global state |
| `@Observed` | Class decorator for observable objects | Nested object updates |
| `@ObjectLink` | Links to @Observed object in parent | Complex nested state |

### V2 Decorators (API 20+, recommended for new projects)

| Decorator | Mechanism | Use Case |
|-----------|-----------|----------|
| `@Local` | Component-local state, triggers re-render | Same as `@State` |
| `@Param` | Parent-to-child data flow | Same as `@Prop` |
| `@Provider` | Provide state to descendants | Cross-component state |
| `@Consumer` | Consume state from ancestor | Cross-component state |
| `@ObservedV2` | Mark class as deeply observable | Complex nested objects |
| `@Trace` | Mark individual fields for tracking | Fine-grained reactivity |

### Selection Decision

- **New projects (API 20+)**: Use V2 decorators — better performance with fine-grained reactivity
- **Existing projects (API 12+)**: Continue with V1, migrate to V2 incrementally
- **Backward compatibility required**: Use V1 decorators

---

## Project Structure

### Recommended Architecture

```
MyApp/
├── entry/                          # Main entry module
│   ├── src/main/
│   │   ├── ets/
│   │   │   ├── entryability/       # UIAbility definitions
│   │   │   │   └── EntryAbility.ets
│   │   │   ├── pages/              # Page components
│   │   │   │   ├── Index.ets
│   │   │   │   └── Detail.ets
│   │   │   ├── components/         # Reusable UI components
│   │   │   │   ├── common/         # Common components
│   │   │   │   └── business/       # Business-specific components
│   │   │   ├── viewmodel/          # ViewModels (MVVM)
│   │   │   ├── model/              # Data models
│   │   │   ├── service/            # Business logic services
│   │   │   ├── repository/         # Data access layer
│   │   │   ├── utils/              # Utility functions
│   │   │   └── constants/          # Constants and configs
│   │   ├── resources/              # Resources (strings, images)
│   │   └── module.json5            # Module configuration
│   └── build-profile.json5
├── common/                         # Shared library module
├── features/                       # Feature modules
│   ├── feature_home/
│   └── feature_profile/
└── build-profile.json5             # Project configuration
```

### Layer Separation

```
┌─────────────────────────────────────┐
│           UI Layer (Pages)          │  ArkUI Components
├─────────────────────────────────────┤
│         ViewModel Layer             │  State management, UI logic
├─────────────────────────────────────┤
│         Service Layer               │  Business logic
├─────────────────────────────────────┤
│        Repository Layer             │  Data access abstraction
├─────────────────────────────────────┤
│    Data Sources (Local/Remote)      │  Preferences, RDB, Network
└─────────────────────────────────────┘
```

---

## Core Technology Stack

### ArkTS Language

- TypeScript-based extension with strict typing
- State decorators: `@State`/`@Prop`/`@Link` (V1) or `@ObservedV2`/`@Trace`/`@Local`/`@Param`/`@Provider`/`@Consumer` (V2)
- Component decorators: `@Component`, `@Entry`, `@Builder`
- Rendering: on-demand updates, minimal re-renders

### ArkUI Component System

- Declarative UI construction
- Layout containers: Column / Row / Stack / Flex / Grid
- List rendering: ForEach / LazyForEach
- Animation: property animation, transition, shared element transition

---

## ArkUI Component Patterns

### Basic Component Structure

```typescript
import { router } from '@kit.ArkUI';

@Component
export struct ProductCard {
  @Prop product: Product;
  @Prop onAddToCart: (product: Product) => void;
  @State isExpanded: boolean = false;

  get formattedPrice(): string {
    return `¥${this.product.price.toFixed(2)}`;
  }

  aboutToAppear(): void {
    console.info('ProductCard appearing');
  }

  aboutToDisappear(): void {
    console.info('ProductCard disappearing');
  }

  private handleTap(): void {
    router.pushUrl({ url: 'pages/ProductDetail', params: { id: this.product.id } });
  }

  private handleAddToCart(): void {
    this.onAddToCart(this.product);
  }

  build() {
    Column() {
      Image(this.product.imageUrl)
        .width('100%')
        .aspectRatio(1)
        .objectFit(ImageFit.Cover)

      Text(this.product.name)
        .fontSize(16)
        .fontWeight(FontWeight.Medium)

      Text(this.formattedPrice)
        .fontSize(14)
        .fontColor('#FF6B00')

      Button('Add to Cart')
        .onClick(() => this.handleAddToCart())
    }
    .padding(12)
    .backgroundColor(Color.White)
    .borderRadius(8)
    .onClick(() => this.handleTap())
  }
}
```

### List with LazyForEach

```typescript
import { BasicDataSource } from '../utils/BasicDataSource';

class ProductDataSource extends BasicDataSource<Product> {
  private products: Product[] = [];

  totalCount(): number { return this.products.length; }
  getData(index: number): Product { return this.products[index]; }

  addData(product: Product): void {
    this.products.push(product);
    this.notifyDataAdd(this.products.length - 1);
  }

  updateData(index: number, product: Product): void {
    this.products[index] = product;
    this.notifyDataChange(index);
  }
}

@Component
struct ProductList {
  private dataSource: ProductDataSource = new ProductDataSource();

  build() {
    List() {
      LazyForEach(this.dataSource, (product: Product, index: number) => {
        ListItem() { ProductCard({ product: product }) }
      }, (product: Product) => product.id)  // Key generator
    }
    .lanes(2)
    .cachedCount(4)
  }
}
```

### Custom Dialog

```typescript
@CustomDialog
struct ConfirmDialog {
  controller: CustomDialogController;
  title: string = 'Confirm';
  message: string = '';
  onConfirm: () => void = () => {};

  build() {
    Column() {
      Text(this.title).fontSize(20).fontWeight(FontWeight.Bold).margin({ bottom: 16 })
      Text(this.message).fontSize(16).margin({ bottom: 24 })
      Row() {
        Button('Cancel').onClick(() => this.controller.close())
          .backgroundColor(Color.Gray).margin({ right: 16 })
        Button('Confirm').onClick(() => { this.onConfirm(); this.controller.close(); })
      }
    }.padding(24)
  }
}

// Usage
@Entry
@Component
struct MainPage {
  dialogController: CustomDialogController = new CustomDialogController({
    builder: ConfirmDialog({
      title: 'Delete Item',
      message: 'Are you sure?',
      onConfirm: () => this.deleteItem()
    }),
    autoCancel: true
  });

  private deleteItem(): void { /* ... */ }

  build() {
    Button('Delete').onClick(() => this.dialogController.open())
  }
}
```

---

## Common Patterns

### Page Navigation

```typescript
import { router } from '@kit.ArkUI';

// Push new page
router.pushUrl({ url: 'pages/Detail', params: { id: '123' } });

// Replace current page (no back stack)
router.replaceUrl({ url: 'pages/Login' });

// Go back
router.back();

// Receive params on target page
const params = router.getParams() as Record<string, string>;
```

### Data Persistence

- **Preferences**: Lightweight key-value storage for user preferences
- **RDB**: Relational database for structured data (SQLite-based)
- **Distributed Data**: Cross-device sync via distributed data services

### Network

```typescript
import { http } from '@kit.NetworkKit';

// HTTP request
const request = http.createHttp();
request.request('https://api.example.com/data', {
  method: http.RequestMethod.GET,
  header: { 'Content-Type': 'application/json' }
}).then((response) => {
  const data = JSON.parse(response.result as string);
});
```

- WebSocket for persistent connections
- Upload/Download via `@kit.BasicServicesKit` request module

---

## Official Documentation

### Primary Documentation Source (MANDATORY)

**Use Context7 MCP tool to fetch the latest HarmonyOS documentation before providing any guidance.**

```
# Example workflow:
1. Use mcp__context7__resolve-library-id with query "harmonyos arkts"
2. Use mcp__context7__query-docs to fetch relevant documentation
3. Cite the documentation source in your response
```

### Official Documentation Links

- **Release notes**: https://developer.huawei.com/consumer/cn/doc/harmonyos-releases/overview-allversion
- **Dev guide**: https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/application-dev-guide
- **API reference**: https://developer.huawei.com/consumer/cn/doc/harmonyos-references/development-intro-api
- **Best practices**: https://developer.huawei.com/consumer/cn/doc/best-practices/bpta-best-practices-overview
- **FAQ**: https://developer.huawei.com/consumer/cn/doc/harmonyos-faqs/faqs-multi-device-scenario

### Documentation Query Protocol

When answering HarmonyOS development questions:

1. **First**: Query Context7 for relevant documentation
2. **Then**: If Context7 doesn't have the answer, search official docs at the links above
3. **Finally**: If no official documentation found, explicitly state:
   > ⚠️ 未在官方文档中找到关于 [topic] 的明确说明，建议查阅：
   > - [Dev guide](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/application-dev-guide)
   > - [API reference](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/development-intro-api)
   > - DevEco Studio 内置提示

4. **Never fabricate** API signatures, method names, or behavior patterns

---

## Development Lifecycle (Closed Loop)

This skill supports the full HarmonyOS development workflow as a closed loop. Pick your entry point based on the task:

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  1. Plan     │  →   │  2. Build    │  →   │  3. Review   │  →   │  4. Ship     │
│              │      │              │      │  (Quality    │      │              │
│  Pre-dev     │      │  Reference   │      │   Gate)      │      │  Address     │
│  checklist + │      │  patterns +  │      │  Run review  │      │  🔴/🟠 fixes │
│  templates   │      │  examples    │      │  checklist   │      │  → re-review │
└──────────────┘      └──────────────┘      └──────┬───────┘      └──────────────┘
                                                    │
                                                    │ if any 🔴 found
                                                    └─────→ back to Build
```

| Phase | Action | Resources |
|-------|--------|-----------|
| **1. Plan** | Confirm API version, target device, project structure | Pre-Development Checklist (above) + [`templates/project-template.md`](templates/project-template.md) |
| **2. Build** | Implement features following references; consult Context7 / official docs | All topic references (see Bundled Resources below) |
| **3. Review** | Run security/quality scan → checklist audit → graded report | [`references/code-review.md`](references/code-review.md) + [`references/review-report-template.md`](references/review-report-template.md) |
| **4. Ship** | Fix all 🔴 critical issues; document 🟠 high-priority handling | Loop back to step 2 until exit criteria met |

### When to Trigger Code Review

Trigger the review phase whenever any of these is true:
- User explicitly asks: "review my code", "audit", "quality check", "代码评审", "代码审查"
- Pre-release / pre-merge milestone reached
- Significant feature implementation completed (>500 LOC changed)
- Refactor or migration finished (e.g., V1→V2 decorator migration)
- Investigating production incident root cause

### Quality Gate (Pre-Release Exit Criteria)

Code is not ready to ship until:
- [ ] [`references/code-review.md`](references/code-review.md) checklist run end-to-end
- [ ] Report generated at `docs/YYYY-MM-DD-review.md` using [`references/review-report-template.md`](references/review-report-template.md)
- [ ] All 🔴 critical issues fixed and verified
- [ ] All 🟠 high-priority issues have `file:line` references and concrete fix plans
- [ ] Overall grade ≥ B (A-F scale)

---

## Bundled Resources

Load these reference documents as needed for detailed guidance on specific topics. Each file has been **deduplicated and merged** from the original harmonyos-app, harmonyos-dev, and harmonyos-review skills — there is exactly one authoritative file per topic.

### Topic-Based References

| File | Scope | Load when |
|------|-------|-----------|
| [`references/arkts.md`](references/arkts.md) | ArkTS language: prohibited features, type system, classes, generics, async, modules, **error handling production rules** (sync/async/Promise/BusinessError patterns) | Working with type definitions, language semantics, debugging errors |
| [`references/state-management.md`](references/state-management.md) | **V1 + V2 decorators** unified guide: lookup tables, ViewModel pattern, AppStorage/PersistentStorage, common pitfalls and debugging checklist | Designing state flow, choosing decorators, debugging "data changed but UI didn't" issues |
| [`references/ui-components.md`](references/ui-components.md) | ArkUI components: basics, layouts, lists (ForEach/LazyForEach), custom components, `@Builder`/`@BuilderParam`/`@Styles`/`@Extend`, animations, gestures, dialogs (CustomDialog + AlertDialog), responsive layout | Building any UI |
| [`references/stage-model.md`](references/stage-model.md) | Stage model: AbilityStage, UIAbility lifecycle, launch types, Navigation component, Context capabilities, Extension Abilities | Setting up new abilities, configuring lifecycle, routing |
| [`references/data-persistence.md`](references/data-persistence.md) | Storage: Preferences, RDB (CRUD + **ResultSet close enforcement** + **transaction rollback** + **database encryption rules**), distributed data, file storage | Persisting data — plus security audit of database code |
| [`references/network.md`](references/network.md) | Network: HTTP basics + production-ready HttpClient class, WebSocket, TCP/UDP sockets, upload/download, network status | Any networking work |
| [`references/distributed.md`](references/distributed.md) | Distributed capabilities: device discovery, KV Store, distributed objects, cross-device call, ability continuation, file sharing | Multi-device collaboration features |
| [`references/security-and-permissions.md`](references/security-and-permissions.md) | **Security + Permissions** combined: hardcoded credentials prevention, input validation, `hilog` vs `console` enforcement, error leakage rules, permission declaration, runtime request, permission checking | Security audit, permission handling, production hardening |
| [`references/performance.md`](references/performance.md) | Performance: render optimization, memory management, network caching, startup optimization, animation, Profiler usage | Performance debugging or optimization tasks |
| [`references/extended.md`](references/extended.md) | Testing (unit + UI), comprehensive dev checklist, theme index of all references | Reviewing your work before completion |

### Review & Quality Gate

| File | Scope | Load when |
|------|-------|-----------|
| [`references/code-review.md`](references/code-review.md) | **Code review checklist**: 10 categories × ~50 check items with priority levels (🔴🟠🟡), quick-scan bash commands, exit criteria. Each item cross-references the correct-practice dev reference | Pre-release audit, security scan, quality gate, code review request |
| [`references/review-report-template.md`](references/review-report-template.md) | **Graded report template**: summary table, per-category findings with `file:line` + code snippets + fix suggestions, priority-sorted recommendations, A-F grade table, checklist appendix | Generating structured review reports |

### Templates

- [`templates/project-template.md`](templates/project-template.md) — Complete project scaffolding: directory structure, `app.json5`/`module.json5`/`main_pages.json` configs, AbilityStage/MainAbility/Index entry files, Model/ViewModel/Service/HttpClient skeletons, resource files

### Cross-Reference Map

When working on a feature, you typically need multiple references in combination:

- **New feature with data fetching** → `state-management.md` + `network.md` + `security-and-permissions.md`
- **List page with persistence** → `ui-components.md` + `state-management.md` + `data-persistence.md`
- **Cross-device feature** → `distributed.md` + `state-management.md` + `security-and-permissions.md`
- **Greenfield project setup** → `templates/project-template.md` + `stage-model.md` + `arkts.md`
- **Performance tuning** → `performance.md` + relevant feature reference
- **Pre-release audit** → `code-review.md` + `review-report-template.md` + affected feature references