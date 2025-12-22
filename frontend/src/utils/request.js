import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    let message = '请求失败'

    if (error.response) {
      const { status, data } = error.response

      // 处理不同的错误格式
      if (data?.detail) {
        // FastAPI 标准错误格式: { detail: "错误信息" }
        if (typeof data.detail === 'string') {
          message = data.detail
        } else if (Array.isArray(data.detail)) {
          // FastAPI 422 验证错误格式: { detail: [{ msg: "错误", loc: [...] }] }
          message = data.detail.map(err => err.msg).join('; ')
        }
      } else if (data?.message) {
        message = data.message
      } else if (status === 422) {
        message = '数据验证失败，请检查输入'
      } else if (status === 401) {
        message = '未授权，请先登录'
      } else if (status === 403) {
        message = '没有权限访问'
      } else if (status === 404) {
        message = '请求的资源不存在'
      } else if (status === 500) {
        message = '服务器错误'
      }
    } else if (error.request) {
      message = '网络错误，请检查网络连接'
    }

    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default request
