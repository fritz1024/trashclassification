<template>
  <div class="ai-chat-page">
    <!-- 左侧对话列表 -->
    <div class="chat-sidebar">
      <!-- 顶部用户信息 -->
      <div class="sidebar-header">
        <div class="user-info">
          <el-icon class="user-avatar"><Avatar /></el-icon>
          <span class="username">{{ userStore.user?.username || '游客' }}</span>
        </div>
      </div>

      <!-- 新对话按钮 -->
      <div class="new-chat-btn">
        <el-button
          type="primary"
          :icon="Plus"
          @click="createNewChat"
          style="width: 100%"
          :disabled="!userStore.isLoggedIn"
        >
          新对话
        </el-button>
      </div>

      <!-- 未登录提示 -->
      <div v-if="!userStore.isLoggedIn" class="login-tip">
        <el-alert
          title="请先登录"
          type="info"
          description="登录后可以保存对话历史"
          :closable="false"
          show-icon
        />
      </div>

      <!-- 对话历史列表 -->
      <div class="chat-list" v-if="userStore.isLoggedIn">
        <div class="chat-list-header">
          <span>历史对话</span>
        </div>
        <div class="chat-list-items">
          <div
            v-for="chat in chatHistory"
            :key="chat.id"
            :class="['chat-item', { active: currentChatId === chat.id }]"
            @click="switchChat(chat.id)"
          >
            <el-icon class="chat-icon"><ChatDotRound /></el-icon>
            <div class="chat-info">
              <div class="chat-title">{{ chat.title }}</div>
              <div class="chat-time">{{ formatTime(chat.updated_at) }}</div>
            </div>
            <el-icon class="delete-icon" @click.stop="deleteChat(chat.id)"><Delete /></el-icon>
          </div>
          <div v-if="chatHistory.length === 0" class="empty-chat">
            <el-empty description="暂无历史对话" :image-size="80" />
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧聊天区域 -->
    <div class="chat-main">
      <!-- 聊天头部 -->
      <div class="chat-header">
        <div class="header-title">
          <el-icon><ChatDotRound /></el-icon>
          <span>AI 助手</span>
        </div>
        <div class="header-actions">
          <el-button text :icon="Delete" @click="clearCurrentChat">清空对话</el-button>
        </div>
      </div>

      <!-- 消息区域 -->
      <div class="chat-messages" ref="messagesContainer">
        <!-- 欢迎消息 -->
        <div v-if="currentMessages.length === 0" class="welcome-section">
          <div class="welcome-title">有什么我能帮你的吗？</div>

          <!-- 未登录提示 -->
          <div v-if="!userStore.isLoggedIn" class="guest-notice">
            <el-alert
              title="游客模式"
              type="warning"
              description="您当前是游客身份，请登录后使用 AI 助手功能"
              show-icon
              :closable="false"
            />
          </div>

          <!-- 快捷问题（仅登录用户可见） -->
          <div v-else class="quick-questions">
            <el-button
              v-for="(question, index) in quickQuestions"
              :key="index"
              class="question-btn"
              @click="sendQuickQuestion(question)"
            >
              {{ question }}
            </el-button>
          </div>
        </div>

        <!-- 对话消息 -->
        <div
          v-for="(msg, index) in currentMessages"
          :key="index"
          :class="['message', msg.role]"
        >
          <div class="message-avatar">
            <el-icon v-if="msg.role === 'user'"><User /></el-icon>
            <el-icon v-else><ChatDotRound /></el-icon>
          </div>
          <div class="message-content">
            <!-- 用户消息：纯文本 -->
            <div v-if="msg.role === 'user'" class="message-text">{{ msg.content }}</div>
            <!-- AI 消息：Markdown 渲染 -->
            <div v-else class="message-text markdown-body" v-html="renderMarkdown(msg.content)"></div>
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

      <!-- 输入区域 -->
      <div class="chat-input-area">
        <div class="input-wrapper">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            :placeholder="userStore.isLoggedIn ? '发消息或输入 / 选择技能' : '请先登录后使用 AI 助手'"
            @keydown.enter.exact.prevent="sendMessage"
            :disabled="loading || !userStore.isLoggedIn"
          />
          <div class="input-actions">
            <div class="action-buttons">
              <el-button text :icon="Paperclip" disabled>附件</el-button>
              <el-button text :icon="Reading" disabled>深度思考</el-button>
              <el-button text :icon="MagicStick" disabled>技能</el-button>
            </div>
            <el-button
              type="primary"
              :icon="Promotion"
              @click="sendMessage"
              :loading="loading"
              :disabled="!inputMessage.trim() || !userStore.isLoggedIn"
              circle
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { useUserStore } from '@/store/user'
import { sendMessage as sendChatMessage, getConversations, createConversation, updateConversation, deleteConversation as deleteConversationAPI } from '@/api/chat'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ChatDotRound,
  Plus,
  Delete,
  User,
  Promotion,
  Avatar,
  Paperclip,
  Reading,
  MagicStick
} from '@element-plus/icons-vue'
import MarkdownIt from 'markdown-it'

// 初始化 Markdown 渲染器
const md = new MarkdownIt({
  html: false, // 不允许 HTML 标签
  linkify: true, // 自动识别链接
  breaks: true, // 转换换行符为 <br>
  typographer: true // 启用一些语言中立的替换和引号美化
})

const userStore = useUserStore()

// 状态
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)
const currentChatId = ref(null)
const chatHistory = ref([])

// 快捷问题
const quickQuestions = [
  '塑料瓶属于什么垃圾？',
  '过期药品如何处理？',
  '厨余垃圾包括哪些？',
  '废旧电池是有害垃圾吗？',
  '纸巾是可回收物吗？',
  '如何正确分类快递包装？'
]

// 渲染 Markdown
const renderMarkdown = (content) => {
  return md.render(content)
}

// 当前对话的消息
const currentMessages = computed(() => {
  if (!currentChatId.value) return []
  const chat = chatHistory.value.find(c => c.id === currentChatId.value)
  return chat ? chat.messages : []
})

// 创建新对话
const createNewChat = async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }

  const newChat = {
    id: Date.now(), // 临时 ID
    title: '新对话',
    messages: [],
    created_at: new Date(),
    updated_at: new Date()
  }
  chatHistory.value.unshift(newChat)
  currentChatId.value = newChat.id
}

// 切换对话
const switchChat = (chatId) => {
  currentChatId.value = chatId
  scrollToBottom()
}

// 删除对话
const deleteChat = async (chatId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个对话吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // 调用后端 API 删除
    await deleteConversationAPI(chatId)

    chatHistory.value = chatHistory.value.filter(c => c.id !== chatId)

    // 如果删除的是当前对话，切换到第一个对话或创建新对话
    if (currentChatId.value === chatId) {
      if (chatHistory.value.length > 0) {
        currentChatId.value = chatHistory.value[0].id
      } else {
        createNewChat()
      }
    }

    ElMessage.success('对话已删除')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除对话失败:', error)
      ElMessage.error('删除对话失败')
    }
  }
}

// 清空当前对话
const clearCurrentChat = async () => {
  if (!currentChatId.value) return

  try {
    await ElMessageBox.confirm('确定要清空当前对话吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const chat = chatHistory.value.find(c => c.id === currentChatId.value)
    if (chat) {
      chat.messages = []
      chat.title = '新对话'
      chat.updated_at = new Date()

      // 如果对话已经保存到后端，更新它
      if (typeof chat.id === 'number' && chat.id < Date.now() - 1000000) {
        await updateConversation(chat.id, {
          title: chat.title,
          messages: chat.messages
        })
      }
    }

    ElMessage.success('对话已清空')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清空对话失败:', error)
    }
  }
}

// 发送快捷问题
const sendQuickQuestion = (question) => {
  // 检查登录状态
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后使用 AI 助手')
    return
  }

  inputMessage.value = question
  sendMessage()
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
  // 检查登录状态
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后使用 AI 助手')
    return
  }

  if (!inputMessage.value.trim() || loading.value) return

  // 如果没有当前对话，创建新对话
  if (!currentChatId.value) {
    await createNewChat()
  }

  const userMessage = inputMessage.value.trim()
  inputMessage.value = ''

  const chat = chatHistory.value.find(c => c.id === currentChatId.value)
  if (!chat) return

  // 添加用户消息
  chat.messages.push({
    role: 'user',
    content: userMessage
  })

  // 如果是第一条消息，更新对话标题
  const isFirstMessage = chat.messages.length === 1
  if (isFirstMessage) {
    chat.title = userMessage.length > 20 ? userMessage.substring(0, 20) + '...' : userMessage
  }

  chat.updated_at = new Date()
  scrollToBottom()

  // 调用API
  loading.value = true
  try {
    const response = await sendChatMessage(chat.messages)

    if (response.success) {
      // 添加AI回复
      chat.messages.push({
        role: 'assistant',
        content: response.reply
      })
      chat.updated_at = new Date()
      scrollToBottom()

      // 保存到后端
      await saveConversationToBackend(chat, isFirstMessage)
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

// 保存对话到后端
const saveConversationToBackend = async (chat, isNew) => {
  try {
    // 判断是新对话还是更新对话
    // 临时 ID 是大于当前时间戳的，后端返回的 ID 是小的
    const isTemporaryId = chat.id > Date.now() - 1000000

    if (isNew || isTemporaryId) {
      // 创建新对话
      const result = await createConversation({
        title: chat.title,
        messages: chat.messages
      })
      // 更新为后端返回的真实 ID
      const oldId = chat.id
      chat.id = result.id
      chat.created_at = result.created_at
      chat.updated_at = result.updated_at

      // 更新 currentChatId
      if (currentChatId.value === oldId) {
        currentChatId.value = result.id
      }
    } else {
      // 更新现有对话
      await updateConversation(chat.id, {
        title: chat.title,
        messages: chat.messages
      })
    }
  } catch (error) {
    console.error('保存对话失败:', error)
    // 不显示错误提示，避免打断用户体验
  }
}

// 格式化时间
const formatTime = (date) => {
  const now = new Date()
  const diff = now - new Date(date)
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`

  const d = new Date(date)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

// 从后端加载聊天历史
const loadChatHistory = async () => {
  if (!userStore.isLoggedIn) {
    // 未登录时，创建一个空的新对话
    chatHistory.value = []
    currentChatId.value = null
    return
  }

  try {
    const conversations = await getConversations()
    chatHistory.value = conversations

    // 如果有历史对话，选中第一个
    if (chatHistory.value.length > 0) {
      currentChatId.value = chatHistory.value[0].id
    } else {
      // 如果没有历史对话，创建一个新对话
      createNewChat()
    }
  } catch (error) {
    console.error('加载聊天历史失败:', error)
    // 加载失败时，创建一个新对话
    chatHistory.value = []
    createNewChat()
  }
}

// 组件挂载时加载历史
onMounted(() => {
  loadChatHistory()
})

// 监听用户登录状态变化
watch(() => userStore.isLoggedIn, (newValue, oldValue) => {
  // 如果从登录状态变为未登录状态（退出登录）
  if (oldValue === true && newValue === false) {
    // 清除聊天历史
    chatHistory.value = []
    currentChatId.value = null
    console.log('用户退出登录，已清除聊天历史')
  }
  // 如果从未登录变为登录状态
  else if (oldValue === false && newValue === true) {
    // 重新加载聊天历史
    loadChatHistory()
  }
})
</script>

<style scoped>
.ai-chat-page {
  display: flex;
  height: calc(100vh - 120px);
  background: #f5f7fa;
  border-radius: 8px;
  overflow: hidden;
}

/* 左侧边栏 */
.chat-sidebar {
  width: 280px;
  background: white;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.username {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.new-chat-btn {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.login-tip {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.login-tip :deep(.el-alert) {
  padding: 12px;
}

.login-tip :deep(.el-alert__title) {
  font-size: 14px;
}

.login-tip :deep(.el-alert__description) {
  font-size: 12px;
  margin-top: 4px;
}

.chat-list {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.chat-list-header {
  padding: 12px 16px;
  font-size: 14px;
  color: #909399;
  font-weight: 600;
}

.chat-list-items {
  flex: 1;
  overflow-y: auto;
  padding: 0 8px;
}

.chat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  margin-bottom: 4px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.chat-item:hover {
  background: #f5f7fa;
}

.chat-item.active {
  background: #ecf5ff;
}

.chat-icon {
  font-size: 20px;
  color: #409eff;
  flex-shrink: 0;
}

.chat-info {
  flex: 1;
  min-width: 0;
}

.chat-title {
  font-size: 14px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chat-time {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.delete-icon {
  font-size: 16px;
  color: #909399;
  opacity: 0;
  transition: opacity 0.3s;
}

.chat-item:hover .delete-icon {
  opacity: 1;
}

.delete-icon:hover {
  color: #f56c6c;
}

.empty-chat {
  padding: 40px 20px;
  text-align: center;
}

/* 右侧聊天区域 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #e4e7ed;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

/* 欢迎区域 */
.welcome-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 40px;
}

.welcome-title {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 40px;
}

.guest-notice {
  max-width: 500px;
  margin: 0 auto;
}

.guest-notice :deep(.el-alert) {
  padding: 20px;
}

.guest-notice :deep(.el-alert__title) {
  font-size: 16px;
  font-weight: 600;
}

.guest-notice :deep(.el-alert__description) {
  font-size: 14px;
  margin-top: 8px;
}

.quick-questions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  max-width: 900px;
}

.question-btn {
  padding: 16px 20px;
  height: auto;
  white-space: normal;
  text-align: left;
  line-height: 1.5;
  border: 1px solid #e4e7ed;
  background: #f5f7fa;
  color: #606266;
}

.question-btn:hover {
  border-color: #409eff;
  color: #409eff;
  background: #ecf5ff;
}

/* 消息样式 */
.message {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
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
  font-size: 15px;
}

.message.user .message-text {
  background: #409eff;
  color: white;
  border-bottom-right-radius: 4px;
}

.message.assistant .message-text {
  background: #f5f7fa;
  color: #303133;
  border-bottom-left-radius: 4px;
}

/* Markdown 样式 */
.markdown-body {
  font-size: 15px;
  line-height: 1.6;
}

.markdown-body p {
  margin: 0 0 8px 0;
}

.markdown-body p:last-child {
  margin-bottom: 0;
}

.markdown-body strong {
  font-weight: 600;
  color: #303133;
}

.markdown-body em {
  font-style: italic;
}

.markdown-body code {
  background: #e6e8eb;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  color: #e83e8c;
}

.markdown-body pre {
  background: #282c34;
  color: #abb2bf;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 8px 0;
}

.markdown-body pre code {
  background: transparent;
  padding: 0;
  color: inherit;
  font-size: 13px;
}

.markdown-body ul,
.markdown-body ol {
  margin: 8px 0;
  padding-left: 24px;
}

.markdown-body li {
  margin: 4px 0;
}

.markdown-body blockquote {
  border-left: 4px solid #409eff;
  padding-left: 12px;
  margin: 8px 0;
  color: #606266;
}

.markdown-body a {
  color: #409eff;
  text-decoration: none;
}

.markdown-body a:hover {
  text-decoration: underline;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4,
.markdown-body h5,
.markdown-body h6 {
  margin: 12px 0 8px 0;
  font-weight: 600;
  color: #303133;
}

.markdown-body h1 {
  font-size: 20px;
}

.markdown-body h2 {
  font-size: 18px;
}

.markdown-body h3 {
  font-size: 16px;
}

.markdown-body table {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
}

.markdown-body th,
.markdown-body td {
  border: 1px solid #dcdfe6;
  padding: 8px 12px;
  text-align: left;
}

.markdown-body th {
  background: #f5f7fa;
  font-weight: 600;
}

.markdown-body hr {
  border: none;
  border-top: 1px solid #dcdfe6;
  margin: 12px 0;
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

/* 输入区域 */
.chat-input-area {
  padding: 16px 24px 24px;
  border-top: 1px solid #e4e7ed;
}

.input-wrapper {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 12px;
}

.input-wrapper :deep(.el-textarea__inner) {
  background: transparent;
  border: none;
  box-shadow: none;
  resize: none;
  font-size: 15px;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

/* 滚动条样式 */
.chat-list-items::-webkit-scrollbar,
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-list-items::-webkit-scrollbar-thumb,
.chat-messages::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 3px;
}

.chat-list-items::-webkit-scrollbar-thumb:hover,
.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #c0c4cc;
}

/* 响应式 */
@media (max-width: 768px) {
  .chat-sidebar {
    width: 240px;
  }

  .quick-questions {
    grid-template-columns: repeat(2, 1fr);
  }

  .message-content {
    max-width: 85%;
  }
}
</style>
