import request from '../utils/request.js'

/**
 * 获取用户统计数据
 */
export function getUserStats() {
  return request.get('/stats/user')
}

/**
 * 获取全局统计数据（管理员）
 */
export function getGlobalStats() {
  return request.get('/stats/global')
}
