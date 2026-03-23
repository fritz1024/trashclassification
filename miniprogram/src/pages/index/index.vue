<template>
  <view class="container">
    <!-- 顶部轮播图 -->
    <swiper class="banner-swiper" indicator-dots circular autoplay interval="3000">
      <swiper-item>
        <view class="banner-item banner1">
          <text class="banner-title">垃圾分类 举手之劳</text>
          <text class="banner-subtitle">智能识别 · 环保生活</text>
        </view>
      </swiper-item>
      <swiper-item>
        <view class="banner-item banner2">
          <text class="banner-title">AI智能识别</text>
          <text class="banner-subtitle">快速准确 · 一键识别</text>
        </view>
      </swiper-item>
      <swiper-item>
        <view class="banner-item banner3">
          <text class="banner-title">保护环境</text>
          <text class="banner-subtitle">从垃圾分类开始</text>
        </view>
      </swiper-item>
    </swiper>

    <!-- 服务卡片 -->
    <view class="service-cards">
      <view class="service-card" @click="goToRecognize">
        <view class="card-icon">📷</view>
        <text class="card-title">智能识别</text>
        <text class="card-desc">拍照识别垃圾分类</text>
      </view>
      <view class="service-card" @click="goToHistory">
        <view class="card-icon">📋</view>
        <text class="card-title">识别历史</text>
        <text class="card-desc">查看历史记录</text>
      </view>
      <view class="service-card" @click="goToGuide">
        <view class="card-icon">📖</view>
        <text class="card-title">分类指南</text>
        <text class="card-desc">学习分类知识</text>
      </view>
    </view>

    <!-- 公告栏 -->
    <view class="notice-section">
      <view class="section-header">
        <text class="section-title">📢 通知公告</text>
      </view>
      <view class="notice-list">
        <view class="notice-item" v-for="(notice, index) in notices" :key="index">
          <text class="notice-dot">•</text>
          <text class="notice-text">{{ notice }}</text>
        </view>
      </view>
    </view>

    <!-- 常用服务 -->
    <view class="common-services">
      <view class="section-header">
        <text class="section-title">常用服务</text>
      </view>
      <view class="services-grid">
        <view class="grid-item" @click="goToStats">
          <view class="grid-icon">📊</view>
          <text class="grid-text">数据统计</text>
        </view>
        <view class="grid-item" @click="goToHistory">
          <view class="grid-icon">🕒</view>
          <text class="grid-text">识别记录</text>
        </view>
        <view class="grid-item" @click="goToKnowledge">
          <view class="grid-icon">💡</view>
          <text class="grid-text">分类知识</text>
        </view>
        <view class="grid-item" @click="goToChat">
          <view class="grid-icon">🤖</view>
          <text class="grid-text">AI助手</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      notices: []
    }
  },

  onLoad() {
    this.fetchNotices()
  },

  methods: {
    async fetchNotices() {
      try {
        const res = await uni.request({
          url: 'http://localhost:8000/api/announcements/list',
          method: 'GET',
          data: { published_only: true, limit: 5 }
        })
        if (res.data && res.data.items) {
          this.notices = res.data.items.map(item => item.title + '：' + item.content)
        }
      } catch (error) {
        console.error('获取公告失败:', error)
      }
    },
    goToRecognize() {
      uni.navigateTo({
        url: '/pages/recognize/recognize'
      })
    },

    goToHistory() {
      const token = uni.getStorageSync('token')
      if (!token) {
        uni.showModal({
          title: '提示',
          content: '查看历史记录需要登录，是否前往登录？',
          success: (res) => {
            if (res.confirm) {
              uni.navigateTo({
                url: '/pages/login/login'
              })
            }
          }
        })
        return
      }
      uni.switchTab({
        url: '/pages/history/history'
      })
    },

    goToStats() {
      const token = uni.getStorageSync('token')
      if (!token) {
        uni.showModal({
          title: '提示',
          content: '查看统计数据需要登录，是否前往登录？',
          success: (res) => {
            if (res.confirm) {
              uni.navigateTo({
                url: '/pages/login/login'
              })
            }
          }
        })
        return
      }
      uni.switchTab({
        url: '/pages/stats/stats'
      })
    },

    goToChat() {
      uni.switchTab({
        url: '/pages/chat/chat'
      })
    },

    goToGuide() {
      uni.showToast({
        title: '功能开发中',
        icon: 'none'
      })
    },

    goToKnowledge() {
      uni.showToast({
        title: '功能开发中',
        icon: 'none'
      })
    }
  }
}
</script>

<style scoped>
.container {
  min-height: 100vh;
  background: #f0fdf4;
}

/* 轮播图 */
.banner-swiper {
  width: 100%;
  height: 400rpx;
}

.banner-item {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40rpx;
}

.banner1 {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.banner2 {
  background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
}

.banner3 {
  background: linear-gradient(135deg, #6ee7b7 0%, #34d399 100%);
}

.banner-title {
  font-size: 48rpx;
  font-weight: bold;
  color: #fff;
  margin-bottom: 20rpx;
}

.banner-subtitle {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.9);
}

/* 服务卡片 */
.service-cards {
  display: flex;
  gap: 20rpx;
  padding: 30rpx;
}

.service-card {
  flex: 1;
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx 20rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 4rpx 12rpx rgba(16, 185, 129, 0.1);
}

.card-icon {
  font-size: 60rpx;
  margin-bottom: 15rpx;
}

.card-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #064e3b;
  margin-bottom: 8rpx;
}

.card-desc {
  font-size: 22rpx;
  color: #6b7280;
  text-align: center;
}

/* 公告栏 */
.notice-section {
  margin: 0 30rpx 30rpx;
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
}

.section-header {
  margin-bottom: 20rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #064e3b;
}

.notice-list {
  display: flex;
  flex-direction: column;
  gap: 15rpx;
}

.notice-item {
  display: flex;
  align-items: flex-start;
}

.notice-dot {
  color: #10b981;
  margin-right: 10rpx;
  font-size: 28rpx;
}

.notice-text {
  flex: 1;
  font-size: 26rpx;
  color: #4b5563;
  line-height: 1.6;
}

/* 常用服务 */
.common-services {
  margin: 0 30rpx 30rpx;
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 30rpx;
}

.grid-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.grid-icon {
  width: 100rpx;
  height: 100rpx;
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 50rpx;
  margin-bottom: 15rpx;
}

.grid-text {
  font-size: 24rpx;
  color: #374151;
  text-align: center;
}
</style>
