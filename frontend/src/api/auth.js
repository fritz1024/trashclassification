import request from '@/utils/request'

// 用户登录
export const login = (data) => {
  return request.post('/auth/login', data)
}

// 用户注册
export const register = (data) => {
  return request.post('/auth/register', data)
}

// 获取当前用户信息
export const getCurrentUser = () => {
  return request.get('/auth/me')
}

// 修改密码
export const updatePassword = (data) => {
  return request.put('/auth/password', data)
}

// 更新个人资料
export const updateProfile = (data) => {
  return request.put('/auth/profile', data)
}

// 上传头像
export const uploadAvatar = (formData) => {
  return request.post('/auth/avatar', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
