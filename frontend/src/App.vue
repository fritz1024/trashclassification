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
            <el-menu-item index="/knowledge">知识科普</el-menu-item>
            <el-menu-item index="/history" v-if="userStore.isLoggedIn">识别历史</el-menu-item>
            <el-menu-item index="/stats" v-if="userStore.isLoggedIn">数据统计</el-menu-item>
            <el-sub-menu index="admin" v-if="userStore.isLoggedIn && userStore.user?.role === 'admin'">
              <template #title>管理后台</template>
              <el-menu-item index="/admin/dashboard">数据概览</el-menu-item>
              <el-menu-item index="/admin/predictions">识别记录</el-menu-item>
              <el-menu-item index="/admin/users">用户管理</el-menu-item>
              <el-menu-item index="/admin/feedbacks">反馈管理</el-menu-item>
              <el-menu-item index="/admin/knowledge">知识库管理</el-menu-item>
            </el-sub-menu>
          </el-menu>
          <div class="user-actions">
            <template v-if="!userStore.isLoggedIn">
              <el-button @click="showLogin = true">登录</el-button>
              <el-button type="primary" @click="showRegister = true">注册</el-button>
            </template>
            <template v-else>
              <el-dropdown class="theme-dropdown">
                <el-button circle>
                  <el-icon><Brush /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item
                      v-for="(theme, key) in themeStore.themes"
                      :key="key"
                      @click="themeStore.setTheme(key)"
                    >
                      <span :style="{ color: theme.primary }">●</span> {{ theme.name }}
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
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

    <!-- 登录对话框 -->
    <el-dialog v-model="showLogin" title="用户登录" width="400px">
      <el-form :model="loginForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="loginForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input
            v-model="loginForm.password"
            :type="loginPasswordVisible ? 'text' : 'password'"
            placeholder="请输入密码"
          >
            <template #suffix>
              <el-icon @click="loginPasswordVisible = !loginPasswordVisible" style="cursor: pointer;">
                <View v-if="!loginPasswordVisible" />
                <Hide v-else />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showLogin = false">取消</el-button>
        <el-button type="primary" @click="handleLogin" :loading="loginLoading">登录</el-button>
      </template>
    </el-dialog>

    <!-- 注册对话框 -->
    <el-dialog v-model="showRegister" title="用户注册" width="400px">
      <el-form :model="registerForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="registerForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="registerForm.email" placeholder="请输入邮箱（可选）" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input
            v-model="registerForm.password"
            :type="registerPasswordVisible ? 'text' : 'password'"
            placeholder="请输入密码"
          >
            <template #suffix>
              <el-icon @click="registerPasswordVisible = !registerPasswordVisible" style="cursor: pointer;">
                <View v-if="!registerPasswordVisible" />
                <Hide v-else />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRegister = false">取消</el-button>
        <el-button type="primary" @click="handleRegister" :loading="registerLoading">注册</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { useThemeStore } from '@/store/theme'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const themeStore = useThemeStore()

const activeMenu = computed(() => route.path)

// 页面加载时，如果有 token，自动获取用户信息
onMounted(async () => {
  // 初始化主题
  themeStore.initTheme()

  if (userStore.token && !userStore.user) {
    try {
      await userStore.fetchCurrentUser()
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // 如果获取失败，清除 token
      userStore.logout()
    }
  }
})

// 登录相关
const showLogin = ref(false)
const loginForm = ref({
  username: '',
  password: ''
})
const loginLoading = ref(false)
const loginPasswordVisible = ref(false)

// 注册相关
const showRegister = ref(false)
const registerForm = ref({
  username: '',
  email: '',
  password: ''
})
const registerLoading = ref(false)
const registerPasswordVisible = ref(false)

// 处理登录
const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    ElMessage.warning('请填写完整信息')
    return
  }

  loginLoading.value = true
  try {
    await userStore.login(loginForm.value)
    ElMessage.success('登录成功')
    showLogin.value = false
    loginForm.value = { username: '', password: '' }
  } catch (error) {
    ElMessage.error(error.message || '登录失败')
  } finally {
    loginLoading.value = false
  }
}

// 处理注册
const handleRegister = async () => {
  if (!registerForm.value.username || !registerForm.value.password) {
    ElMessage.warning('请填写完整信息')
    return
  }

  registerLoading.value = true
  try {
    // 如果邮箱为空，不发送 email 字段
    const userData = {
      username: registerForm.value.username,
      password: registerForm.value.password
    }

    // 只有当邮箱不为空时才添加 email 字段
    if (registerForm.value.email && registerForm.value.email.trim()) {
      userData.email = registerForm.value.email
    }

    await userStore.register(userData)
    ElMessage.success('注册成功，请登录')
    showRegister.value = false
    showLogin.value = true
    registerForm.value = { username: '', email: '', password: '' }
  } catch (error) {
    ElMessage.error(error.message || '注册失败')
  } finally {
    registerLoading.value = false
  }
}

// 处理登出
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

.theme-dropdown :deep(.el-button) {
  background-color: transparent;
  border-color: var(--theme-header-text);
  color: var(--theme-header-text);
}

.theme-dropdown :deep(.el-button:hover) {
  background-color: var(--theme-menu-active-bg);
  border-color: var(--theme-header-text);
  color: var(--theme-header-text);
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
  padding: 20px;
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
