<template>
  <div class="user-layout" :class="{ 'sidebar-collapsed': sidebarCollapsed, 'mobile-open': mobileOpen }">
    <aside class="user-sidebar">
      <div class="sidebar-header">
        <img v-if="userStore.user?.avatar" :src="'/' + userStore.user.avatar" class="sidebar-avatar sidebar-avatar-img" />
        <div v-else class="sidebar-avatar">
          <span>{{ initial }}</span>
        </div>
        <div class="sidebar-user" v-show="!sidebarCollapsed">
          <span class="sidebar-name">{{ userStore.user?.username || '用户' }}</span>
          <el-tag size="small" round :type="userStore.user?.role === 'super_admin' ? 'danger' : userStore.user?.role === 'admin' ? 'warning' : 'success'">
            {{ userStore.user?.role === 'super_admin' ? '超级管理员' : userStore.user?.role === 'admin' ? '管理员' : '用户' }}
          </el-tag>
        </div>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: activeMenu === item.path }"
        >
          <el-icon :size="18"><component :is="item.icon" /></el-icon>
          <span class="nav-label" v-show="!sidebarCollapsed">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <button class="collapse-btn" @click="sidebarCollapsed = !sidebarCollapsed">
          <el-icon :size="16">
            <DArrowLeft v-if="!sidebarCollapsed" />
            <DArrowRight v-else />
          </el-icon>
        </button>
      </div>
    </aside>

    <div class="sidebar-overlay" v-if="mobileOpen" @click="mobileOpen = false" />

    <div class="user-main">
      <header class="user-header glass-heavy">
        <div class="header-left">
          <button class="mobile-toggle" @click="mobileOpen = !mobileOpen">
            <el-icon :size="20"><Fold /></el-icon>
          </button>
          <router-link to="/" class="header-logo">
            <div class="logo-icon-sm">
              <el-icon :size="16"><Delete /></el-icon>
            </div>
            <span>垃圾分类识别</span>
          </router-link>
        </div>
        <nav class="header-nav">
          <router-link to="/" class="header-nav-link">首页</router-link>
          <router-link to="/classify" class="header-nav-link">智能识别</router-link>
          <router-link to="/ai-chat" class="header-nav-link">AI 助手</router-link>
          <router-link to="/admin/dashboard" class="header-nav-link" v-if="['admin', 'super_admin'].includes(userStore.user?.role)">管理后台</router-link>
        </nav>
        <div class="header-right">
          <button class="theme-toggle" @click="themeStore.toggleTheme" :title="themeStore.isDark ? '切换亮色模式' : '切换暗色模式'">
            <el-icon :size="16">
              <Sunny v-if="themeStore.isDark" />
              <Moon v-else />
            </el-icon>
          </button>
          <el-dropdown>
            <div class="header-user-chip">
              <img v-if="userStore.user?.avatar" :src="'/' + userStore.user.avatar" class="chip-avatar chip-avatar-img" />
              <div v-else class="chip-avatar">{{ initial }}</div>
              <span class="chip-name">{{ userStore.user?.username || '用户' }}</span>
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="$router.push('/user/profile')">
                  <el-icon><User /></el-icon> 个人中心
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon> 退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <main class="user-content">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { useThemeStore } from '@/store/theme'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const themeStore = useThemeStore()

const activeMenu = computed(() => route.path)
const sidebarCollapsed = ref(false)
const mobileOpen = ref(false)

const initial = computed(() => {
  const name = userStore.user?.username || 'U'
  return name.charAt(0).toUpperCase()
})

const menuItems = [
  { path: '/user/profile', icon: 'User', label: '个人信息' },
  { path: '/user/history', icon: 'List', label: '识别历史' },
  { path: '/user/feedbacks', icon: 'ChatDotRound', label: '我的反馈' },
  { path: '/user/stats', icon: 'DataAnalysis', label: '数据统计' },
  { path: '/user/security', icon: 'Lock', label: '账号安全' },
]

const handleLogout = () => {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/')
}
</script>

<style scoped>
.user-layout {
  display: flex;
  min-height: 100vh;
  background: var(--bg-secondary);
}

/* Sidebar */
.user-sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: var(--sidebar-width);
  background: var(--bg-primary);
  border-right: 1px solid var(--border-secondary);
  display: flex;
  flex-direction: column;
  z-index: var(--z-fixed);
  transition: width var(--transition-normal);
}

.sidebar-collapsed .user-sidebar {
  width: var(--sidebar-collapsed-width);
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-5);
  border-bottom: 1px solid var(--border-secondary);
  height: 72px;
  flex-shrink: 0;
}

.sidebar-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  flex-shrink: 0;
}

.sidebar-avatar-img {
  object-fit: cover;
  background: none;
}

.sidebar-user {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  min-width: 0;
}

.sidebar-name {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Nav */
.sidebar-nav {
  flex: 1;
  padding: var(--space-3);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  text-decoration: none;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.nav-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.nav-item.active {
  background: var(--color-primary-lightest);
  color: var(--color-primary-dark);
  font-weight: var(--font-semibold);
}

.nav-label { overflow: hidden; }

/* Footer */
.sidebar-footer {
  padding: var(--space-3);
  border-top: 1px solid var(--border-secondary);
  flex-shrink: 0;
}

.collapse-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-2);
  border-radius: var(--radius-sm);
  border: none;
  background: transparent;
  color: var(--text-tertiary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.collapse-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

/* Main */
.user-main {
  flex: 1;
  margin-left: var(--sidebar-width);
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  transition: margin-left var(--transition-normal);
}

.sidebar-collapsed .user-main {
  margin-left: var(--sidebar-collapsed-width);
}

/* Header */
.user-header {
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-6);
  height: 60px;
  border-bottom: 1px solid var(--border-secondary);
  flex-shrink: 0;
  gap: var(--space-6);
}

.header-left { display: flex; align-items: center; gap: var(--space-3); }

.header-logo {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  text-decoration: none;
  color: var(--text-primary);
  font-weight: var(--font-bold);
  font-size: var(--text-base);
}

.logo-icon-sm {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  border-radius: var(--radius-xs);
  color: white;
}

.header-nav {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.header-nav-link {
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  text-decoration: none;
  transition: all var(--transition-fast);
}

.header-nav-link:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.header-user-chip {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: 3px var(--space-3) 3px 3px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border-primary);
  background: var(--bg-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.header-user-chip:hover {
  border-color: var(--color-primary);
  background: var(--bg-hover);
}

.chip-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
}

.chip-avatar-img {
  object-fit: cover;
  background: none;
}

.chip-name {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
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

/* Content */
.user-content {
  flex: 1;
  padding: var(--space-6);
}

/* Overlay */
.sidebar-overlay { display: none; }

.mobile-toggle {
  display: none;
  align-items: center;
  justify-content: center;
  padding: var(--space-2);
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
}

/* Responsive */
@media (max-width: 768px) {
  .user-sidebar {
    transform: translateX(-100%);
    box-shadow: var(--shadow-lg);
  }
  .user-layout.mobile-open .user-sidebar { transform: translateX(0); }
  .sidebar-collapsed .user-sidebar { width: var(--sidebar-width); transform: translateX(-100%); }
  .user-main { margin-left: 0 !important; }
  .mobile-toggle { display: flex; }
  .header-nav { display: none; }
  .header-logo span { display: none; }
  .chip-name { display: none; }
  .sidebar-overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.3);
    z-index: calc(var(--z-fixed) - 1);
  }
  .user-content { padding: var(--space-4); }
}
</style>
