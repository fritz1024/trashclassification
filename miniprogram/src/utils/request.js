import config from './config.js'

/**
 * 封装 uni.request 请求
 */
class Request {
  constructor() {
    this.baseURL = config.apiURL  // 使用完整的 API 地址
    this.timeout = config.timeout
  }

  // 获取 token
  getToken() {
    return uni.getStorageSync('token') || ''
  }

  // 请求拦截器
  interceptRequest(options) {
    const token = this.getToken()
    if (token) {
      options.header = {
        ...options.header,
        'Authorization': `Bearer ${token}`
      }
    }
    return options
  }

  // 响应拦截器
  interceptResponse(response) {
    const { statusCode, data } = response

    // 请求成功
    if (statusCode === 200) {
      return data
    }

    // token 过期或无效
    if (statusCode === 401) {
      uni.removeStorageSync('token')
      uni.removeStorageSync('userInfo')
      uni.showToast({
        title: '请先登录',
        icon: 'none'
      })
      setTimeout(() => {
        uni.navigateTo({
          url: '/pages/login/login'
        })
      }, 1500)
      return Promise.reject(data)
    }

    // 其他错误
    uni.showToast({
      title: data.detail || '请求失败',
      icon: 'none'
    })
    return Promise.reject(data)
  }

  // 通用请求方法
  request(options) {
    options.url = this.baseURL + options.url
    options.timeout = this.timeout
    options = this.interceptRequest(options)

    return new Promise((resolve, reject) => {
      uni.request({
        ...options,
        success: (res) => {
          resolve(this.interceptResponse(res))
        },
        fail: (err) => {
          uni.showToast({
            title: '网络请求失败',
            icon: 'none'
          })
          reject(err)
        }
      })
    })
  }

  // GET 请求
  get(url, data = {}, options = {}) {
    return this.request({
      url,
      data,
      method: 'GET',
      ...options
    })
  }

  // POST 请求
  post(url, data = {}, options = {}) {
    return this.request({
      url,
      data,
      method: 'POST',
      header: {
        'Content-Type': 'application/json',
        ...options.header
      },
      ...options
    })
  }

  // 文件上传
  upload(url, filePath, name = 'file', formData = {}) {
    const token = this.getToken()

    return new Promise((resolve, reject) => {
      uni.uploadFile({
        url: this.baseURL + url,
        filePath,
        name,
        formData,
        header: {
          'Authorization': token ? `Bearer ${token}` : ''
        },
        success: (res) => {
          if (res.statusCode === 200) {
            const data = JSON.parse(res.data)
            resolve(data)
          } else {
            const data = JSON.parse(res.data)
            uni.showToast({
              title: data.detail || '上传失败',
              icon: 'none'
            })
            reject(data)
          }
        },
        fail: (err) => {
          uni.showToast({
            title: '上传失败',
            icon: 'none'
          })
          reject(err)
        }
      })
    })
  }
}

export default new Request()
