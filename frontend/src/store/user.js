import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, register, getCurrentUser } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)

  const isLoggedIn = computed(() => !!token.value)

  // 登录
  const loginAction = async (credentials) => {
    const response = await login(credentials)
    token.value = response.access_token
    user.value = response.user
    localStorage.setItem('token', response.access_token)
  }

  // 注册
  const registerAction = async (userData) => {
    await register(userData)
  }

  // 登出
  const logout = () => {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  // 获取当前用户信息
  const fetchCurrentUser = async () => {
    if (token.value) {
      try {
        user.value = await getCurrentUser()
      } catch (error) {
        logout()
      }
    }
  }

  return {
    token,
    user,
    isLoggedIn,
    login: loginAction,
    register: registerAction,
    logout,
    fetchCurrentUser
  }
})
