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
