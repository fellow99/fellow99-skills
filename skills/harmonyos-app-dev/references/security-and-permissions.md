# 权限与安全管理参考

> **内容来源**：harmonyos-dev 的 permissions.md + harmonyos-review 的安全检查清单。
>
> 官方文档：
> - 权限管理指南: https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/permissions
> - 申请权限: https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-acquire-permissions
> - 权限列表: https://developer.huawei.com/consumer/cn/doc/harmonyos-references/permissions

---

# 第一部分：安全开发规范

> 以下规则会被 [`code-review.md`](code-review.md) 中的安全检查章节强制验证。违反任何一条都属于 🔴 关键问题。

## 规则1: 禁止硬编码凭据

代码中**严禁**出现明文密钥、Token、密码、签名密码。

```typescript
// ❌ 禁止：硬编码凭据
const API_KEY = 'sk-1234567890abcdef';
const DB_PASSWORD = 'MySecretP@ss';
```

```json5
// ❌ 禁止：build-profile.json5 中明文签名密码
// "signPwd": "123456"
```

```markdown
✅ 解决方案：
- API 密钥 → 服务端下发，或通过环境变量/CI 注入
- 签名密码 → DevEco Studio 签名配置中管理，不提交到 git
- 检查方法：grep -r "password\|secret\|key\|token" --include="*.json5" --include="*.ets"
```

## 规则2: 禁止向用户泄漏错误细节

```typescript
// ❌ 禁止：将数据库错误暴露给 UI
try {
  await store.insert('users', valueBucket);
} catch (e) {
  this.errorMessage = e.message;  // 可能含表结构等敏感信息
}

// ✅ 正确：对外返回通用消息，敏感信息只写日志
try {
  await store.insert('users', valueBucket);
} catch (e) {
  hilog.error(DOMAIN, TAG, 'Insert failed: %{public}s', JSON.stringify(e));
  this.errorMessage = '操作失败，请重试';
}
```

## 规则3: 使用 hilog 代替 console

来源: [hilog 使用指南](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-hilog)

```typescript
// ❌ 禁止：console.log / console.error
console.log('debug info');   // Android 桥接性能差
console.error('error');       // 不归入 HarmonyOS 日志系统

// ✅ 正确：使用 hilog
import { hilog } from '@kit.PerformanceAnalysisKit';

const DOMAIN = 0x0000;
const TAG = 'MyComponent';

hilog.info(DOMAIN, TAG, 'Component initialized');
hilog.error(DOMAIN, TAG, 'Failed: %{public}s', errorMessage);

// 快速检查：grep -r "console\." --include="*.ets" | grep -v "hilog"
```

## 规则4: 验证所有用户输入

```typescript
// ✅ 必须在边界处校验
function processUserInput(input: string): string {
  if (!input || input.length === 0) {
    throw new Error('Input required');
  }
  if (input.length > 1000) {
    throw new Error('Input too long');
  }
  return sanitize(input);
}
```

---

# 第二部分：权限管理

来源: [权限分类](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/permissions#权限分类)

### system_grant（系统授权）

安装时自动授予，包括：
- 网络访问
- 获取网络状态
- 查看网络连接

### user_grant（用户授权）

需要用户手动授予，包括：
- 相机、麦克风
- 位置信息
- 日历、联系人
- 存储、文件访问

## 配置权限

来源: [配置权限](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-acquire-permissions#配置权限)

### module.json5 配置

```json5
{
  "module": {
    "requestPermissions": [
      {
        "name": "ohos.permission.INTERNET",
        "reason": "$string:internet_reason",
        "usedScene": {
          "abilities": ["EntryAbility"],
          "when": "always"
        }
      },
      {
        "name": "ohos.permission.CAMERA",
        "reason": "$string:camera_reason",
        "usedScene": {
          "abilities": ["EntryAbility"],
          "when": "inuse"
        }
      }
    ]
  }
}
```

## 运行时请求权限

来源: [请求用户授权](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-acquire-permissions#请求用户授权)

### 单个权限请求

```typescript
import { abilityAccessCtrl, bundleManager, Permissions } from '@kit.AbilityKit';

async function requestPermission(context: Context, permission: Permissions) {
  let atManager = abilityAccessCtrl.createAtManager();
  let bundleInfo = await bundleManager.getBundleInfoForSelf(bundleManager.BundleFlag.GET_BUNDLE_INFO_WITH_APPLICATION);

  let grantStatus = await atManager.requestPermissionsFromUser(context, [permission]);

  if (grantStatus.authResults[0] === 0) {
    // 权限授予成功
    return true;
  } else {
    // 权限被拒绝
    return false;
  }
}

// 使用
await requestPermission(getContext(), 'ohos.permission.CAMERA');
```

### 多个权限请求

```typescript
let permissions: Permissions[] = [
  'ohos.permission.CAMERA',
  'ohos.permission.READ_MEDIA',
  'ohos.permission.WRITE_MEDIA'
];

let grantStatus = await atManager.requestPermissionsFromUser(getContext(), permissions);

// 检查每个权限的结果
permissions.forEach((permission, index) => {
  if (grantStatus.authResults[index] === 0) {
    console.log(`${permission} granted`);
  } else {
    console.log(`${permission} denied`);
  }
});
```

## 检查权限状态

来源: [校验权限](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-acquire-permissions#校验权限)

```typescript
async function checkPermission(context: Context, permission: Permissions): Promise<boolean> {
  let atManager = abilityAccessCtrl.createAtManager();
  let bundleInfo = await bundleManager.getBundleInfoForSelf(bundleManager.BundleFlag.GET_BUNDLE_INFO_WITH_APPLICATION);

  let grantStatus = await atManager.checkAccessToken(
    bundleInfo.appInfo.accessTokenId,
    permission
  );

  return grantStatus === abilityAccessCtrl.GrantStatus.PERMISSION_GRANTED;
}

// 使用
let hasPermission = await checkPermission(getContext(), 'ohos.permission.CAMERA');
if (!hasPermission) {
  // 请求权限
}
```

## 常用权限列表

来源: [权限列表](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/permissions)

| 权限名 | 类型 | 说明 |
|--------|------|------|
| ohos.permission.INTERNET | system_grant | 网络访问 |
| ohos.permission.GET_NETWORK_INFO | system_grant | 获取网络信息 |
| ohos.permission.CAMERA | user_grant | 使用相机 |
| ohos.permission.MICROPHONE | user_grant | 使用麦克风 |
| ohos.permission.LOCATION | user_grant | 获取位置信息 |
| ohos.permission.APPROXIMATELY_LOCATION | user_grant | 模糊位置信息 |
| ohos.permission.READ_MEDIA | user_grant | 读取媒体文件 |
| ohos.permission.WRITE_MEDIA | user_grant | 写入媒体文件 |
| ohos.permission.READ_PREFERENCES | system_grant | 读取配置 |
| ohos.permission.WRITE_PREFERENCES | system_grant | 写入配置 |

## 权限最佳实践

来源: [权限最佳实践](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/permissions#最佳实践)

1. **最小权限原则**：只申请必要的权限（官方文档规定）
2. **及时请求**：在需要使用权限前再请求（推荐实践）
3. **解释原因**：清楚说明为什么需要该权限（官方文档规定）
4. **处理拒绝**：优雅处理用户拒绝权限的情况（推荐实践）
5. **动态检查**：每次使用前检查权限状态（推荐实践）

## 相关参考

- 网络权限声明后网络请求参考 [`network.md`](network.md)
- 文件读写权限后文件操作参考 [`data-persistence.md`](data-persistence.md)
- 数据库加密配置参考 [`data-persistence.md`](data-persistence.md) 的"数据库安全与可靠性"章节
- 在交付前对照 [`code-review.md`](code-review.md) 的"1. 安全规范评审"运行检查