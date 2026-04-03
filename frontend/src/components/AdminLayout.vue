<template>
  <div class="admin-layout" :class="{ 'sidebar-collapsed': sidebarCollapsed, 'mobile-open': mobileOpen }">
    <!-- Sidebar -->
    <aside class="admin-sidebar">
      <div class="sidebar-header">
        <div class="sidebar-logo">
          <el-icon :size="20"><DataAnalysis /></el-icon>
        </div>
        <span class="sidebar-title" v-show="!sidebarCollapsed">管理后台</span>
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

    <!-- Overlay for mobile -->
    <div
      class="sidebar-overlay"
      v-if="mobileOpen"
      @click="mobileOpen = false"
    />

    <!-- Main content -->
    <div class="admin-main">
      <header class="admin-header glass-heavy">
        <div class="header-left">
          <button class="mobile-toggle" @click="mobileOpen = !mobileOpen">
            <el-icon :size="20"><Fold /></el-icon>
          </button>
        </div>
        <div class="header-right">
          <el-button text class="back-btn" @click="backToUser">
            <el-icon><Back /></el-icon>
            <span>返回用户端</span>
          </el-button>
          <button class="theme-toggle" @click="themeStore.toggleTheme" :title="themeStore.isDark ? '切换亮色模式' : '切换暗色模式'">
            <el-icon :size="16">
              <Sunny v-if="themeStore.isDark" />
              <Moon v-else />
            </el-icon>
          </button>
          <el-dropdown>
            <span class="user-chip">
              <el-icon :size="14"><User /></el-icon>
              <span class="user-name">{{ userStore.user?.username || '管理员' }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <main class="admin-content">
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

const menuItems = computed(() => {
  const items = [
    { path: '/admin/dashboard', icon: 'DataAnalysis', label: '数据概览' },
    { path: '/admin/predictions', icon: 'Picture', label: '识别记录' },
    { path: '/admin/users', icon: 'User', label: '用户管理' },
    { path: '/admin/feedbacks', icon: 'ChatDotRound', label: '反馈管理' },
    { path: '/admin/model', icon: 'Cpu', label: '模型管理' },
    { path: '/admin/announcements', icon: 'Bell', label: '公告管理' },
    { path: '/admin/knowledge', icon: 'Reading', label: '知识库管理' },
  ]

  // 只有超级管理员才能看到模型训练
  if (userStore.user?.role === 'super_admin') {
    items.splice(5, 0, { path: '/admin/training', icon: 'Tools', label: '模型训练' })
  }

  return items
})

const backToUser = () => {
  router.push('/')
}

const handleLogout = () => {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/admin')
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: var(--bg-secondary);
}

/* ---- Sidebar ---- */
.admin-sidebar {
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

.sidebar-collapsed .admin-sidebar {
  width: var(--sidebar-collapsed-width);
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-5) var(--space-5);
  border-bottom: 1px solid var(--border-secondary);
  height: 60px;
  flex-shrink: 0;
}

.sidebar-logo {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  border-radius: var(--radius-sm);
  color: white;
  flex-shrink: 0;
}

.sidebar-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  white-space: nowrap;
}

/* ---- Navigation ---- */
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
  cursor: pointer;
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

.nav-label {
  overflow: hidden;
}

/* ---- Sidebar footer ---- */
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

/* ---- Main area ---- */
.admin-main {
  flex: 1;
  margin-left: var(--sidebar-width);
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  transition: margin-left var(--transition-normal);
}

.sidebar-collapsed .admin-main {
  margin-left: var(--sidebar-collapsed-width);
}

/* ---- Header ---- */
.admin-header {
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 var(--space-6);
  height: 60px;
  border-bottom: 1px solid var(--border-secondary);
  flex-shrink: 0;
}

.header-left {
  display: none;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.back-btn {
  font-size: var(--text-sm);
  color: var(--text-secondary);
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

.user-chip {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-full);
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.user-chip:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.user-name {
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ---- Content ---- */
.admin-content {
  flex: 1;
  padding: var(--space-6);
}

/* ---- Overlay ---- */
.sidebar-overlay {
  display: none;
}

/* ---- Mobile toggle ---- */
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

/* ---- Responsive ---- */
@media (max-width: 768px) {
  .admin-sidebar {
    transform: translateX(-100%);
    box-shadow: var(--shadow-lg);
  }

  .admin-layout.mobile-open .admin-sidebar {
    transform: translateX(0);
  }

  .sidebar-collapsed .admin-sidebar {
    width: var(--sidebar-width);
    transform: translateX(-100%);
  }

  .admin-main {
    margin-left: 0 !important;
  }

  .header-left {
    display: flex;
  }

  .admin-header {
    justify-content: space-between;
  }

  .mobile-toggle {
    display: flex;
  }

  .sidebar-overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.3);
    z-index: calc(var(--z-fixed) - 1);
  }

  .admin-content {
    padding: var(--space-4);
  }

  .user-name {
    display: none;
  }
}
</style>
