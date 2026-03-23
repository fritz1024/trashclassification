import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

// 绿色主题配置
export const themes = {
  green: {
    name: '绿色主题',
    primary: '#10b981',
    headerBg: '#10b981',
    headerText: '#ffffff',
    menuActiveBg: 'rgba(255, 255, 255, 0.2)',
    footerBg: '#047857',
    mainBg: '#f0fdf4',
    cardBg: '#ffffff',
    textColor: '#1f2937'
  }
}

export const useThemeStore = defineStore('theme', () => {
  const currentTheme = ref('green')

  // 应用主题
  const applyTheme = () => {
    const theme = themes.green
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

  // 初始化主题
  const initTheme = () => {
    applyTheme()
  }

  return {
    currentTheme,
    themes,
    initTheme
  }
})
