import request from '@/utils/request'

// 获取所有识别记录（管理员）
export const getAllPredictions = (params) => {
  return request.get('/admin/predictions', { params })
}

// 删除识别记录（管理员）
export const deletePredictionAdmin = (id) => {
  return request.delete(`/admin/predictions/${id}`)
}

// 获取所有用户（管理员）
export const getAllUsers = (params) => {
  return request.get('/admin/users', { params })
}

// 更新用户状态（管理员）
export const updateUserStatus = (userId, isActive) => {
  return request.put(`/admin/users/${userId}/status`, null, {
    params: { is_active: isActive }
  })
}

// 删除用户（管理员）
export const deleteUser = (userId) => {
  return request.delete(`/admin/users/${userId}`)
}

// 重置用户密码（管理员）
export const resetUserPassword = (userId, newPassword) => {
  return request.put(`/admin/users/${userId}/password`, {
    new_password: newPassword
  })
}

// 获取所有反馈（管理员）
export const getAllFeedbacks = (params) => {
  return request.get('/admin/feedbacks', { params })
}

// 更新反馈状态（管理员）
export const updateFeedbackStatus = (feedbackId, status) => {
  return request.put(`/admin/feedbacks/${feedbackId}`, null, {
    params: { status_value: status }
  })
}

// 获取所有知识（管理员）
export const getAllKnowledgeAdmin = (params) => {
  return request.get('/admin/knowledge', { params })
}

// 创建知识（管理员）
export const createKnowledge = (data) => {
  return request.post('/admin/knowledge', data)
}

// 更新知识（管理员）
export const updateKnowledge = (id, data) => {
  return request.put(`/admin/knowledge/${id}`, data)
}

// 删除知识（管理员）
export const deleteKnowledge = (id) => {
  return request.delete(`/admin/knowledge/${id}`)
}
