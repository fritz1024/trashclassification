<template>
  <view class="container">
    <!-- 未登录提示 -->
    <view v-if="!isLogin" class="empty-state">
      <view class="empty-icon-box">
        <text class="empty-icon-text">未登录</text>
      </view>
      <text class="empty-text">请先登录查看数据统计</text>
      <button class="login-btn" @click="goLogin">去登录</button>
    </view>

    <!-- 统计数据 -->
    <view v-else class="stats-content">
      <!-- 统计卡片 -->
      <view class="stats-cards">
        <view class="stat-card">
          <text class="stat-value">{{ stats.total_predictions || 0 }}</text>
          <text class="stat-label">识别次数</text>
        </view>
        <view class="stat-card">
          <text class="stat-value">{{ averageConfidence }}</text>
          <text class="stat-label">平均置信度</text>
        </view>
      </view>

      <!-- 分类占比 -->
      <view class="chart-card">
        <view class="card-header">
          <text class="card-title">垃圾分类统计</text>
        </view>
        <view v-if="categoryStats.length === 0" class="empty-chart">
          <text class="empty-text">暂无数据</text>
        </view>
        <view v-else>
          <!-- 简单饼图展示 -->
          <view class="simple-pie-container">
            <view class="simple-pie">
              <view
                v-for="(item, index) in categoryStats.slice(0, 4)"
                :key="index"
                class="pie-segment"
                :style="{
                  width: item.percentage + '%',
                  background: getSimpleColor(index)
                }"
              ></view>
            </view>
            <view class="pie-legend">
              <view
                v-for="(item, index) in categoryStats.slice(0, 4)"
                :key="index"
                class="legend-item"
              >
                <view class="legend-dot" :style="{ background: getSimpleColor(index) }"></view>
                <text class="legend-text">{{ item.category }} ({{ item.percentage.toFixed(1) }}%)</text>
              </view>
            </view>
          </view>

          <!-- 进度条列表 -->
          <view class="category-list">
            <view
              v-for="(item, index) in paginatedCategoryStats"
              :key="index"
              class="category-item"
            >
              <view class="category-info">
                <text class="category-name">{{ item.category }}</text>
                <text class="category-count">{{ item.count }}次</text>
              </view>
              <view class="progress-bar">
                <view
                  class="progress-fill"
                  :style="{ width: item.percentage + '%', background: getSimpleColor(item.originalIndex) }"
                ></view>
              </view>
              <text class="percentage">{{ item.percentage.toFixed(1) }}%</text>
            </view>
          </view>

          <!-- 分页控件 -->
          <view v-if="categoryStats.length > 0" class="pagination">
            <view class="page-size-selector">
              <text class="page-size-label">每页显示：</text>
              <picker mode="selector" :range="pageSizeOptions" :value="pageSizeIndex" @change="onPageSizeChange">
                <view class="picker">
                  {{ pageSizeOptions[pageSizeIndex] }} 条
                </view>
              </picker>
            </view>
            <view class="page-controls">
              <button class="page-btn" :disabled="currentPage === 1" @click="prevPage">上一页</button>
              <text class="page-info">{{ currentPage }} / {{ totalPages }}</text>
              <button class="page-btn" :disabled="currentPage === totalPages" @click="nextPage">下一页</button>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { getUserStats } from '../../api/stats.js'

export default {
  data() {
    return {
      isLogin: false,
      stats: {},
      categoryStats: [],
      currentPage: 1,
      pageSize: 10,
      pageSizeOptions: [10, 20, 50],
      pageSizeIndex: 0
    }
  },

  computed: {
    averageConfidence() {
      const avg = this.stats.avg_confidence || 0
      return avg.toFixed(1) + ' %'
    },

    totalPages() {
      return Math.ceil(this.categoryStats.length / this.pageSize)
    },

    paginatedCategoryStats() {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      return this.categoryStats.slice(start, end).map((item, index) => ({
        ...item,
        originalIndex: start + index
      }))
    }
  },

  onLoad() {
    this.checkLogin()
    if (this.isLogin) {
      this.loadStats()
    }
  },

  onShow() {
    // 每次页面显示时重新检查登录状态并刷新数据
    const wasLogin = this.isLogin
    this.checkLogin()

    if (this.isLogin) {
      // 刷新统计数据
      this.loadStats()
    } else if (wasLogin && !this.isLogin) {
      // 如果从已登录变为未登录，清空数据
      this.stats = {}
      this.categoryStats = []
    }
  },

  methods: {
    checkLogin() {
      const token = uni.getStorageSync('token')
      this.isLogin = !!token
    },

    goLogin() {
      uni.navigateTo({
        url: '/pages/login/login'
      })
    },

    async loadStats() {
      try {
        const res = await getUserStats()
        this.stats = res
        // 后端返回的是 category_stats 数组，不是 category_distribution 对象
        this.processCategoryStats(res.category_stats || [])
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }
    },

    processCategoryStats(categoryStatsArray) {
      // 后端返回格式: [{ category: "厨余垃圾-蔬菜", count: 5 }, ...]
      const total = categoryStatsArray.reduce((sum, item) => sum + item.count, 0)
      this.categoryStats = categoryStatsArray
        .map(item => ({
          category: item.category,
          count: item.count,
          percentage: total > 0 ? (item.count / total) * 100 : 0
        }))
        .sort((a, b) => b.count - a.count)
    },

    getCategoryColor(index) {
      const colors = [
        'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
        'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
        'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
      ]
      return colors[index % colors.length]
    },

    getSimpleColor(index) {
      const colors = [
        '#667eea',
        '#f093fb',
        '#4facfe',
        '#43e97b',
        '#fa709a'
      ]
      return colors[index % colors.length]
    },

    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--
      }
    },

    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++
      }
    },

    onPageSizeChange(e) {
      const index = e.detail.value
      this.pageSizeIndex = index
      this.pageSize = this.pageSizeOptions[index]
      this.currentPage = 1
    }
  }
}
</script>

<style scoped>
.container {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20rpx;
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
  font-size: 32rpx;
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

.stats-content {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.stats-cards {
  display: flex;
  gap: 20rpx;
}

.stat-card {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10rpx;
  padding: 40rpx;
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 48rpx;
  font-weight: bold;
  color: #fff;
  margin-bottom: 10rpx;
}

.stat-label {
  display: block;
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
}

.chart-card {
  background: #fff;
  border-radius: 10rpx;
  padding: 30rpx;
}

.card-header {
  margin-bottom: 30rpx;
}

.card-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.simple-pie-container {
  margin-bottom: 40rpx;
  padding: 20rpx 0;
}

.simple-pie {
  display: flex;
  height: 40rpx;
  border-radius: 20rpx;
  overflow: hidden;
  margin-bottom: 30rpx;
}

.pie-segment {
  height: 100%;
  transition: width 0.3s;
}

.pie-legend {
  display: flex;
  flex-direction: column;
  gap: 15rpx;
  padding: 0 20rpx;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 15rpx;
}

.legend-dot {
  width: 20rpx;
  height: 20rpx;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-text {
  font-size: 24rpx;
  color: #333;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 30rpx;
}

.category-item {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.category-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.category-name {
  font-size: 28rpx;
  color: #333;
}

.category-count {
  font-size: 24rpx;
  color: #999;
}

.progress-bar {
  height: 16rpx;
  background: #f0f0f0;
  border-radius: 8rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8rpx;
  transition: width 0.3s;
}

.percentage {
  font-size: 24rpx;
  color: #667eea;
  font-weight: bold;
}

.empty-chart {
  text-align: center;
  padding: 60rpx 0;
}

.empty-chart .empty-text {
  font-size: 28rpx;
  color: #999;
}

/* 分页样式 */
.pagination {
  margin-top: 30rpx;
  padding: 20rpx;
  background: #fff;
  border-radius: 10rpx;
}

.page-size-selector {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20rpx;
}

.page-size-label {
  font-size: 26rpx;
  color: #666;
  margin-right: 10rpx;
}

.picker {
  padding: 10rpx 20rpx;
  background: #f5f5f5;
  border-radius: 8rpx;
  font-size: 26rpx;
  color: #333;
}

.page-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20rpx;
}

.page-btn {
  padding: 10rpx 30rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 8rpx;
  font-size: 26rpx;
  border: none;
}

.page-btn[disabled] {
  background: #e0e0e0;
  color: #999;
}

.page-info {
  font-size: 26rpx;
  color: #666;
  min-width: 120rpx;
  text-align: center;
}
</style>
