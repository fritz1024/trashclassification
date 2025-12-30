# 小程序配置说明

## 1. 环境配置

### 修改 API 地址

编辑 `utils/config.js` 文件：

```javascript
// 当前环境（根据实际情况修改）
const currentEnv = 'development'  // 开发环境
// const currentEnv = 'production'  // 生产环境
```

### 配置生产环境地址

在 `utils/config.js` 中修改生产环境的 baseURL：

```javascript
production: {
  baseURL: 'https://your-domain.com',  // 修改为你的服务器地址
  apiPrefix: '/api'
}
```

## 2. 微信小程序 appid 配置（可选）

如果你已经申请了微信小程序，需要在 `manifest.json` 中配置 appid：

```json
{
  "appid": "你的小程序appid",
  "mp-weixin": {
    "appid": "你的小程序appid"
  }
}
```

如果还没有申请，可以暂时留空，使用微信开发者工具的测试号进行开发。

## 3. 运行小程序

### 开发环境运行

```bash
npm run dev:mp-weixin
```

### 生产环境构建

```bash
npm run build:mp-weixin
```

## 4. 使用微信开发者工具

1. 打开微信开发者工具
2. 导入项目，选择 `miniprogram/dist/dev/mp-weixin` 目录
3. 如果没有 appid，选择"测试号"
4. 开始开发调试

## 5. 注意事项

- 开发时确保后端服务已启动（默认 http://localhost:8000）
- 生产环境部署前，记得修改 `currentEnv` 为 `'production'`
- 小程序需要配置服务器域名白名单（在微信公众平台配置）