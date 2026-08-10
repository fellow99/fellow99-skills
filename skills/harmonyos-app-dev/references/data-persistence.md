# 数据持久化参考

> **内容合并自** harmonyos-dev 的 data-persistence.md（Preferences + RDB + 文件存储）+ harmonyos-app stage-model.md 的 Preferences 类封装。
>
> 官方文档：
> - 数据管理指南: https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/data-management
> - Preferences: https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-preferences
> - 关系型数据库: https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-relational-store
> - 分布式数据: https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-distributed-data-object
> - 文件管理: https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-file-management

## 存储方案选择

| 方案 | 适用场景 | 数据量 | 跨设备 |
|------|---------|--------|--------|
| Preferences | 用户设置、偏好 | 小 | 否 |
| RDB | 结构化业务数据 | 中-大 | 否 |
| 分布式 KV | 多设备共享状态 | 小-中 | 是 |
| 分布式对象 | 实时协同数据 | 小-中 | 是 |
| 文件存储 | 文档、媒体 | 大 | 部分 |
| AppStorage | 应用级运行时状态 | 小 | 否 |
| PersistentStorage | 持久化的应用状态 | 小 | 否 |

---

## Preferences（轻量级键值存储）

来源: [Preferences用户首选项](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-preferences)

### 基础用法

```typescript
import { preferences } from '@kit.ArkData';

// 获取 Preferences 实例
let dataPreferences = await preferences.getPreferences(getContext(), 'mystore');

// 存储数据
await dataPreferences.put('key', 'value');
await dataPreferences.flush();

// 读取数据
let value = await dataPreferences.get('key', 'defaultValue');

// 删除数据
await dataPreferences.delete('key');
await dataPreferences.flush();
```

### 数据监听

来源: [Preferences数据监听](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-preferences#监听数据变化)

```typescript
dataPreferences.on('change', (key) => {
  console.log(`Key ${key} changed`);
});
```

### 封装版 PreferencesManager

```typescript
import { preferences } from '@kit.ArkData';
import { common } from '@kit.AbilityKit';

class PreferencesManager {
  private prefs: preferences.Preferences | null = null;
  private context: common.UIAbilityContext;

  constructor(context: common.UIAbilityContext) {
    this.context = context;
  }

  async init(): Promise<void> {
    this.prefs = await preferences.getPreferences(this.context, 'app_prefs');
  }

  async set(key: string, value: preferences.ValueType): Promise<void> {
    if (!this.prefs) return;
    await this.prefs.put(key, value);
    await this.prefs.flush();
  }

  async get<T extends preferences.ValueType>(key: string, defaultValue: T): Promise<T> {
    if (!this.prefs) return defaultValue;
    return await this.prefs.get(key, defaultValue) as T;
  }

  async remove(key: string): Promise<void> {
    if (!this.prefs) return;
    await this.prefs.delete(key);
    await this.prefs.flush();
  }
}
```

---

## 关系型数据库（RDB）

来源: [关系型数据库RDB](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-relational-store)

### 初始化

```typescript
import { relationalStore } from '@kit.ArkData';

const STORE_CONFIG: relationalStore.StoreConfig = {
  name: 'RdbStore.db',
  securityLevel: relationalStore.SecurityLevel.S1
};

let store = await relationalStore.getRdbStore(getContext(), STORE_CONFIG);
```

### 创建表

来源: [RDB建表](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-relational-store#创建数据库表)

```typescript
await store.executeSql(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER
  )
`);
```

### 插入数据

来源: [RDB插入](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-relational-store#插入数据)

```typescript
let valueBucket: relationalStore.ValuesBucket = {
  'name': 'John',
  'age': 30
};
await store.insert('users', valueBucket);
```

### 查询数据

来源: [RDB查询](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-relational-store#查询数据)

```typescript
let predicates = new relationalStore.RdbPredicates('users');
predicates.equalTo('name', 'John');

let resultSet = await store.query(predicates);
while (resultSet.goToNextRow()) {
  let id = resultSet.getLong(resultSet.getColumnIndex('id'));
  let name = resultSet.getString(resultSet.getColumnIndex('name'));
}
resultSet.close();  // ⚠️ 必须关闭 ResultSet
```

### 更新数据

来源: [RDB更新](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-relational-store#更新数据)

```typescript
let valueBucket: relationalStore.ValuesBucket = { 'age': 31 };
let predicates = new relationalStore.RdbPredicates('users');
predicates.equalTo('name', 'John');
await store.update(valueBucket, predicates);
```

### 删除数据

来源: [RDB删除](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-relational-store#删除数据)

```typescript
let predicates = new relationalStore.RdbPredicates('users');
predicates.equalTo('name', 'John');
await store.delete(predicates);
```

---

## 分布式数据

来源: [分布式数据对象](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-distributed-data-object)

### 分布式数据对象

```typescript
import { distributedDataObject } from '@kit.ArkData';

let obj: distributedDataObject.DataObject = {
  name: 'John',
  age: 30
};

let localObject = await distributedDataObject.create(getContext(), obj);

// 监听数据变化
localObject.on('change', (sessionId, fields) => {
  console.log('Data changed:', fields);
});

// 加入分布式网络
let sessionId = await localObject.setSessionId();
```

> **完整的分布式能力**（KV Store、设备发现、跨设备调用、任务接续）请参考 [`distributed.md`](distributed.md)。

---

## 文件存储

来源: [文件管理](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-file-management)

### 文件读写

来源: [文件基础操作](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-file-io)

```typescript
import { fileIo } from '@kit.CoreFileKit';

// 写入文件
let file = await fileIo.open(filePath, fileIo.OpenMode.CREATE | fileIo.OpenMode.WRITE_ONLY);
await fileIo.write(file.fd, content);
await fileIo.close(file.fd);

// 读取文件
file = await fileIo.open(filePath, fileIo.OpenMode.READ_ONLY);
let arrayBuffer = new ArrayBuffer(1024);
await fileIo.read(file.fd, arrayBuffer);
await fileIo.close(file.fd);
```

### 目录操作

```typescript
// 创建目录
await fileIo.mkdir(dirPath);

// 列出目录
let files = await fileIo.listFile(dirPath);

// 删除文件
await fileIo.unlink(filePath);
```

### 应用目录路径

```typescript
import { common } from '@kit.AbilityKit';

const context = getContext(this) as common.UIAbilityContext;
const filesDir = context.filesDir;       // 应用文件目录
const cacheDir = context.cacheDir;       // 缓存目录
const tempDir = context.tempDir;         // 临时目录
const databaseDir = context.databaseDir; // 数据库目录
const distFilesDir = context.distributedFilesDir; // 分布式文件目录
```

---

## 数据库安全与可靠性（生产必备）

> 以下规则会被 [`code-review.md`](code-review.md) 中的数据库章节强制检查。违反任何一条都属于 🔴 关键问题。

### 规则1: 数据库加密

敏感数据必须启用加密。`relationalStore.StoreConfig` 默认 `encrypt: false`。

```typescript
// ❌ 错误：未加密的存储用户/订单数据的库
const STORE_CONFIG: relationalStore.StoreConfig = {
  name: 'UserStore.db',
  securityLevel: relationalStore.SecurityLevel.S1
};

// ✅ 正确：敏感数据库必须加密 + 合适的 securityLevel
const STORE_CONFIG: relationalStore.StoreConfig = {
  name: 'UserStore.db',
  securityLevel: relationalStore.SecurityLevel.S3,  // 敏感数据用 S3+
  encrypt: true                                      // 强制加密
};
```

**securityLevel 选择**:
- `S1` — 仅用于完全公开/无敏感的数据
- `S2` — 一般业务数据
- `S3` — 含个人信息（推荐默认）
- `S4` — 高敏感（支付/密码等）

### 规则2: ResultSet 必须在所有代码路径中关闭

未关闭的 ResultSet 会泄漏底层 SQLite 游标，长期运行会导致资源耗尽。

```typescript
// ❌ 错误：异常分支中泄漏
let resultSet = await store.query(predicates);
while (resultSet.goToNextRow()) {
  const name = resultSet.getString(resultSet.getColumnIndex('name'));
  if (name === 'invalid') {
    return;  // 🔴 泄漏！未关闭 resultSet
  }
}
resultSet.close();

// ✅ 正确：try-finally 保证关闭
let resultSet = await store.query(predicates);
try {
  while (resultSet.goToNextRow()) {
    const name = resultSet.getString(resultSet.getColumnIndex('name'));
    if (name === 'invalid') return;  // 仍然安全
  }
} finally {
  resultSet.close();  // 总是执行
}
```

### 规则3: 事务必须正确提交或回滚

```typescript
// ❌ 错误：错误未传播，且没有回滚
async function transferMoney(from: number, to: number, amount: number) {
  store.beginTransaction();
  try {
    await store.update({ balance: -amount }, fromPredicates);
    await store.update({ balance: +amount }, toPredicates);
    store.commit();
  } catch (e) {
    console.error(e);  // 🔴 错误吞掉了，事务也没回滚
  }
}

// ✅ 正确：失败时回滚 + 传播错误
async function transferMoney(from: number, to: number, amount: number) {
  store.beginTransaction();
  try {
    await store.update({ balance: -amount }, fromPredicates);
    await store.update({ balance: +amount }, toPredicates);
    store.commit();
  } catch (e) {
    store.rollBack();  // 关键：失败必须回滚
    throw e;           // 关键：错误必须向上传播
  }
}
```

### 规则4: 版本升级回调

新增数据库表/字段时必须实现升级逻辑：

```typescript
const STORE_CONFIG: relationalStore.StoreConfig = {
  name: 'AppStore.db',
  securityLevel: relationalStore.SecurityLevel.S3,
  encrypt: true
};

let store = await relationalStore.getRdbStore(getContext(), STORE_CONFIG);

// 版本升级
if (store.version === 0) {
  await store.executeSql('CREATE TABLE ...');
  store.version = 1;
}
if (store.version === 1) {
  await store.executeSql('ALTER TABLE users ADD COLUMN email TEXT');
  store.version = 2;
}
```

---

## 选择建议

- **用户设置、开关** → Preferences / PersistentStorage
- **联系人、订单、文章** → RDB（含个人信息时强制 `encrypt: true` + `S3`）
- **多设备共享状态** → 分布式 KV 或分布式对象
- **文档、媒体缓存** → 文件存储
- **运行时跨组件共享（不持久化）** → AppStorage
- **运行时跨组件共享（持久化）** → PersistentStorage