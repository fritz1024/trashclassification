<template>
  <div class="chat-widget">
    <!-- Float Button -->
    <Transition name="bounce">
      <button v-if="!isOpen" class="chat-fab" @click="toggleChat">
        <el-icon :size="24"><ChatDotRound /></el-icon>
      </button>
    </Transition>

    <!-- Chat Window -->
    <Transition name="chat-pop">
      <div v-if="isOpen" class="chat-window glass-heavy">
        <div class="cw-header">
          <div class="cw-title">
            <div class="cw-avatar"><el-icon :size="16"><ChatDotRound /></el-icon></div>
            <span>AI 助手</span>
          </div>
          <div class="cw-actions">
            <button @click="clearChat" title="清空"><el-icon :size="16"><Delete /></el-icon></button>
            <button @click="toggleChat" title="关闭"><el-icon :size="16"><Close /></el-icon></button>
          </div>
        </div>

        <div class="cw-messages" ref="messagesContainer">
          <div v-if="messages.length === 0" class="cw-welcome">
            <div class="cw-welcome-icon"><el-icon :size="28"><ChatDotRound /></el-icon></div>
            <p class="cw-welcome-title">你好！我是垃圾分类 AI 助手</p>
            <div class="cw-welcome-list">
              <span>解答垃圾分类问题</span>
              <span>解释识别结果</span>
              <span>提供环保建议</span>
            </div>
          </div>

          <div v-for="(msg, index) in messages" :key="index" :class="['cw-msg', msg.role]">
            <div class="cw-msg-avatar">
              <el-icon v-if="msg.role === 'user'" :size="14"><User /></el-icon>
              <el-icon v-else :size="14"><ChatDotRound /></el-icon>
            </div>
            <div class="cw-msg-bubble">{{ msg.content }}</div>
          </div>

          <div v-if="loading" class="cw-msg assistant">
            <div class="cw-msg-avatar"><el-icon :size="14"><ChatDotRound /></el-icon></div>
            <div class="cw-msg-bubble"><div class="cw-typing"><span></span><span></span><span></span></div></div>
          </div>
        </div>

        <div class="cw-input">
          <input v-model="inputMessage" placeholder="输入消息..." @keyup.enter="sendMessage" :disabled="loading" />
          <button class="cw-send" @click="sendMessage" :disabled="!inputMessage.trim() || loading">
            <el-icon :size="16"><Promotion /></el-icon>
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { ChatDotRound, Close, Delete, User, Promotion } from '@element-plus/icons-vue'
import { sendMessage as sendChatMessage } from '../api/chat'
import { ElMessage } from 'element-plus'

const isOpen = ref(false)
const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)

const toggleChat = () => { isOpen.value = !isOpen.value }
const clearChat = () => { messages.value = []; ElMessage.success('对话已清空') }
const scrollToBottom = () => { nextTick(() => { if (messagesContainer.value) messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight }) }

const sendMessage = async () => {
  if (!inputMessage.value.trim() || loading.value) return
  const userMessage = inputMessage.value.trim()
  inputMessage.value = ''
  messages.value.push({ role: 'user', content: userMessage })
  scrollToBottom()
  loading.value = true
  try {
    const response = await sendChatMessage(messages.value)
    if (response.success) {
      messages.value.push({ role: 'assistant', content: response.reply })
      scrollToBottom()
    } else {
      ElMessage.error(response.error || 'AI 服务暂时不可用')
    }
  } catch (error) {
    ElMessage.error('发送消息失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {})
</script>

<style scoped>
.chat-widget {
  position: fixed;
  bottom: var(--space-8);
  right: var(--space-8);
  z-index: var(--z-popover);
}

/* FAB */
.chat-fab {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(16, 185, 129, 0.35);
  transition: all var(--transition-normal);
}

.chat-fab:hover {
  transform: scale(1.08);
  box-shadow: 0 6px 24px rgba(16, 185, 129, 0.45);
}

/* Window */
.chat-window {
  width: 380px;
  height: 560px;
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-secondary);
  box-shadow: var(--shadow-xl);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Header */
.cw-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4);
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  color: white;
}

.cw-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-weight: var(--font-semibold);
  font-size: var(--text-md);
}

.cw-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(255,255,255,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.cw-actions {
  display: flex;
  gap: var(--space-1);
}

.cw-actions button {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  color: rgba(255,255,255,0.8);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.cw-actions button:hover {
  background: rgba(255,255,255,0.2);
  color: white;
}

/* Messages */
.cw-messages {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-4);
  background: var(--bg-secondary);
}

/* Welcome */
.cw-welcome {
  text-align: center;
  padding: var(--space-8) var(--space-4);
}

.cw-welcome-icon {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: var(--color-primary-lightest);
  color: var(--color-primary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-4);
}

.cw-welcome-title {
  font-size: var(--text-md);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-bottom: var(--space-4);
}

.cw-welcome-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.cw-welcome-list span {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.cw-welcome-list span::before {
  content: "✓ ";
  color: var(--color-primary);
  font-weight: bold;
}

/* Message */
.cw-msg {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
  animation: msgFade 0.2s ease;
}

@keyframes msgFade {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

.cw-msg.user { flex-direction: row-reverse; }

.cw-msg-avatar {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: white;
}

.cw-msg.user .cw-msg-avatar { background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark)); }
.cw-msg.assistant .cw-msg-avatar { background: linear-gradient(135deg, var(--color-accent), #7c3aed); }

.cw-msg-bubble {
  max-width: 75%;
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
  word-wrap: break-word;
  white-space: pre-wrap;
}

.cw-msg.user .cw-msg-bubble {
  background: var(--color-primary);
  color: white;
  border-bottom-right-radius: var(--radius-xs);
}

.cw-msg.assistant .cw-msg-bubble {
  background: var(--bg-elevated);
  color: var(--text-primary);
  border-bottom-left-radius: var(--radius-xs);
  box-shadow: var(--shadow-xs);
}

/* Typing */
.cw-typing { display: flex; gap: 3px; padding: var(--space-1) 0; }
.cw-typing span { width: 6px; height: 6px; border-radius: 50%; background: var(--text-tertiary); animation: cwBounce 1.4s infinite; }
.cw-typing span:nth-child(2) { animation-delay: 0.2s; }
.cw-typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes cwBounce { 0%, 60%, 100% { transform: translateY(0); } 30% { transform: translateY(-6px); } }

/* Input */
.cw-input {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3);
  border-top: 1px solid var(--border-secondary);
  background: var(--bg-primary);
}

.cw-input input {
  flex: 1;
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  background: var(--bg-primary);
  color: var(--text-primary);
  outline: none;
  transition: border-color var(--transition-fast);
}

.cw-input input:focus {
  border-color: var(--color-primary);
}

.cw-send {
  width: 34px;
  height: 34px;
  border: none;
  border-radius: var(--radius-sm);
  background: var(--color-primary);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.cw-send:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.cw-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Transitions */
.chat-pop-enter-active { animation: popIn 0.25s ease; }
.chat-pop-leave-active { animation: popIn 0.2s ease reverse; }
@keyframes popIn {
  from { opacity: 0; transform: scale(0.9) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

.bounce-enter-active { animation: bounceIn 0.3s ease; }
@keyframes bounceIn {
  from { opacity: 0; transform: scale(0.5); }
  50% { transform: scale(1.1); }
  to { opacity: 1; transform: scale(1); }
}

/* Responsive */
@media (max-width: 768px) {
  .chat-widget { bottom: var(--space-5); right: var(--space-5); }
  .chat-window { width: calc(100vw - 40px); height: calc(100vh - 120px); }
  .chat-fab { width: 48px; height: 48px; }
}
</style>
