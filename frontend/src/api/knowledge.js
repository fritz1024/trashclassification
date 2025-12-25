import request from '@/utils/request'

// 获取知识库列表（用户端 - 博文列表）
export const getKnowledgeList = (params) => {
  return request.get('/knowledge', { params })
}

// 获取知识详情（博文详情）
export const getKnowledgeDetail = (id) => {
  return request.get(`/knowledge/${id}`)
}

// 获取相关文章推荐
export const getRelatedKnowledge = (id, limit = 3) => {
  return request.get(`/knowledge/${id}/related`, { params: { limit } })
}

// 根据分类获取知识
export const getKnowledgeByCategory = (category) => {
  return request.get('/knowledge', {
    params: { category }
  })
}
