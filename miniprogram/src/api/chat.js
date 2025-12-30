import request from '../utils/request.js'

/**
 * 发送聊天消息
 */
export function sendMessage(data) {
  return request.post('/chat/', data)
}

/**
 * 获取对话历史
 */
export function getChatHistory(conversationId) {
  return request.get('/chat/history', { conversation_id: conversationId })
}

/**
 * 获取对话列表
 */
export function getConversations() {
  return request.get('/chat/conversations')
}

/**
 * 创建新对话
 */
export function createConversation(title) {
  return request.post('/chat/conversations', {
    title,
    messages: []
  })
}

/**
 * 删除对话
 */
export function deleteConversation(conversationId) {
  return request.request({
    url: `/chat/conversations/${conversationId}`,
    method: 'DELETE'
  })
}

/**
 * 更新对话
 */
export function updateConversation(conversationId, data) {
  return request.request({
    url: `/chat/conversations/${conversationId}`,
    method: 'PUT',
    data
  })
}

/**
 * 检查 AI 服务状态
 */
export function checkHealth() {
  return request.get('/chat/health')
}
