<template>
  <view class="container">
    <!-- 识别模式切换 -->
    <view class="mode-switch">
      <view
        class="mode-item"
        :class="{ active: mode === 'single' }"
        @click="switchMode('single')"
      >
        <text>单张识别</text>
      </view>
      <view
        class="mode-item"
        :class="{ active: mode === 'batch' }"
        @click="switchMode('batch')"
      >
        <text>批量识别</text>
      </view>
    </view>

    <!-- 单张识别 -->
    <view v-if="mode === 'single'" class="single-mode">
      <view class="upload-area" @click="chooseImage">
        <image
          v-if="imageUrl"
          :src="imageUrl"
          class="preview-image"
          mode="aspectFit"
        />
        <view v-else class="upload-placeholder">
          <view class="icon-box">
            <text class="icon-text">+</text>
          </view>
          <text class="text">点击上传图片</text>
          <text class="tip">支持拍照或从相册选择</text>
        </view>
      </view>

      <button
        v-if="imageUrl && !loading"
        class="recognize-btn"
        @click="recognizeSingle"
      >
        开始识别
      </button>

      <!-- 识别结果 -->
      <view v-if="result && result.top3_results && result.top3_results.length > 0" class="result-card">
        <view class="result-header">
          <text class="result-title">识别结果</text>
        </view>
        <view class="result-item main">
          <text class="category">{{ result.top3_results[0].class_name }}</text>
          <text class="confidence">置信度: {{ result.top3_results[0].confidence.toFixed(2) }}%</text>
        </view>
        <view v-if="result.top3_results.length > 1" class="other-results">
          <text class="other-title">其他可能:</text>
          <view
            v-for="(item, index) in result.top3_results.slice(1)"
            :key="index"
            class="result-item"
          >
            <text class="category-name">{{ item.class_name }}</text>
            <text class="confidence-value">{{ item.confidence.toFixed(2) }}%</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 批量识别 -->
    <view v-else class="batch-mode">
      <view class="batch-images">
        <view
          v-for="(img, index) in batchImages"
          :key="index"
          class="batch-image-item"
        >
          <image :src="img" class="batch-image" mode="aspectFill" />
          <view class="delete-btn" @click="removeBatchImage(index)">×</view>
        </view>
        <view
          v-if="batchImages.length < 9"
          class="add-image-btn"
          @click="chooseBatchImages"
        >
          <text class="add-icon">+</text>
          <text class="add-text">添加图片</text>
        </view>
      </view>

      <button
        v-if="batchImages.length > 0 && !loading"
        class="recognize-btn"
        @click="recognizeBatch"
      >
        批量识别 ({{ batchImages.length }})
      </button>

      <!-- 批量识别结果 -->
      <view v-if="batchResults.length > 0" class="batch-results">
        <view class="result-header">
          <text class="result-title">识别结果</text>
        </view>
        <view
          v-for="(item, index) in batchResults"
          :key="index"
          class="batch-result-item"
        >
          <image :src="batchImages[index]" class="result-thumb" mode="aspectFill" />
          <view class="result-info">
            <text class="category">{{ item.predicted_class || '未知' }}</text>
            <text class="confidence">置信度: {{ item.confidence ? item.confidence.toFixed(2) : '0' }}%</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 加载提示 -->
    <view v-if="loading" class="loading-mask">
      <view class="loading-content">
        <text class="loading-text">识别中...</text>
      </view>
    </view>
  </view>
</template>

<script>
import { predictSingle, predictBatch } from '../../api/predict.js'

export default {
  data() {
    return {
      mode: 'single',
      imageUrl: '',
      imagePath: '',
      result: null,
      batchImages: [],
      batchResults: [],
      loading: false
    }
  },

  methods: {
    switchMode(mode) {
      this.mode = mode
      this.imageUrl = ''
      this.imagePath = ''
      this.result = null
      this.batchImages = []
      this.batchResults = []
    },

    // 选择单张图片
    chooseImage() {
      uni.showActionSheet({
        itemList: ['拍照', '从相册选择'],
        success: (res) => {
          const sourceType = res.tapIndex === 0 ? ['camera'] : ['album']
          uni.chooseImage({
            count: 1,
            sourceType,
            success: (res) => {
              this.imageUrl = res.tempFilePaths[0]
              this.imagePath = res.tempFilePaths[0]
              this.result = null
            }
          })
        }
      })
    },

    // 选择批量图片
    chooseBatchImages() {
      const maxCount = 9 - this.batchImages.length
      uni.chooseImage({
        count: maxCount,
        sourceType: ['album', 'camera'],
        success: (res) => {
          this.batchImages = [...this.batchImages, ...res.tempFilePaths]
          this.batchResults = []
        }
      })
    },

    // 删除批量图片
    removeBatchImage(index) {
      this.batchImages.splice(index, 1)
      if (this.batchResults.length > 0) {
        this.batchResults.splice(index, 1)
      }
    },

    // 单张识别
    async recognizeSingle() {
      if (!this.imagePath) {
        uni.showToast({
          title: '请先选择图片',
          icon: 'none'
        })
        return
      }

      this.loading = true
      try {
        const res = await predictSingle(this.imagePath)

        // 检查返回数据是否有效
        if (!res || !res.top3_results || res.top3_results.length === 0) {
          uni.showToast({
            title: '识别失败，请重试',
            icon: 'none'
          })
          this.result = null
          return
        }

        this.result = res
        uni.showToast({
          title: '识别成功',
          icon: 'success'
        })
      } catch (error) {
        console.error('识别错误:', error)
        uni.showToast({
          title: '识别失败，请检查网络',
          icon: 'none'
        })
        this.result = null
      } finally {
        this.loading = false
      }
    },

    // 批量识别
    async recognizeBatch() {
      if (this.batchImages.length === 0) {
        uni.showToast({
          title: '请先选择图片',
          icon: 'none'
        })
        return
      }

      // 检查是否登录
      const token = uni.getStorageSync('token')
      if (!token) {
        uni.showModal({
          title: '提示',
          content: '批量识别需要登录，是否前往登录？',
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

      this.loading = true
      try {
        const results = await predictBatch(this.batchImages)

        // 检查返回数据是否有效
        if (!results || results.length === 0) {
          uni.showToast({
            title: '识别失败，请重试',
            icon: 'none'
          })
          this.batchResults = []
          return
        }

        this.batchResults = results
        uni.showToast({
          title: '识别完成',
          icon: 'success'
        })
      } catch (error) {
        console.error('批量识别错误:', error)
        uni.showToast({
          title: '识别失败，请检查网络',
          icon: 'none'
        })
        this.batchResults = []
      } finally {
        this.loading = false
      }
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

.mode-switch {
  display: flex;
  background: #fff;
  border-radius: 10rpx;
  padding: 10rpx;
  margin-bottom: 20rpx;
}

.mode-item {
  flex: 1;
  text-align: center;
  padding: 20rpx;
  border-radius: 8rpx;
  font-size: 28rpx;
  color: #666;
  transition: all 0.3s;
}

.mode-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-weight: bold;
}

/* 单张识别 */
.upload-area {
  background: #fff;
  border-radius: 10rpx;
  padding: 40rpx;
  margin-bottom: 20rpx;
  min-height: 500rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-image {
  width: 100%;
  height: 500rpx;
}

.upload-placeholder {
  text-align: center;
}

.icon-box {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50rpx;
  background: #f0f0f0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20rpx;
}

.icon-text {
  font-size: 60rpx;
  color: #999;
  font-weight: 300;
}

.text {
  display: block;
  font-size: 32rpx;
  color: #333;
  margin-bottom: 10rpx;
}

.tip {
  display: block;
  font-size: 24rpx;
  color: #999;
}

.recognize-btn {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 44rpx;
  font-size: 32rpx;
  border: none;
  margin-bottom: 20rpx;
}

.result-card {
  background: #fff;
  border-radius: 10rpx;
  padding: 30rpx;
}

.result-header {
  margin-bottom: 20rpx;
}

.result-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.result-item {
  padding: 20rpx;
  border-radius: 8rpx;
  margin-bottom: 10rpx;
}

.result-item.main {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.category {
  display: block;
  font-size: 36rpx;
  font-weight: bold;
  color: #fff;
  margin-bottom: 10rpx;
}

.confidence {
  display: block;
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.9);
}

.other-results {
  margin-top: 20rpx;
}

.other-title {
  display: block;
  font-size: 28rpx;
  color: #666;
  margin-bottom: 10rpx;
}

.category-name {
  font-size: 28rpx;
  color: #333;
}

.confidence-value {
  font-size: 24rpx;
  color: #999;
  margin-left: 20rpx;
}

/* 批量识别 */
.batch-images {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
  margin-bottom: 20rpx;
}

.batch-image-item {
  position: relative;
  width: 220rpx;
  height: 220rpx;
}

.batch-image {
  width: 100%;
  height: 100%;
  border-radius: 10rpx;
}

.delete-btn {
  position: absolute;
  top: -10rpx;
  right: -10rpx;
  width: 50rpx;
  height: 50rpx;
  background: #ff4d4f;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
  line-height: 1;
}

.add-image-btn {
  width: 220rpx;
  height: 220rpx;
  background: #fff;
  border-radius: 10rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 2rpx dashed #ddd;
}

.add-icon {
  font-size: 60rpx;
  color: #999;
  margin-bottom: 10rpx;
}

.add-text {
  font-size: 24rpx;
  color: #999;
}

.batch-results {
  background: #fff;
  border-radius: 10rpx;
  padding: 30rpx;
}

.batch-result-item {
  display: flex;
  align-items: center;
  padding: 20rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.batch-result-item:last-child {
  border-bottom: none;
}

.result-thumb {
  width: 100rpx;
  height: 100rpx;
  border-radius: 8rpx;
  margin-right: 20rpx;
}

.result-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.result-info .category {
  font-size: 28rpx;
  color: #333;
  font-weight: bold;
  margin-bottom: 5rpx;
}

.result-info .confidence {
  font-size: 24rpx;
  color: #666;
}

.loading-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-content {
  background: #fff;
  padding: 40rpx 60rpx;
  border-radius: 10rpx;
}

.loading-text {
  font-size: 28rpx;
  color: #333;
}
</style>
