<template>
  <view class="container">
    <!-- 未登录提示 -->
    <view v-if="!isLogin" class="empty-state">
      <view class="empty-icon-box">
        <text class="empty-icon-text">未登录</text>
      </view>
      <text class="empty-text">请先登录查看识别历史</text>
      <button class="login-btn" @click="goLogin">去登录</button>
    </view>

    <!-- 历史记录列表 -->
    <view v-else>
      <view v-if="!loading && historyList.length === 0" class="empty-state">
        <view class="empty-icon-box">
          <text class="empty-icon-text">空</text>
        </view>
        <text class="empty-text">暂无识别记录</text>
      </view>

      <view v-else class="history-list">
        <view
          v-for="item in historyList"
          :key="item.id"
          class="history-item"
        >
          <image
            :src="getImageUrl(item.image_path)"
            class="history-image"
            mode="aspectFill"
            @error="onImageError"
          />
          <view class="history-info">
            <text class="category">{{ item.predicted_class }}</text>
            <text class="confidence">置信度: {{ item.confidence.toFixed(2) }}%</text>
            <text class="time">{{ formatTime(item.created_at) }}</text>
          </view>
          <view class="history-actions">
            <button class="delete-btn" @click="deleteItem(item.id)">删除</button>
          </view>
        </view>
      </view>

      <!-- 分页 -->
      <view v-if="total > 0" class="pagination">
        <view class="page-size-selector">
          <text class="page-size-label">每页</text>
          <picker mode="selector" :range="pageSizeOptions" :value="pageSizeIndex" @change="onPageSizeChange">
            <view class="page-size-value">{{ pageSize }}</view>
          </picker>
          <text class="page-size-label">条</text>
        </view>
        <view class="page-controls">
          <button
            class="page-btn"
            :disabled="currentPage === 1"
            @click="goToPage(currentPage - 1)"
          >
            上一页
          </button>
          <text class="page-info">{{ currentPage }} / {{ totalPages }}</text>
          <button
            class="page-btn"
            :disabled="currentPage === totalPages"
            @click="goToPage(currentPage + 1)"
          >
            下一页
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { getHistory, deleteRecord } from '../../api/predict.js'
import config from '../../utils/config.js'

export default {
  data() {
    return {
      isLogin: false,
      historyList: [],
      currentPage: 1,
      pageSize: 10,
      pageSizeOptions: [10, 20, 50, 100],
      pageSizeIndex: 0,
      total: 0,
      loading: false,
      baseURL: config.baseURL
    }
  },

  computed: {
    totalPages() {
      return Math.ceil(this.total / this.pageSize)
    }
  },

  onLoad() {
    this.checkLogin()
    if (this.isLogin) {
      this.loadHistory()
    }
  },

  onShow() {
    // 每次页面显示时重新检查登录状态
    this.checkLogin()

    // 如果已登录，加载历史记录
    if (this.isLogin) {
      this.loadHistory()
    }
  },

  onPullDownRefresh() {
    this.currentPage = 1
    this.loadHistory().then(() => {
      uni.stopPullDownRefresh()
    })
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

    getImageUrl(imagePath) {
      // 处理图片路径
      if (!imagePath) return ''
      if (imagePath.startsWith('http')) return imagePath

      // 移除开头的 ./ 并将反斜杠转换为正斜杠
      let path = imagePath.replace(/^\.?[\/\\]/, '/').replace(/\\/g, '/')
      return this.baseURL + path
    },

    onImageError(e) {
      console.error('图片加载失败:', e)
    },

    async loadHistory() {
      if (this.loading) return

      this.loading = true
      try {
        const res = await getHistory({
          skip: (this.currentPage - 1) * this.pageSize,
          limit: this.pageSize
        })

        // 后端返回格式: { total: number, items: [] }
        this.total = res.total || 0
        this.historyList = res.items || []
      } catch (error) {
        console.error('加载历史记录失败:', error)
        uni.showToast({
          title: '加载失败',
          icon: 'none'
        })
      } finally {
        this.loading = false
      }
    },

    goToPage(page) {
      if (page < 1 || page > this.totalPages) return
      this.currentPage = page
      this.loadHistory()
    },

    onPageSizeChange(e) {
      const index = e.detail.value
      this.pageSizeIndex = index
      this.pageSize = this.pageSizeOptions[index]
      this.currentPage = 1
      this.loadHistory()
    },

    deleteItem(id) {
      uni.showModal({
        title: '提示',
        content: '确定删除这条记录吗？',
        success: async (res) => {
          if (res.confirm) {
            try {
              await deleteRecord(id)
              // 重新加载当前页数据
              this.loadHistory()
              uni.showToast({
                title: '删除成功',
                icon: 'success'
              })
            } catch (error) {
              console.error('删除失败:', error)
              uni.showToast({
                title: '删除失败',
                icon: 'none'
              })
            }
          }
        }
      })
    },

    formatTime(time) {
      // 将 UTC 时间转换为本地时间
      const date = new Date(time)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}/${month}/${day}`
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

.history-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.history-item {
  display: flex;
  background: #fff;
  border-radius: 10rpx;
  padding: 20rpx;
  align-items: center;
}

.history-image {
  width: 120rpx;
  height: 120rpx;
  border-radius: 8rpx;
  margin-right: 20rpx;
}

.history-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.category {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 10rpx;
}

.confidence {
  font-size: 24rpx;
  color: #666;
  margin-bottom: 10rpx;
}

.time {
  font-size: 24rpx;
  color: #999;
}

.history-actions {
  margin-left: 20rpx;
}

.delete-btn {
  padding: 10rpx 30rpx;
  background: #ff4d4f;
  color: #fff;
  border-radius: 20rpx;
  font-size: 24rpx;
  border: none;
}

.pagination {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40rpx 20rpx;
  gap: 20rpx;
}

.page-size-selector {
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.page-size-label {
  font-size: 24rpx;
  color: #666;
}

.page-size-value {
  padding: 5rpx 20rpx;
  background: #f0f0f0;
  border-radius: 10rpx;
  font-size: 24rpx;
  color: #333;
}

.page-controls {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.page-btn {
  padding: 10rpx 30rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 20rpx;
  font-size: 24rpx;
  border: none;
}

.page-btn[disabled] {
  background: #ddd;
  color: #999;
}

.page-info {
  font-size: 28rpx;
  color: #333;
}
</style>
