<template>
  <div class="chat-widget">
    <!-- 聊天按钮 -->
    <el-button
      v-if="!isOpen"
      class="chat-button"
      type="primary"
      :icon="ChatDotRound"
      circle
      size="large"
      @click="toggleChat"
    />

    <!-- 聊天窗口 -->
    <el-card v-if="isOpen" class="chat-window" shadow="always">
      <!-- 头部 -->
      <template #header>
        <div class="chat-header">
          <div class="header-title">
            <el-icon><ChatDotRound /></el-icon>
            <span>AI 助手</span>
          </div>
          <div class="header-actions">
            <el-button
              text
              :icon="Delete"
              @click="clearChat"
              title="清空对话"
            />
            <el-button
              text
              :icon="Close"
              @click="toggleChat"
              title="关闭"
            />
          </div>
        </div>
      </template>

      <!-- 消息列表 -->
      <div class="chat-messages" ref="messagesContainer">
        <!-- 欢迎消息 -->
        <div v-if="messages.length === 0" class="welcome-message">
          <el-icon class="welcome-icon"><ChatDotRound /></el-icon>
          <p>你好！我是垃圾分类 AI 助手</p>
          <p class="welcome-tips">我可以帮你：</p>
          <ul class="welcome-list">
            <li>解答垃圾分类问题</li>
            <li>解释识别结果</li>
            <li>提供环保建议</li>
          </ul>
        </div>

        <!-- 对话消息 -->
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message', msg.role]"
        >
          <div class="message-avatar">
            <el-icon v-if="msg.role === 'user'"><User /></el-icon>
            <el-icon v-else><ChatDotRound /></el-icon>
          </div>
          <div class="message-content">
            <div class="message-text">{{ msg.content }}</div>
          </div>
        </div>

        <!-- 加载中 -->
        <div v-if="loading" class="message assistant">
          <div class="message-avatar">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <div class="message-content">
            <div class="message-text typing">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入框 -->
      <div class="chat-input">
        <el-input
          v-model="inputMessage"
          placeholder="输入消息..."
          @keyup.enter="sendMessage"
          :disabled="loading"
        >
          <template #append>
            <el-button
              :icon="Promotion"
              @click="sendMessage"
              :loading="loading"
              :disabled="!inputMessage.trim()"
            />
          </template>
        </el-input>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { ChatDotRound, Close, Delete, User, Promotion } from '@element-plus/icons-vue'
import { sendMessage as sendChatMessage } from '../api/chat'
import { ElMessage } from 'element-plus'

// 状态
const isOpen = ref(false)
const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)

// 切换聊天窗口
const toggleChat = () => {
  isOpen.value = !isOpen.value
}

// 清空对话
const clearChat = () => {
  messages.value = []
  ElMessage.success('对话已清空')
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim() || loading.value) return

  const userMessage = inputMessage.value.trim()
  inputMessage.value = ''

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: userMessage
  })
  scrollToBottom()

  // 调用API
  loading.value = true
  try {
    const response = await sendChatMessage(messages.value)

    if (response.success) {
      // 添加AI回复
      messages.value.push({
        role: 'assistant',
        content: response.reply
      })
      scrollToBottom()
    } else {
      ElMessage.error(response.error || 'AI 服务暂时不可用')
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error('发送消息失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 组件挂载时的初始化
onMounted(() => {
  // 可以在这里添加初始化逻辑
})
</script>

<style scoped>
.chat-widget {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 9999;
}

/* 聊天按钮 */
.chat-button {
  width: 60px;
  height: 60px;
  font-size: 28px;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
  transition: all 0.3s;
}

.chat-button:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.6);
}

/* 聊天窗口 */
.chat-window {
  width: 380px;
  height: 600px;
  display: flex;
  flex-direction: column;
  border-radius: 12px;
  overflow: hidden;
}

.chat-window :deep(.el-card__header) {
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.chat-window :deep(.el-card__body) {
  padding: 0;
  display: flex;
  flex-direction: column;
  height: calc(100% - 60px);
}

/* 头部 */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 4px;
}

.header-actions .el-button {
  color: white;
}

.header-actions .el-button:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* 消息列表 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #f5f7fa;
}

/* 欢迎消息 */
.welcome-message {
  text-align: center;
  padding: 40px 20px;
  color: #606266;
}

.welcome-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 16px;
}

.welcome-message p {
  margin: 8px 0;
  font-size: 16px;
}

.welcome-tips {
  margin-top: 20px;
  font-weight: 600;
  color: #303133;
}

.welcome-list {
  list-style: none;
  padding: 0;
  margin: 12px 0;
}

.welcome-list li {
  padding: 8px 0;
  color: #606266;
}

.welcome-list li:before {
  content: "✓ ";
  color: #67c23a;
  font-weight: bold;
  margin-right: 8px;
}

/* 消息样式 */
.message {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 20px;
}

.message.user .message-avatar {
  background: #409eff;
  color: white;
}

.message.assistant .message-avatar {
  background: #67c23a;
  color: white;
}

.message-content {
  max-width: 70%;
}

.message-text {
  padding: 12px 16px;
  border-radius: 12px;
  word-wrap: break-word;
  white-space: pre-wrap;
  line-height: 1.6;
}

.message.user .message-text {
  background: #409eff;
  color: white;
  border-bottom-right-radius: 4px;
}

.message.assistant .message-text {
  background: white;
  color: #303133;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 加载动画 */
.typing {
  display: flex;
  gap: 4px;
  padding: 16px !important;
}

.typing span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #909399;
  animation: typing 1.4s infinite;
}

.typing span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
}

/* 输入框 */
.chat-input {
  padding: 16px;
  background: white;
  border-top: 1px solid #e4e7ed;
}

.chat-input :deep(.el-input-group__append) {
  padding: 0;
}

.chat-input :deep(.el-input-group__append .el-button) {
  margin: 0;
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #c0c4cc;
}

/* 响应式 */
@media (max-width: 768px) {
  .chat-widget {
    bottom: 20px;
    right: 20px;
  }

  .chat-window {
    width: calc(100vw - 40px);
    height: calc(100vh - 100px);
  }

  .chat-button {
    width: 50px;
    height: 50px;
    font-size: 24px;
  }
}
</style>
