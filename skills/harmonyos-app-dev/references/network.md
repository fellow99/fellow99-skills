# 网络通信参考

> **内容合并自** harmonyos-dev 的 network.md（HTTP / WebSocket / TCP / UDP / 上传下载）+ harmonyos-app extended.md 的 HttpClient 类封装。
>
> 官方文档：
> - 网络管理: https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/network-management
> - HTTP 请求: https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-http-request
> - WebSocket: https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-websocket
> - Socket: https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-socket
> - 上传下载: https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-upload-download

## HTTP 请求

来源: [HTTP网络请求](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-http-request)

### 基础 GET 请求

```typescript
import { http } from '@kit.NetworkKit';

let request = http.createHttp();

let response = await request.request('https://api.example.com/data', {
  method: http.RequestMethod.GET,
  header: {
    'Content-Type': 'application/json'
  },
  connectTimeout: 60000,
  readTimeout: 60000
});

if (response.responseType === http.ResponseType.STRING) {
  let data = JSON.parse(response.result as string);
}

request.destroy();  // ⚠️ 必须销毁，释放底层资源
```

### POST 请求

来源: [HTTP POST请求](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-http-request#发起post请求)

```typescript
let response = await request.request('https://api.example.com/data', {
  method: http.RequestMethod.POST,
  header: {
    'Content-Type': 'application/json'
  },
  extraData: JSON.stringify({
    key1: 'value1',
    key2: 'value2'
  })
});
```

---

## HttpClient 封装（推荐用于生产）

完整的、带认证和错误处理的 HTTP 客户端封装：

```typescript
import { http } from '@kit.NetworkKit';

export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export class HttpClient {
  private baseUrl: string;
  private timeout: number = 30000;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async request<T>(
    method: http.RequestMethod,
    path: string,
    data?: Object
  ): Promise<T> {
    const httpRequest = http.createHttp();

    try {
      const response = await httpRequest.request(
        `${this.baseUrl}${path}`,
        {
          method: method,
          header: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${await this.getToken()}`
          },
          extraData: data ? JSON.stringify(data) : undefined,
          connectTimeout: this.timeout,
          readTimeout: this.timeout,
          expectDataType: http.HttpDataType.OBJECT
        }
      );

      if (response.responseCode >= 200 && response.responseCode < 300) {
        const result = response.result as ApiResponse<T>;
        if (result.code === 0) {
          return result.data;
        }
        throw new Error(result.message);
      }
      throw new Error(`HTTP ${response.responseCode}`);
    } finally {
      httpRequest.destroy();  // 关键：始终释放资源
    }
  }

  async get<T>(path: string): Promise<T> {
    return this.request<T>(http.RequestMethod.GET, path);
  }

  async post<T>(path: string, data: Object): Promise<T> {
    return this.request<T>(http.RequestMethod.POST, path, data);
  }

  async put<T>(path: string, data: Object): Promise<T> {
    return this.request<T>(http.RequestMethod.PUT, path, data);
  }

  async delete(path: string): Promise<void> {
    await this.request<void>(http.RequestMethod.DELETE, path);
  }

  private async getToken(): Promise<string> {
    return AppStorage.get('authToken') ?? '';
  }
}

// 单例导出
export const httpClient = new HttpClient('https://api.example.com');
```

---

## 文件上传与下载

来源: [上传下载](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-upload-download)

### 上传

```typescript
import { request } from '@kit.BasicServicesKit';

let uploadTask = await request.uploadFile(getContext(), {
  url: 'https://example.com/upload',
  method: 'POST',
  files: [
    {
      filename: 'test.txt',
      name: 'file',
      uri: 'file://path/to/file.txt',
      type: 'txt'
    }
  ],
  data: []
});

uploadTask.on('progress', (uploadedSize, totalSize) => {
  console.log(`Progress: ${uploadedSize}/${totalSize}`);
});
```

### 下载

```typescript
let downloadTask = await request.downloadFile(getContext(), {
  url: 'https://example.com/file.zip',
  filePath: '/data/storage/el2/files/download.zip'
});

downloadTask.on('progress', (downloadedSize, totalSize) => {
  console.log(`Progress: ${downloadedSize}/${totalSize}`);
});
```

---

## WebSocket

来源: [WebSocket连接](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-websocket)

### 建立连接

```typescript
import { webSocket } from '@kit.NetworkKit';

let ws = webSocket.createWebSocket();

ws.connect('ws://example.com/socket', (err, value) => {
  if (!err) {
    console.log('Connected');
  }
});
```

### 发送与接收

```typescript
// 发送
ws.send('Hello Server', (err) => {
  if (err) {
    console.error('Send error:', err);
  }
});

// 接收
ws.on('message', (err, data) => {
  if (!err) {
    console.log('Received:', data);
  }
});

// 关闭
ws.close((err) => {
  if (!err) {
    console.log('Closed');
  }
});
```

---

## Socket 连接

来源: [Socket连接](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-socket)

### TCP Socket

来源: [TCP Socket](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-socket#tcp-socket开发)

```typescript
import { socket } from '@kit.NetworkKit';

let tcp = socket.constructTCPSocketInstance();

await tcp.bind({ address: '0.0.0.0', port: 8888, family: 1 });

await tcp.connect({
  address: '192.168.1.1',
  port: 9999,
  family: 1
});

tcp.on('message', (data) => {
  console.log('Received:', data);
});

await tcp.send({ data: 'Hello' });
```

### UDP Socket

来源: [UDP Socket](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-socket#udp-socket开发)

```typescript
let udp = socket.constructUDPSocketInstance();

await udp.bind({ address: '0.0.0.0', port: 8888, family: 1 });

udp.on('message', (data) => {
  console.log('Received:', data);
});

await udp.send({
  data: 'Hello',
  address: { address: '192.168.1.1', port: 9999, family: 1 }
});
```

---

## 网络状态

来源: [网络连接管理](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-net-connection)

### 监听网络变化

```typescript
import { connection } from '@kit.NetworkKit';

let netCon = connection.createNetConnection();

netCon.register((error, data) => {
  if (!error) {
    console.log('Network type:', data.type);
    console.log('Is available:', data.isAvailable);
  }
});

// 取消注册
netCon.unregister();
```

### 获取网络类型

```typescript
let netType = connection.getConnectionType();
console.log('Network type:', netType);
```

---

## 最佳实践

1. **始终调用 `destroy()`** — `http.createHttp()` 创建的实例必须显式销毁以释放底层网络资源（参见 HttpClient 示例的 `finally` 块）。
2. **统一错误处理** — 包装一层 `ApiResponse<T>` 处理业务码和 HTTP 码。
3. **认证集中管理** — Token 通过 AppStorage 或专用 AuthManager 注入，避免散落各处。
4. **请求缓存与合并** — 参考 [`performance.md`](performance.md) 的 ApiCache 和 RequestBatcher 模式。
5. **网络权限** — 在 `module.json5` 声明 `ohos.permission.INTERNET`（system_grant）。详见 [`permissions.md`](permissions.md)。