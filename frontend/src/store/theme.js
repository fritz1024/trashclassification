import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

// 主题配置
export const themes = {
  light: {
    name: '亮色模式',
    primary: '#409eff',
    headerBg: '#409eff',
    headerText: '#ffffff',
    menuActiveBg: 'rgba(255, 255, 255, 0.2)',
    footerBg: '#2c3e50',
    mainBg: '#f5f7fa',
    cardBg: '#ffffff',
    textColor: '#303133'
  },
  dark: {
    name: '暗黑模式',
    primary: '#409eff',
    headerBg: '#1f1f1f',
    headerText: '#ffffff',
    menuActiveBg: 'rgba(255, 255, 255, 0.1)',
    footerBg: '#000000',
    mainBg: '#141414',
    cardBg: '#1f1f1f',
    textColor: '#e5e5e5'
  }
}

export const useThemeStore = defineStore('theme', () => {
  const currentTheme = ref(localStorage.getItem('theme') || 'light')

  // 应用主题
  const applyTheme = (themeName) => {
    const theme = themes[themeName]
    if (!theme) return

    const root = document.documentElement
    root.style.setProperty('--theme-primary', theme.primary)
    root.style.setProperty('--theme-header-bg', theme.headerBg)
    root.style.setProperty('--theme-header-text', theme.headerText)
    root.style.setProperty('--theme-menu-active-bg', theme.menuActiveBg)
    root.style.setProperty('--theme-footer-bg', theme.footerBg)
    root.style.setProperty('--theme-main-bg', theme.mainBg)
    root.style.setProperty('--theme-card-bg', theme.cardBg)
    root.style.setProperty('--theme-text-color', theme.textColor)
  }

  // 切换主题
  const setTheme = (themeName) => {
    if (themes[themeName]) {
      currentTheme.value = themeName
      localStorage.setItem('theme', themeName)
      applyTheme(themeName)
    }
  }

  // 初始化主题
  const initTheme = () => {
    applyTheme(currentTheme.value)
  }

  // 监听主题变化
  watch(currentTheme, (newTheme) => {
    applyTheme(newTheme)
  })

  return {
    currentTheme,
    themes,
    setTheme,
    initTheme
  }
})
