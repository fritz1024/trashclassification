<template>
  <view class="container">
    <!-- 未登录状态 -->
    <view v-if="!isLogin" class="empty-state">
      <view class="empty-icon-box">
        <text class="empty-icon-text">未登录</text>
      </view>
      <text class="empty-text">请先登录</text>
      <button class="login-btn" @click="goLogin">去登录</button>
    </view>

    <!-- 已登录状态 -->
    <view v-else class="profile-content">
      <!-- 用户信息卡片 -->
      <view class="user-card">
        <view class="avatar">
          <text class="avatar-text">{{ userInfo.username ? userInfo.username.charAt(0).toUpperCase() : 'U' }}</text>
        </view>
        <view class="user-info">
          <text class="username">{{ userInfo.username }}</text>
          <text class="user-role">{{ userInfo.role === 'admin' ? '管理员' : '普通用户' }}</text>
        </view>
      </view>

      <!-- 统计信息 -->
      <view class="stats-grid">
        <view class="stat-item">
          <text class="stat-value">{{ stats.total || 0 }}</text>
          <text class="stat-label">识别次数</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ stats.days || 0 }}</text>
          <text class="stat-label">使用天数</text>
        </view>
      </view>

      <!-- 功能列表 -->
      <view class="menu-list">
        <view class="menu-item" @click="goToHistory">
          <text class="menu-text">识别历史</text>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="goToStats">
          <text class="menu-text">数据统计</text>
          <text class="menu-arrow">›</text>
        </view>
      </view>

      <!-- 退出登录按钮 -->
      <button class="logout-btn" @click="handleLogout">退出登录</button>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      isLogin: false,
      userInfo: {},
      stats: {
        total: 0,
        days: 0
      }
    }
  },

  onLoad() {
    this.checkLogin()
  },

  onShow() {
    this.checkLogin()
    if (this.isLogin) {
      this.loadUserStats()
    }
  },

  methods: {
    checkLogin() {
      const token = uni.getStorageSync('token')
      const userInfo = uni.getStorageSync('userInfo')
      this.isLogin = !!token
      if (userInfo) {
        this.userInfo = userInfo
      }
    },

    goLogin() {
      uni.navigateTo({
        url: '/pages/login/login'
      })
    },

    async loadUserStats() {
      // 这里可以调用 API 获取用户统计数据
      // 暂时使用本地存储的数据
      try {
        const { getUserStats } = require('../../api/stats.js')
        const res = await getUserStats()
        this.stats.total = res.total_predictions || 0
        // 计算使用天数（简单实现）
        const userInfo = uni.getStorageSync('userInfo')
        if (userInfo && userInfo.created_at) {
          const createdDate = new Date(userInfo.created_at)
          const now = new Date()
          const days = Math.floor((now - createdDate) / (1000 * 60 * 60 * 24))
          this.stats.days = days
        }
      } catch (error) {
        console.error('加载用户统计失败:', error)
      }
    },

    goToHistory() {
      uni.switchTab({
        url: '/pages/history/history'
      })
    },

    goToStats() {
      uni.switchTab({
        url: '/pages/stats/stats'
      })
    },

    handleLogout() {
      uni.showModal({
        title: '提示',
        content: '确定要退出登录吗？',
        success: (res) => {
          if (res.confirm) {
            // 清除本地存储
            uni.removeStorageSync('token')
            uni.removeStorageSync('userInfo')

            // 更新状态
            this.isLogin = false
            this.userInfo = {}
            this.stats = { total: 0, days: 0 }

            uni.showToast({
              title: '已退出登录',
              icon: 'success'
            })
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.container {
  min-height: 100vh;
  background: #f5f5f5;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 200rpx 0;
}

.empty-icon-box {
  width: 120rpx;
  height: 120rpx;
  border-radius: 60rpx;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 30rpx;
}

.empty-icon-text {
  font-size: 28rpx;
  color: #999;
  font-weight: bold;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
  margin-bottom: 40rpx;
}

.login-btn {
  width: 300rpx;
  height: 80rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 40rpx;
  font-size: 28rpx;
  border: none;
}
.profile-content {
  padding: 20rpx;
}

.user-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20rpx;
  padding: 40rpx;
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.avatar {
  width: 120rpx;
  height: 120rpx;
  border-radius: 60rpx;
  background: rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 30rpx;
}

.avatar-text {
  font-size: 48rpx;
  color: #fff;
  font-weight: bold;
}

.user-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.username {
  font-size: 36rpx;
  color: #fff;
  font-weight: bold;
  margin-bottom: 10rpx;
}

.user-role {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
}

.stats-grid {
  display: flex;
  gap: 20rpx;
  margin-bottom: 20rpx;
}

.stat-item {
  flex: 1;
  background: #fff;
  border-radius: 10rpx;
  padding: 30rpx;
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 48rpx;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 10rpx;
}

.stat-label {
  display: block;
  font-size: 24rpx;
  color: #999;
}

.menu-list {
  background: #fff;
  border-radius: 10rpx;
  margin-bottom: 20rpx;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-text {
  flex: 1;
  font-size: 28rpx;
  color: #333;
}

.menu-arrow {
  font-size: 40rpx;
  color: #ccc;
}

.logout-btn {
  width: 100%;
  height: 88rpx;
  background: #fff;
  color: #ff4d4f;
  border-radius: 10rpx;
  font-size: 28rpx;
  border: 1rpx solid #ff4d4f;
}
</style>
