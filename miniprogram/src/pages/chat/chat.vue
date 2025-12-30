<template>
  <view class="container">
    <!-- 未登录提示 -->
    <view v-if="!isLogin" class="empty-state">
      <view class="empty-icon-box">
        <text class="empty-icon-text">未登录</text>
      </view>
      <text class="empty-text">请先登录使用AI助手</text>
      <button class="login-btn" @click="goLogin">去登录</button>
    </view>

    <!-- 聊天界面 -->
    <view v-else class="chat-container">
      <!-- 顶部操作栏 -->
      <view class="chat-header">
        <button class="header-btn" @click="showHistoryDrawer = true">
          <text class="btn-text">历史</text>
        </button>
        <button class="header-btn" @click="createNewChat">
          <text class="btn-text">新对话</text>
        </button>
        <button class="header-btn" @click="clearChat">
          <text class="btn-text">清空</text>
        </button>
      </view>

      <!-- 消息列表 -->
      <scroll-view
        class="message-list"
        scroll-y
        :scroll-into-view="scrollToView"
        scroll-with-animation
      >
        <!-- 欢迎消息 -->
        <view v-if="messages.length === 0" class="welcome-section">
          <view class="welcome-icon-box">
            <text class="welcome-icon-text">AI</text>
          </view>
          <text class="welcome-title">有什么我能帮你的吗？</text>
          <text class="welcome-subtitle">我可以帮你解答垃圾分类相关的问题</text>
        </view>

        <!-- 消息列表 -->
        <view
          v-for="(msg, index) in messages"
          :key="index"
          :id="'msg-' + index"
          class="message-item"
          :class="msg.role"
        >
          <view class="message-avatar">
            <text class="avatar-text">{{ msg.role === 'user' ? '我' : 'AI' }}</text>
          </view>
          <view class="message-bubble">
            <rich-text v-if="msg.role === 'assistant'" :nodes="formatMarkdown(msg.content)" class="message-text"></rich-text>
            <text v-else class="message-text">{{ msg.content }}</text>
          </view>
        </view>

        <!-- 加载中 -->
        <view v-if="loading" class="message-item assistant">
          <view class="message-avatar">
            <text class="avatar-text">AI</text>
          </view>
          <view class="message-bubble">
            <text class="loading-text">思考中...</text>
          </view>
        </view>
      </scroll-view>

      <!-- 输入框 -->
      <view class="input-area">
        <input
          class="input"
          v-model="inputText"
          placeholder="输入您的问题..."
          placeholder-class="placeholder"
          @confirm="sendMessage"
        />
        <button
          class="send-btn"
          @click="sendMessage"
          :disabled="loading || !inputText.trim()"
        >
          发送
        </button>
      </view>

      <!-- 历史对话抽屉 -->
      <view v-if="showHistoryDrawer" class="history-drawer-mask" @click="showHistoryDrawer = false">
        <view class="history-drawer" @click.stop>
          <view class="drawer-header">
            <text class="drawer-title">历史对话</text>
            <text class="drawer-close" @click="showHistoryDrawer = false">✕</text>
          </view>
          <scroll-view class="history-list" scroll-y>
            <view
              v-for="conv in conversations"
              :key="conv.id"
              class="history-item"
              :class="{ active: currentConversationId === conv.id }"
              @click="switchConversation(conv.id)"
            >
              <view class="history-info">
                <text class="history-title">{{ conv.title }}</text>
                <text class="history-time">{{ formatTime(conv.updated_at) }}</text>
              </view>
              <text class="delete-icon" @click.stop="deleteConversation(conv.id)">🗑️</text>
            </view>
            <view v-if="conversations.length === 0" class="empty-history">
              <text class="empty-text">暂无历史对话</text>
            </view>
          </scroll-view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { sendMessage as sendChatMessage, getConversations, createConversation, deleteConversation as deleteConv, updateConversation } from '../../api/chat.js'

export default {
  data() {
    return {
      isLogin: false,
      messages: [],
      inputText: '',
      loading: false,
      scrollToView: '',
      showHistoryDrawer: false,
      conversations: [],
      currentConversationId: null
    }
  },

  onLoad() {
    this.checkLogin()
    if (this.isLogin) {
      this.loadConversations()
    }
  },

  onShow() {
    // 每次页面显示时重新检查登录状态
    this.checkLogin()
    if (this.isLogin) {
      this.loadConversations()
    }
  },

  methods: {
    checkLogin() {
      const token = uni.getStorageSync('token')
      this.isLogin = !!token
    },

    goLogin() {
      uni.navigateTo({
        url: '/pages/login/login'
      })
    },

    async loadConversations() {
      try {
        const res = await getConversations()
        this.conversations = res || []
      } catch (error) {
        console.error('加载对话列表失败:', error)
      }
    },

    async createNewChat() {
      try {
        const title = '新对话'
        const res = await createConversation(title)
        this.currentConversationId = res.id
        this.messages = []
        await this.loadConversations()
        uni.showToast({
          title: '已创建新对话',
          icon: 'success'
        })
      } catch (error) {
        console.error('创建对话失败:', error)
        uni.showToast({
          title: '创建失败',
          icon: 'none'
        })
      }
    },

    clearChat() {
      uni.showModal({
        title: '提示',
        content: '确定要清空当前对话吗？',
        success: (res) => {
          if (res.confirm) {
            this.messages = []
            uni.showToast({
              title: '已清空',
              icon: 'success'
            })
          }
        }
      })
    },

    async sendMessage() {
      const text = this.inputText.trim()
      if (!text || this.loading) return

      // 如果没有当前对话，先创建一个
      if (!this.currentConversationId) {
        await this.createNewChat()
      }

      // 添加用户消息
      this.messages.push({
        role: 'user',
        content: text
      })
      this.inputText = ''
      this.scrollToBottom()

      this.loading = true
      try {
        // 发送完整的对话历史
        const res = await sendChatMessage({
          messages: this.messages
        })

        // 添加AI回复
        if (res && res.reply) {
          this.messages.push({
            role: 'assistant',
            content: res.reply
          })
          this.scrollToBottom()

          // 保存对话到后端
          await this.saveConversation()
        } else {
          throw new Error('无效的响应格式')
        }
      } catch (error) {
        console.error('聊天错误:', error)

        // 移除刚才添加的用户消息（因为发送失败）
        this.messages.pop()

        // 显示错误提示
        const errorMsg = error.detail ?
          (Array.isArray(error.detail) ? error.detail[0].msg : error.detail) :
          '发送失败，请重试'

        uni.showToast({
          title: errorMsg,
          icon: 'none'
        })
      } finally {
        this.loading = false
      }
    },

    scrollToBottom() {
      this.$nextTick(() => {
        this.scrollToView = 'msg-' + (this.messages.length - 1)
      })
    },

    async saveConversation() {
      if (!this.currentConversationId) return

      try {
        // 生成对话标题（使用第一条用户消息的前20个字符）
        let title = '新对话'
        const firstUserMsg = this.messages.find(m => m.role === 'user')
        if (firstUserMsg) {
          title = firstUserMsg.content.substring(0, 20)
          if (firstUserMsg.content.length > 20) {
            title += '...'
          }
        }

        // 更新对话
        await updateConversation(this.currentConversationId, {
          title,
          messages: this.messages
        })

        // 刷新对话列表
        await this.loadConversations()
      } catch (error) {
        console.error('保存对话失败:', error)
      }
    },

    async switchConversation(id) {
      try {
        const conv = this.conversations.find(c => c.id === id)
        if (conv) {
          this.currentConversationId = id
          this.messages = conv.messages || []
          this.showHistoryDrawer = false
        }
      } catch (error) {
        console.error('切换对话失败:', error)
      }
    },

    async deleteConversation(id) {
      uni.showModal({
        title: '提示',
        content: '确定要删除这个对话吗？',
        success: async (res) => {
          if (res.confirm) {
            try {
              await deleteConv(id)
              if (this.currentConversationId === id) {
                this.currentConversationId = null
                this.messages = []
              }
              this.loadConversations()
              uni.showToast({
                title: '已删除',
                icon: 'success'
              })
            } catch (error) {
              console.error('删除对话失败:', error)
            }
          }
        }
      })
    },

    formatTime(time) {
      const date = new Date(time)
      const now = new Date()
      const diff = now - date

      if (diff < 60000) return '刚刚'
      if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
      if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'

      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${month}-${day}`
    },

    formatMarkdown(text) {
      if (!text) return ''

      // 转义HTML特殊字符
      let html = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')

      // 处理代码块 ```code```
      html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
        return `<div style="background:#f5f5f5;padding:10px;border-radius:5px;margin:10px 0;overflow-x:auto;"><code style="font-family:monospace;font-size:14px;white-space:pre;">${code.trim()}</code></div>`
      })

      // 处理行内代码 `code`
      html = html.replace(/`([^`]+)`/g, '<code style="background:#f5f5f5;padding:2px 6px;border-radius:3px;font-family:monospace;font-size:14px;">$1</code>')

      // 处理粗体 **text**
      html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')

      // 处理斜体 *text*
      html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>')

      // 处理换行
      html = html.replace(/\n/g, '<br/>')

      return html
    }
  }
}
</script>

<style scoped>
.container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.empty-icon-box {
  width: 120rpx;
  height: 120rpx;
  border-radius: 60rpx;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 30rpx;
}

.empty-icon-text {
  font-size: 32rpx;
  color: #999;
  font-weight: bold;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
  margin-bottom: 40rpx;
}

.login-btn {
  width: 300rpx;
  height: 80rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 40rpx;
  font-size: 28rpx;
  border: none;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-header {
  background: #fff;
  padding: 20rpx;
  border-bottom: 1rpx solid #e5e5e5;
  display: flex;
  justify-content: flex-end;
  gap: 15rpx;
}

.header-btn {
  display: flex;
  align-items: center;
  padding: 12rpx 24rpx;
  background: #f5f5f5;
  border-radius: 20rpx;
  border: none;
  font-size: 26rpx;
  color: #666;
}

.btn-text {
  font-size: 26rpx;
}

.welcome-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 40rpx;
  text-align: center;
}

.welcome-icon-box {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 30rpx;
}

.welcome-icon-text {
  font-size: 36rpx;
  color: #fff;
  font-weight: bold;
}

.welcome-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
}

.welcome-subtitle {
  font-size: 28rpx;
  color: #999;
}

.message-list {
  flex: 1;
  padding: 20rpx;
  overflow-y: auto;
}

.message-item {
  display: flex;
  margin-bottom: 20rpx;
  align-items: flex-start;
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 60rpx;
  height: 60rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message-item.user .message-avatar {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  margin-left: 15rpx;
}

.message-item.assistant .message-avatar {
  margin-right: 15rpx;
}

.avatar-text {
  font-size: 24rpx;
  color: #fff;
  font-weight: bold;
}

.message-bubble {
  max-width: 70%;
  padding: 20rpx 30rpx;
  border-radius: 16rpx;
  word-wrap: break-word;
}

.message-item.user .message-bubble {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.message-item.assistant .message-bubble {
  background: #fff;
}

.message-text {
  font-size: 28rpx;
  line-height: 1.6;
  word-break: break-word;
}

/* rich-text 内部样式 */
.message-text >>> strong {
  font-weight: bold;
}

.message-text >>> em {
  font-style: italic;
}

.message-text >>> code {
  font-family: 'Courier New', monospace;
}

.message-item.user .message-text {
  color: #fff;
}

.message-item.assistant .message-text {
  color: #333;
}

.loading-text {
  font-size: 28rpx;
  color: #999;
}

.input-area {
  display: flex;
  align-items: center;
  padding: 20rpx;
  background: #fff;
  border-top: 1rpx solid #eee;
}

.input {
  flex: 1;
  height: 70rpx;
  background: #f5f5f5;
  border-radius: 35rpx;
  padding: 0 30rpx;
  font-size: 28rpx;
  margin-right: 20rpx;
}

.placeholder {
  color: #ccc;
}

.send-btn {
  width: 120rpx;
  height: 70rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 35rpx;
  font-size: 28rpx;
  border: none;
}

.send-btn[disabled] {
  opacity: 0.5;
}

/* 历史对话抽屉 */
.history-drawer-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

.history-drawer {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 70%;
  background: #fff;
  display: flex;
  flex-direction: column;
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #e5e5e5;
}

.drawer-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.drawer-close {
  font-size: 40rpx;
  color: #999;
}

.history-list {
  flex: 1;
  overflow-y: auto;
}

.history-item {
  display: flex;
  align-items: center;
  padding: 25rpx 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.history-item.active {
  background: #f5f5f5;
}

.history-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.history-title {
  font-size: 28rpx;
  color: #333;
  margin-bottom: 8rpx;
}

.history-time {
  font-size: 24rpx;
  color: #999;
}

.delete-icon {
  font-size: 32rpx;
  color: #ff4d4f;
  padding: 10rpx;
}

.empty-history {
  padding: 100rpx 40rpx;
  text-align: center;
}

.empty-history .empty-text {
  font-size: 28rpx;
  color: #999;
}
</style>
