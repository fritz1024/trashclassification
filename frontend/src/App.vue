<template>
  <div id="app" :class="{ 'is-dark': themeStore.isDark }">
    <!-- 毛玻璃导航栏 (管理后台页面隐藏) -->
    <header v-if="!isAdminPage" class="navbar glass-heavy">
      <div class="navbar-inner container">
        <!-- Logo -->
        <router-link to="/" class="navbar-logo">
          <div class="logo-icon">
            <el-icon :size="20"><Delete /></el-icon>
          </div>
          <span class="logo-text">垃圾分类识别</span>
        </router-link>

        <!-- Desktop Nav -->
        <nav class="navbar-nav">
          <router-link to="/" class="nav-link" :class="{ active: route.path === '/' }">首页</router-link>
          <router-link to="/classify" class="nav-link" :class="{ active: route.path === '/classify' }">智能识别</router-link>
          <router-link to="/ai-chat" class="nav-link" :class="{ active: route.path === '/ai-chat' }">AI 助手</router-link>
          <router-link to="/user/profile" class="nav-link" :class="{ active: route.path.startsWith('/user') }" v-if="userStore.isLoggedIn">个人中心</router-link>
          <router-link to="/admin/dashboard" class="nav-link" :class="{ active: route.path.startsWith('/admin') }" v-if="userStore.isLoggedIn && userStore.user?.role === 'admin'">管理后台</router-link>
        </nav>

        <!-- Right Actions -->
        <div class="navbar-actions">
          <!-- Theme Toggle -->
          <button class="theme-toggle" @click="themeStore.toggleTheme" :title="themeStore.isDark ? '切换亮色模式' : '切换暗色模式'">
            <el-icon :size="18">
              <Sunny v-if="themeStore.isDark" />
              <Moon v-else />
            </el-icon>
          </button>

          <!-- Auth -->
          <template v-if="!userStore.isLoggedIn">
            <el-button round @click="$router.push('/login')">登录</el-button>
            <el-button round type="primary" @click="$router.push('/login')">注册</el-button>
          </template>
          <template v-else>
            <el-dropdown trigger="hover">
              <div class="user-avatar-btn">
                <img v-if="userStore.user?.avatar" :src="'/' + userStore.user.avatar" class="avatar-circle avatar-img" />
                <div v-else class="avatar-circle">
                  <el-icon :size="16"><User /></el-icon>
                </div>
                <span class="username">{{ userStore.user?.username || '用户' }}</span>
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="$router.push('/profile')">
                    <el-icon><User /></el-icon> 个人中心
                  </el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout">
                    <el-icon><SwitchButton /></el-icon> 退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>

          <!-- Mobile Menu Toggle -->
          <button class="mobile-menu-btn" @click="mobileMenuOpen = !mobileMenuOpen">
            <el-icon :size="22">
              <Close v-if="mobileMenuOpen" />
              <Operation v-else />
            </el-icon>
          </button>
        </div>
      </div>
    </header>

    <!-- Mobile Menu Overlay -->
    <Transition name="mobile-menu">
      <div class="mobile-menu-overlay" v-if="mobileMenuOpen" @click="mobileMenuOpen = false">
        <nav class="mobile-menu glass-heavy" @click.stop>
          <router-link to="/" class="mobile-nav-link" @click="mobileMenuOpen = false">首页</router-link>
          <router-link to="/classify" class="mobile-nav-link" @click="mobileMenuOpen = false">智能识别</router-link>
          <router-link to="/ai-chat" class="mobile-nav-link" @click="mobileMenuOpen = false">AI 助手</router-link>
          <router-link to="/user/profile" class="mobile-nav-link" @click="mobileMenuOpen = false" v-if="userStore.isLoggedIn">个人中心</router-link>
          <template v-if="userStore.isLoggedIn && userStore.user?.role === 'admin'">
            <div class="mobile-nav-divider"></div>
            <span class="mobile-nav-label">管理后台</span>
            <router-link to="/admin/dashboard" class="mobile-nav-link" @click="mobileMenuOpen = false">数据概览</router-link>
            <router-link to="/admin/predictions" class="mobile-nav-link" @click="mobileMenuOpen = false">识别记录</router-link>
            <router-link to="/admin/users" class="mobile-nav-link" @click="mobileMenuOpen = false">用户管理</router-link>
            <router-link to="/admin/feedbacks" class="mobile-nav-link" @click="mobileMenuOpen = false">反馈管理</router-link>
          </template>
        </nav>
      </div>
    </Transition>

    <!-- Main Content -->
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <Transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </Transition>
      </router-view>
    </main>

    <!-- Footer (管理后台页面隐藏) -->
    <footer v-if="!isAdminPage" class="app-footer">
      <div class="container">
        <p>&copy; 2025 垃圾分类识别系统 &middot; 基于 MobileNetV2 深度学习模型</p>
      </div>
    </footer>

    <!-- AI Chat Widget -->
    <ChatWidget v-if="route.path !== '/ai-chat'" />
  </div>
</template>

<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { useThemeStore } from '@/store/theme'
import { ElMessage } from 'element-plus'
import ChatWidget from '@/components/ChatWidget.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const themeStore = useThemeStore()
const mobileMenuOpen = ref(false)
const isAdminPage = computed(() => {
  const p = route.path
  return (p.startsWith('/admin/') && p !== '/admin') || p.startsWith('/user/')
})

// 路由变化时关闭移动菜单
watch(() => route.path, () => {
  mobileMenuOpen.value = false
})

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
  display: flex;
  flex-direction: column;
  background: var(--bg-secondary);
  transition: background var(--transition-normal);
}

/* === Navbar === */
.navbar {
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
  height: var(--navbar-height);
  border-bottom: 1px solid var(--border-secondary);
  transition: all var(--transition-normal);
}

.navbar-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  gap: var(--space-8);
}

/* Logo */
.navbar-logo {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  text-decoration: none;
  color: var(--text-primary);
  flex-shrink: 0;
}

.logo-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  border-radius: var(--radius-sm);
  color: white;
}

.logo-text {
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: var(--text-primary);
}

/* Nav Links */
.navbar-nav {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  flex: 1;
  justify-content: center;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-sm);
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  text-decoration: none;
  transition: all var(--transition-fast);
  cursor: pointer;
  white-space: nowrap;
}

.nav-link:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.nav-link.active {
  color: var(--color-primary);
  background: var(--color-primary-lightest);
}

/* Actions */
.navbar-actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-shrink: 0;
}

.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  background: var(--bg-primary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.theme-toggle:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: var(--bg-hover);
}

.user-avatar-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-1) var(--space-3) var(--space-1) var(--space-1);
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: all var(--transition-fast);
  border: 1px solid var(--border-primary);
  background: var(--bg-primary);
}

.user-avatar-btn:hover {
  border-color: var(--color-primary);
  background: var(--bg-hover);
}

.avatar-circle {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.avatar-img {
  object-fit: cover;
}

.username {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Mobile Menu Button */
.mobile-menu-btn {
  display: none;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  background: var(--bg-primary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.mobile-menu-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

/* === Mobile Menu === */
.mobile-menu-overlay {
  position: fixed;
  inset: 0;
  top: var(--navbar-height);
  z-index: var(--z-modal-backdrop);
  background: rgba(0, 0, 0, 0.3);
}

.mobile-menu {
  position: absolute;
  top: 0;
  right: 0;
  width: 280px;
  max-height: calc(100vh - var(--navbar-height));
  overflow-y: auto;
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  border-left: 1px solid var(--border-secondary);
  border-bottom: 1px solid var(--border-secondary);
  border-radius: 0 0 0 var(--radius-lg);
}

.mobile-nav-link {
  display: block;
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-sm);
  font-size: var(--text-md);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  text-decoration: none;
  transition: all var(--transition-fast);
}

.mobile-nav-link:hover,
.mobile-nav-link.router-link-exact-active {
  color: var(--color-primary);
  background: var(--bg-hover);
}

.mobile-nav-divider {
  height: 1px;
  background: var(--border-primary);
  margin: var(--space-2) 0;
}

.mobile-nav-label {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: var(--space-2) var(--space-4);
}

.mobile-menu-enter-active,
.mobile-menu-leave-active {
  transition: opacity 0.2s ease;
}

.mobile-menu-enter-active .mobile-menu,
.mobile-menu-leave-active .mobile-menu {
  transition: transform 0.25s ease;
}

.mobile-menu-enter-from,
.mobile-menu-leave-to {
  opacity: 0;
}

.mobile-menu-enter-from .mobile-menu,
.mobile-menu-leave-to .mobile-menu {
  transform: translateX(100%);
}

/* === Main Content === */
.main-content {
  flex: 1;
  min-height: calc(100vh - var(--navbar-height) - 60px);
}

/* === Footer === */
.app-footer {
  padding: var(--space-5) 0;
  text-align: center;
  color: var(--text-tertiary);
  font-size: var(--text-sm);
  border-top: 1px solid var(--border-secondary);
  background: var(--bg-primary);
}

/* === Responsive === */
@media (max-width: 1024px) {
  .navbar-nav {
    display: none;
  }

  .mobile-menu-btn {
    display: flex;
  }
}

@media (max-width: 768px) {
  .navbar-actions .el-button {
    display: none;
  }

  .logo-text {
    font-size: var(--text-base);
  }
}
</style>
