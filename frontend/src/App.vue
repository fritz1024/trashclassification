<template>
  <div id="app">
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header>
        <div class="header-content">
          <div class="logo">
            <el-icon><Delete /></el-icon>
            <span>垃圾分类识别系统</span>
          </div>
          <el-menu
            mode="horizontal"
            :default-active="activeMenu"
            router
            class="nav-menu"
          >
            <el-menu-item index="/">首页</el-menu-item>
            <el-menu-item index="/classify">智能识别</el-menu-item>
            <el-menu-item index="/ai-chat">AI 助手</el-menu-item>
            <el-menu-item index="/history" v-if="userStore.isLoggedIn">识别历史</el-menu-item>
            <el-menu-item index="/stats" v-if="userStore.isLoggedIn">数据统计</el-menu-item>
            <el-sub-menu index="admin" v-if="userStore.isLoggedIn && userStore.user?.role === 'admin'">
              <template #title>管理后台</template>
              <el-menu-item index="/admin/dashboard">数据概览</el-menu-item>
              <el-menu-item index="/admin/predictions">识别记录</el-menu-item>
              <el-menu-item index="/admin/users">用户管理</el-menu-item>
              <el-menu-item index="/admin/feedbacks">反馈管理</el-menu-item>
              <el-menu-item index="/admin/model">模型管理</el-menu-item>
              <el-menu-item index="/admin/announcements">公告管理</el-menu-item>
            </el-sub-menu>
          </el-menu>
          <div class="user-actions">
            <template v-if="!userStore.isLoggedIn">
              <el-button @click="$router.push('/login')">登录</el-button>
              <el-button type="success" @click="$router.push('/login')">注册</el-button>
            </template>
            <template v-else>
              <el-dropdown>
                <span class="user-info">
                  <el-icon><User /></el-icon>
                  {{ userStore.user?.username || '用户' }}
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="$router.push('/profile')">个人中心</el-dropdown-item>
                    <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </div>
        </div>
      </el-header>

      <!-- 主内容区 -->
      <el-main>
        <router-view />
      </el-main>

      <!-- 底部 -->
      <el-footer>
        <div class="footer-content">
          <p>&copy; 2025 垃圾分类识别系统 | 基于 MobileNetV2 深度学习模型</p>
        </div>
      </el-footer>
    </el-container>

    <!-- AI 聊天助手悬浮窗口（在 AI 助手页面隐藏） -->
    <ChatWidget v-if="route.path !== '/ai-chat'" />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { useThemeStore } from '@/store/theme'
import { ElMessage } from 'element-plus'
import ChatWidget from '@/components/ChatWidget.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const themeStore = useThemeStore()

const activeMenu = computed(() => route.path)

onMounted(async () => {
  themeStore.initTheme()

  if (userStore.token && !userStore.user) {
    try {
      await userStore.fetchCurrentUser()
    } catch (error) {
      console.error('获取用户信息失败:', error)
      userStore.logout()
    }
  }
})

const handleLogout = () => {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/')
}
</script>

<style scoped>
#app {
  min-height: 100vh;
  background-color: var(--theme-main-bg);
  color: var(--theme-text-color);
  margin: 0;
  padding: 0;
}

.el-container {
  margin: 0;
  padding: 0;
}

.el-header {
  background-color: var(--theme-header-bg);
  color: var(--theme-header-text);
  padding: 0;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: bold;
  color: var(--theme-header-text);
}

.nav-menu {
  flex: 1;
  background-color: transparent !important;
  border: none !important;
  margin: 0 40px;
}

.nav-menu :deep(.el-menu-item),
.nav-menu :deep(.el-sub-menu__title) {
  color: var(--theme-header-text) !important;
  border-bottom: none !important;
  background-color: transparent !important;
}

.nav-menu :deep(.el-menu-item:hover),
.nav-menu :deep(.el-menu-item.is-active),
.nav-menu :deep(.el-sub-menu__title:hover) {
  background-color: var(--theme-menu-active-bg) !important;
  color: var(--theme-header-text) !important;
}

.nav-menu :deep(.el-sub-menu.is-active .el-sub-menu__title) {
  background-color: var(--theme-menu-active-bg) !important;
  color: var(--theme-header-text) !important;
}

.user-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
  color: var(--theme-header-text);
}

.user-info:hover {
  background-color: var(--theme-menu-active-bg);
}

.el-main {
  min-height: calc(100vh - 120px);
  background-color: var(--theme-main-bg);
  padding: 0;
}

.el-footer {
  background-color: var(--theme-footer-bg);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.footer-content {
  text-align: center;
}

/* 暗黑模式下的对话框样式 */
:deep(.el-dialog) {
  background-color: var(--theme-card-bg);
  color: var(--theme-text-color);
}

:deep(.el-dialog__header) {
  border-bottom: 1px solid rgba(128, 128, 128, 0.2);
}

:deep(.el-form-item__label) {
  color: var(--theme-text-color);
}

:deep(.el-input__wrapper) {
  background-color: var(--theme-main-bg);
}

:deep(.el-input__inner) {
  color: var(--theme-text-color);
}
</style>
