import request from '@/utils/request'

// 获取知识库列表（用户端）
export const getKnowledgeList = (params) => {
  return request.get('/knowledge', { params })
}

// 根据分类获取知识
export const getKnowledgeByCategory = (category) => {
  return request.get('/knowledge', {
    params: { category }
  })
}
