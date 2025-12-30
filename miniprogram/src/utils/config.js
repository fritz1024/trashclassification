// 环境配置
const ENV = {
  // 开发环境
  development: {
    baseURL: 'http://localhost:8000',
    apiPrefix: '/api'
  },
  // 生产环境
  production: {
    baseURL: 'https://your-domain.com',  // 请修改为实际的服务器地址
    apiPrefix: '/api'
  }
}

// 当前环境（根据实际情况修改）
// 'development' - 开发环境
// 'production' - 生产环境
const currentEnv = 'development'

// API 配置
export const config = {
  // API 基础地址
  baseURL: ENV[currentEnv].baseURL,

  // API 前缀
  apiPrefix: ENV[currentEnv].apiPrefix,

  // 完整的 API 地址
  get apiURL() {
    return this.baseURL + this.apiPrefix
  },

  // 请求超时时间（毫秒）
  timeout: 30000,

  // 图片上传大小限制（MB）
  maxImageSize: 10,

  // 当前环境
  env: currentEnv,

  // 是否为开发环境
  isDev: currentEnv === 'development'
}

export default config
