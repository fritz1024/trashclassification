import request from '@/utils/request'

// 获取用户统计数据
export const getUserStats = () => {
  return request.get('/stats/user')
}

// 获取全局统计数据（管理员）
export const getGlobalStats = () => {
  return request.get('/stats/global')
}
