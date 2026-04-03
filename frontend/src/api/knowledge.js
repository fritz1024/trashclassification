import request from '@/utils/request'

// 上传知识库文档
export const uploadDocument = (formData) => {
  return request.post('/admin/knowledge/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 获取知识库文档列表
export const getDocuments = (params) => {
  return request.get('/admin/knowledge', { params })
}

// 获取文档内容
export const getDocumentContent = (id) => {
  return request.get(`/admin/knowledge/${id}/content`)
}

// 更新文档内容
export const updateDocument = (id, content) => {
  return request.put(`/admin/knowledge/${id}`, { content })
}

// 删除知识库文档
export const deleteDocument = (id) => {
  return request.delete(`/admin/knowledge/${id}`)
}
