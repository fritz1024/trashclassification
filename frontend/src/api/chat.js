/**
 * AI聊天相关API
 */
import request from '../utils/request'

/**
 * 发送聊天消息
 * @param {Array} messages - 对话历史 [{role: 'user', content: '...'}, ...]
 * @param {Boolean} showReasoning - 是否显示推理过程
 */
export function sendMessage(messages, showReasoning = true) {
  return request({
    url: '/chat/',
    method: 'post',
    data: {
      messages,
      show_reasoning: showReasoning
    }
  })
}

/**
 * 发送聊天消息 (流式返回)
 * @param {Array} messages - 对话历史
 * @param {Boolean} showReasoning - 是否显示推理过程
 * @param {Function} onMessage - 接收到消息块的回调函数 (content) => void
 * @param {Function} onError - 发生错误的回调函数 (error) => void
 */
export async function sendMessageStream(messages, showReasoning = true, onMessage, onError) {
  try {
    const token = localStorage.getItem('token') || ''
    const response = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        messages,
        show_reasoning: showReasoning
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() // 最后一行可能不完整，保留到下一次处理

      for (const line of lines) {
        if (line.trim() === '') continue
        try {
          const data = JSON.parse(line)
          if (data.type === 'error') {
            if (onError) onError(new Error(data.content))
          } else if (data.type === 'content') {
            if (onMessage) onMessage(data.content)
          }
        } catch (e) {
          console.error('JSON parse error:', e, 'Line:', line)
        }
      }
    }
    
    // 处理最后一个不完整的块（如果有）
    if (buffer.trim()) {
      try {
        const data = JSON.parse(buffer)
        if (data.type === 'content' && onMessage) {
          onMessage(data.content)
        }
      } catch (e) {
        // ignore
      }
    }
    
    return true
  } catch (error) {
    if (onError) onError(error)
    return false
  }
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
