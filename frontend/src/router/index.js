import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage } from 'element-plus'

const routes = [
  // 用户端路由
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/classify',
    name: 'Classify',
    component: () => import('@/views/Classify.vue')
  },
  {
    path: '/ai-chat',
    name: 'AiChat',
    component: () => import('@/views/AiChat.vue')
  },
  {
    path: '/announcements',
    name: 'Announcements',
    component: () => import('@/views/Announcements.vue')
  },
  {
    path: '/announcements/:id',
    name: 'AnnouncementDetail',
    component: () => import('@/views/AnnouncementDetail.vue')
  },

  // 用户中心路由
  {
    path: '/user/profile',
    name: 'UserProfile',
    component: () => import('@/views/user/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/user/history',
    name: 'UserHistory',
    component: () => import('@/views/user/History.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/user/stats',
    name: 'UserStats',
    component: () => import('@/views/user/Stats.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/user/feedbacks',
    name: 'UserFeedbacks',
    component: () => import('@/views/user/Feedbacks.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/user/security',
    name: 'UserSecurity',
    component: () => import('@/views/user/Security.vue'),
    meta: { requiresAuth: true }
  },

  // 旧路由重定向
  { path: '/history', redirect: '/user/history' },
  { path: '/stats', redirect: '/user/stats' },
  { path: '/profile', redirect: '/user/profile' },

  // 管理端路由
  {
    path: '/admin',
    name: 'AdminLogin',
    component: () => import('@/views/admin/Login.vue')
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: () => import('@/views/admin/Dashboard.vue'),
    meta: { requiresAdmin: true }
  },
  {
    path: '/admin/predictions',
    name: 'AdminPredictions',
    component: () => import('@/views/admin/Predictions.vue'),
    meta: { requiresAdmin: true }
  },
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: () => import('@/views/admin/Users.vue'),
    meta: { requiresAdmin: true }
  },
  {
    path: '/admin/feedbacks',
    name: 'AdminFeedbacks',
    component: () => import('@/views/admin/Feedbacks.vue'),
    meta: { requiresAdmin: true }
  },
  {
    path: '/admin/model',
    name: 'AdminModel',
    component: () => import('@/views/admin/Model.vue'),
    meta: { requiresAdmin: true }
  },
  {
    path: '/admin/announcements',
    name: 'AdminAnnouncements',
    component: () => import('@/views/admin/Announcements.vue'),
    meta: { requiresAdmin: true }
  },
  {
    path: '/admin/settings',
    name: 'AdminSettings',
    component: () => import('@/views/admin/Settings.vue'),
    meta: { requiresAdmin: true }
  },
  {
    path: '/admin/knowledge',
    name: 'AdminKnowledge',
    component: () => import('@/views/admin/Knowledge.vue'),
    meta: { requiresAdmin: true }
  },
  {
    path: '/admin/training',
    name: 'AdminTraining',
    component: () => import('@/views/admin/Training.vue'),
    meta: { requiresAdmin: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  if (to.meta.requiresAdmin) {
    if (!userStore.isLoggedIn || !['admin', 'super_admin'].includes(userStore.user?.role)) {
      ElMessage.warning('需要管理员权限')
      next('/admin')
      return
    }
  }

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    next('/login')
    return
  }

  next()
})

export default router
