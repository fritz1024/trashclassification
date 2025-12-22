/**
 * AI聊天相关API
 */
import request from '../utils/request'

/**
 * 发送聊天消息
 * @param {Array} messages - 对话历史 [{role: 'user', content: '...'}, ...]
 */
export function sendMessage(messages) {
  return request({
    url: '/chat/',
    method: 'post',
    data: {
      messages
    }
  })
}

/**
 * 检查AI服务健康状态
 */
export function checkHealth() {
  return request({
    url: '/chat/health',
    method: 'get'
  })
}

// ==================== 对话历史管理 API ====================

/**
 * 获取所有对话历史
 */
export function getConversations() {
  return request({
    url: '/chat/conversations',
    method: 'get'
  })
}

/**
 * 获取指定对话详情
 * @param {Number} conversationId - 对话ID
 */
export function getConversation(conversationId) {
  return request({
    url: `/chat/conversations/${conversationId}`,
    method: 'get'
  })
}

/**
 * 创建新对话
 * @param {Object} data - {title: string, messages: Array}
 */
export function createConversation(data) {
  return request({
    url: '/chat/conversations',
    method: 'post',
    data
  })
}

/**
 * 更新对话
 * @param {Number} conversationId - 对话ID
 * @param {Object} data - {title?: string, messages?: Array}
 */
export function updateConversation(conversationId, data) {
  return request({
    url: `/chat/conversations/${conversationId}`,
    method: 'put',
    data
  })
}

/**
 * 删除对话
 * @param {Number} conversationId - 对话ID
 */
export function deleteConversation(conversationId) {
  return request({
    url: `/chat/conversations/${conversationId}`,
    method: 'delete'
  })
}
