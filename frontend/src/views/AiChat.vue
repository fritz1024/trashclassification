<template>
  <div class="ai-chat-page">
    <!-- Sidebar -->
    <aside class="chat-sidebar">
      <div class="sidebar-top">
        <div class="sidebar-user">
          <img v-if="userStore.user?.avatar" :src="'/' + userStore.user.avatar" class="sidebar-avatar sidebar-avatar-img" />
          <div v-else class="sidebar-avatar">
            <el-icon :size="18"><User /></el-icon>
          </div>
          <span>{{ userStore.user?.username || '游客' }}</span>
        </div>
        <el-button type="primary" round :icon="Plus" @click="createNewChat" :disabled="!userStore.isLoggedIn" class="new-chat-btn">新对话</el-button>
      </div>

      <div v-if="!userStore.isLoggedIn" class="sidebar-notice">
        <el-icon :size="16"><InfoFilled /></el-icon>
        <span>登录后可保存对话历史</span>
      </div>

      <div class="chat-list" v-if="userStore.isLoggedIn">
        <span class="chat-list-label">历史对话</span>
        <div class="chat-list-scroll">
          <div v-for="chat in chatHistory" :key="chat.id" :class="['chat-item', { active: currentChatId === chat.id }]" @click="switchChat(chat.id)">
            <el-icon class="chat-item-icon"><ChatDotRound /></el-icon>
            <div class="chat-item-info">
              <span class="chat-item-title">{{ chat.title }}</span>
              <span class="chat-item-time">{{ formatTime(chat.updated_at) }}</span>
            </div>
            <el-icon class="chat-item-del" @click.stop="deleteChat(chat.id)"><Delete /></el-icon>
          </div>
          <div v-if="chatHistory.length === 0" class="chat-list-empty">
            <el-icon :size="32" color="var(--text-tertiary)"><ChatDotRound /></el-icon>
            <span>暂无历史对话</span>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Chat -->
    <div class="chat-main">
      <div class="chat-topbar">
        <div class="topbar-title">
          <el-icon><ChatDotRound /></el-icon>
          <span>AI 助手</span>
        </div>
        <el-button text size="small" :icon="Delete" @click="clearCurrentChat">清空</el-button>
      </div>

      <div class="chat-messages" ref="messagesContainer">
        <!-- Welcome -->
        <div v-if="currentMessages.length === 0" class="welcome">
          <h2>有什么我能帮你的吗？</h2>
          <div v-if="!userStore.isLoggedIn" class="guest-alert">
            <el-alert type="warning" :closable="false" show-icon>
              <template #title>游客模式</template>
              <template #default>请登录后使用 AI 助手功能</template>
            </el-alert>
          </div>
          <div v-else class="quick-grid">
            <button v-for="(q, i) in quickQuestions" :key="i" class="quick-btn" @click="sendQuickQuestion(q)">{{ q }}</button>
          </div>
        </div>

        <!-- Messages -->
        <div v-for="(msg, index) in currentMessages" :key="index" :class="['msg', msg.role]">
          <div class="msg-avatar">
            <el-icon v-if="msg.role === 'user'" :size="16"><User /></el-icon>
            <el-icon v-else :size="16"><ChatDotRound /></el-icon>
          </div>
          <div class="msg-bubble">
            <div v-if="msg.role === 'user'">{{ msg.content }}</div>
            <div v-else class="md-body" v-html="renderMarkdown(msg.content)"></div>
          </div>
        </div>

        <!-- Typing -->
        <div v-if="loading" class="msg assistant">
          <div class="msg-avatar"><el-icon :size="16"><ChatDotRound /></el-icon></div>
          <div class="msg-bubble">
            <div class="typing-dots"><span></span><span></span><span></span></div>
          </div>
        </div>
      </div>

      <!-- Input -->
      <div class="chat-input">
        <div class="input-box">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="2"
            :placeholder="userStore.isLoggedIn ? '输入消息，Enter 发送...' : '请先登录'"
            @keydown.enter.exact.prevent="sendMessage"
            :disabled="loading || !userStore.isLoggedIn"
            resize="none"
          />
          <el-button type="primary" :icon="Promotion" @click="sendMessage" :loading="loading" :disabled="!inputMessage.trim() || !userStore.isLoggedIn" circle class="send-btn" />
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
import { ChatDotRound, Plus, Delete, User, Promotion, InfoFilled } from '@element-plus/icons-vue'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({ html: false, linkify: true, breaks: true, typographer: true })
const userStore = useUserStore()
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)
const currentChatId = ref(null)
const chatHistory = ref([])

const quickQuestions = ['塑料瓶属于什么垃圾？', '过期药品如何处理？', '厨余垃圾包括哪些？', '废旧电池是有害垃圾吗？', '纸巾是可回收物吗？', '如何正确分类快递包装？']

const renderMarkdown = (content) => md.render(content)
const currentMessages = computed(() => {
  if (!currentChatId.value) return []
  const chat = chatHistory.value.find(c => c.id === currentChatId.value)
  return chat ? chat.messages : []
})

const createNewChat = async () => {
  if (!userStore.isLoggedIn) { ElMessage.warning('请先登录'); return }
  const newChat = { id: Date.now(), title: '新对话', messages: [], created_at: new Date(), updated_at: new Date() }
  chatHistory.value.unshift(newChat)
  currentChatId.value = newChat.id
}

const switchChat = (chatId) => { currentChatId.value = chatId; scrollToBottom() }

const deleteChat = async (chatId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个对话吗？', '提示', { type: 'warning' })
    await deleteConversationAPI(chatId)
    chatHistory.value = chatHistory.value.filter(c => c.id !== chatId)
    if (currentChatId.value === chatId) {
      currentChatId.value = chatHistory.value.length > 0 ? chatHistory.value[0].id : null
      if (!currentChatId.value) createNewChat()
    }
    ElMessage.success('对话已删除')
  } catch (error) { if (error !== 'cancel') ElMessage.error('删除对话失败') }
}

const clearCurrentChat = async () => {
  if (!currentChatId.value) return
  try {
    await ElMessageBox.confirm('确定要清空当前对话吗？', '提示', { type: 'warning' })
    const chat = chatHistory.value.find(c => c.id === currentChatId.value)
    if (chat) {
      chat.messages = []
      chat.title = '新对话'
      chat.updated_at = new Date()
      if (typeof chat.id === 'number' && chat.id < Date.now() - 1000000) {
        await updateConversation(chat.id, { title: chat.title, messages: chat.messages })
      }
    }
    ElMessage.success('对话已清空')
  } catch (error) { /* cancel */ }
}

const sendQuickQuestion = (question) => {
  if (!userStore.isLoggedIn) { ElMessage.warning('请先登录'); return }
  inputMessage.value = question
  sendMessage()
}

const scrollToBottom = () => { nextTick(() => { if (messagesContainer.value) messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight }) }

const sendMessage = async () => {
  if (!userStore.isLoggedIn) { ElMessage.warning('请先登录'); return }
  if (!inputMessage.value.trim() || loading.value) return
  if (!currentChatId.value) await createNewChat()
  const userMsg = inputMessage.value.trim()
  inputMessage.value = ''
  const chat = chatHistory.value.find(c => c.id === currentChatId.value)
  if (!chat) return
  chat.messages.push({ role: 'user', content: userMsg })
  const isFirst = chat.messages.length === 1
  if (isFirst) chat.title = userMsg.length > 20 ? userMsg.substring(0, 20) + '...' : userMsg
  chat.updated_at = new Date()
  scrollToBottom()
  loading.value = true
  try {
    const response = await sendChatMessage(chat.messages)
    if (response.success) {
      chat.messages.push({ role: 'assistant', content: response.reply })
      chat.updated_at = new Date()
      scrollToBottom()
      await saveConversationToBackend(chat, isFirst)
    } else {
      ElMessage.error(response.error || 'AI 服务暂时不可用')
    }
  } catch (error) {
    ElMessage.error('发送消息失败')
  } finally { loading.value = false }
}

const saveConversationToBackend = async (chat, isNew) => {
  try {
    const isTemporaryId = chat.id > Date.now() - 1000000
    if (isNew || isTemporaryId) {
      const result = await createConversation({ title: chat.title, messages: chat.messages })
      const oldId = chat.id
      chat.id = result.id; chat.created_at = result.created_at; chat.updated_at = result.updated_at
      if (currentChatId.value === oldId) currentChatId.value = result.id
    } else {
      await updateConversation(chat.id, { title: chat.title, messages: chat.messages })
    }
  } catch (error) { /* silent */ }
}

const formatTime = (date) => {
  const diff = Date.now() - new Date(date)
  const m = Math.floor(diff / 60000), h = Math.floor(diff / 3600000), d = Math.floor(diff / 86400000)
  if (m < 1) return '刚刚'
  if (m < 60) return `${m}分钟前`
  if (h < 24) return `${h}小时前`
  if (d < 7) return `${d}天前`
  const dt = new Date(date); return `${dt.getMonth() + 1}/${dt.getDate()}`
}

const loadChatHistory = async () => {
  if (!userStore.isLoggedIn) { chatHistory.value = []; currentChatId.value = null; return }
  try {
    const conversations = await getConversations()
    chatHistory.value = conversations
    currentChatId.value = chatHistory.value.length > 0 ? chatHistory.value[0].id : null
    if (!currentChatId.value) createNewChat()
  } catch (error) { chatHistory.value = []; createNewChat() }
}

onMounted(() => loadChatHistory())
watch(() => userStore.isLoggedIn, (n, o) => {
  if (o && !n) { chatHistory.value = []; currentChatId.value = null }
  else if (!o && n) loadChatHistory()
})
</script>

<style scoped>
.ai-chat-page {
  display: flex;
  height: calc(100vh - var(--navbar-height) - 60px);
  background: var(--bg-primary);
  margin: var(--space-4) auto;
  max-width: 1200px;
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-md);
}

/* Sidebar */
.chat-sidebar {
  width: 280px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-secondary);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-top {
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  border-bottom: 1px solid var(--border-secondary);
}

.sidebar-user {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-weight: var(--font-semibold);
  font-size: var(--text-base);
  color: var(--text-primary);
}

.sidebar-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.sidebar-avatar-img {
  object-fit: cover;
  background: none;
}

.new-chat-btn { width: 100%; }

.sidebar-notice {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  border-bottom: 1px solid var(--border-secondary);
}

.chat-list {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.chat-list-label {
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.chat-list-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 0 var(--space-2);
}

.chat-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  margin-bottom: 2px;
}

.chat-item:hover { background: var(--bg-hover); }
.chat-item.active { background: var(--color-primary-lightest); }

.chat-item-icon { color: var(--color-primary); flex-shrink: 0; font-size: 18px; }
.chat-item-info { flex: 1; min-width: 0; }
.chat-item-title { display: block; font-size: var(--text-sm); color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.chat-item-time { display: block; font-size: var(--text-xs); color: var(--text-tertiary); margin-top: 2px; }
.chat-item-del { font-size: 14px; color: var(--text-tertiary); opacity: 0; transition: all var(--transition-fast); flex-shrink: 0; }
.chat-item:hover .chat-item-del { opacity: 1; }
.chat-item-del:hover { color: var(--color-danger); }

.chat-list-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-10);
  color: var(--text-tertiary);
  font-size: var(--text-sm);
}

/* Main */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  min-width: 0;
}

.chat-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--border-secondary);
}

.topbar-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-6);
}

/* Welcome */
.welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: var(--space-8);
}

.welcome h2 {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin-bottom: var(--space-8);
}

.guest-alert { max-width: 400px; }

.quick-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
  max-width: 720px;
}

.quick-btn {
  padding: var(--space-4);
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  text-align: left;
  cursor: pointer;
  transition: all var(--transition-fast);
  line-height: var(--leading-normal);
}

.quick-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: var(--bg-hover);
}

/* Messages */
.msg {
  display: flex;
  gap: var(--space-3);
  margin-bottom: var(--space-5);
  animation: msgIn 0.25s ease;
}

@keyframes msgIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.msg.user { flex-direction: row-reverse; }

.msg-avatar {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: white;
}

.msg.user .msg-avatar { background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark)); }
.msg.assistant .msg-avatar { background: linear-gradient(135deg, var(--color-accent), #7c3aed); }

.msg-bubble {
  max-width: 70%;
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  font-size: var(--text-base);
  line-height: var(--leading-relaxed);
  word-wrap: break-word;
  white-space: pre-wrap;
}

.msg.user .msg-bubble {
  background: var(--color-primary);
  color: white;
  border-bottom-right-radius: var(--radius-xs);
}

.msg.assistant .msg-bubble {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-bottom-left-radius: var(--radius-xs);
}

/* Markdown */
.md-body :deep(p) { margin: 0 0 var(--space-2); }
.md-body :deep(p:last-child) { margin-bottom: 0; }
.md-body :deep(strong) { font-weight: var(--font-semibold); }
.md-body :deep(code) { background: var(--bg-tertiary); padding: 1px 5px; border-radius: var(--radius-xs); font-family: var(--font-mono); font-size: var(--text-sm); }
.md-body :deep(pre) { background: #1e293b; color: #e2e8f0; padding: var(--space-3); border-radius: var(--radius-sm); overflow-x: auto; margin: var(--space-2) 0; }
.md-body :deep(pre code) { background: transparent; padding: 0; color: inherit; }
.md-body :deep(ul), .md-body :deep(ol) { margin: var(--space-2) 0; padding-left: var(--space-6); }
.md-body :deep(li) { margin: var(--space-1) 0; }
.md-body :deep(blockquote) { border-left: 3px solid var(--color-primary); padding-left: var(--space-3); margin: var(--space-2) 0; color: var(--text-secondary); }
.md-body :deep(a) { color: var(--color-primary); }
.md-body :deep(h1), .md-body :deep(h2), .md-body :deep(h3) { margin: var(--space-3) 0 var(--space-2); font-weight: var(--font-semibold); }
.md-body :deep(table) { border-collapse: collapse; width: 100%; margin: var(--space-2) 0; }
.md-body :deep(th), .md-body :deep(td) { border: 1px solid var(--border-primary); padding: var(--space-2) var(--space-3); }
.md-body :deep(th) { background: var(--bg-tertiary); font-weight: var(--font-semibold); }

/* Typing dots */
.typing-dots { display: flex; gap: 4px; padding: var(--space-2) 0; }
.typing-dots span { width: 7px; height: 7px; border-radius: 50%; background: var(--text-tertiary); animation: bounce 1.4s infinite; }
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%, 60%, 100% { transform: translateY(0); } 30% { transform: translateY(-8px); } }

/* Input */
.chat-input {
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--border-secondary);
}

.input-box {
  display: flex;
  align-items: flex-end;
  gap: var(--space-3);
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  padding: var(--space-3);
  border: 1px solid var(--border-primary);
  transition: border-color var(--transition-fast);
}

.input-box:focus-within {
  border-color: var(--color-primary);
}

.input-box :deep(.el-textarea__inner) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  resize: none;
  font-size: var(--text-base);
  padding: var(--space-1) var(--space-2);
}

.send-btn {
  flex-shrink: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .ai-chat-page { margin: 0; border-radius: 0; border: none; height: calc(100vh - var(--navbar-height)); }
  .chat-sidebar { width: 220px; }
  .quick-grid { grid-template-columns: repeat(2, 1fr); }
  .msg-bubble { max-width: 85%; }
}

@media (max-width: 640px) {
  .chat-sidebar { display: none; }
}
</style>
