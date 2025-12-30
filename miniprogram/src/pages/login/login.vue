<template>
  <view class="login-container">
    <view class="header">
      <text class="title">垃圾分类助手</text>
      <text class="subtitle">智能识别 · 环保生活</text>
    </view>

    <view class="form-container">
      <view class="tab-bar">
        <view
          class="tab-item"
          :class="{ active: isLogin }"
          @click="switchTab(true)"
        >
          登录
        </view>
        <view
          class="tab-item"
          :class="{ active: !isLogin }"
          @click="switchTab(false)"
        >
          注册
        </view>
      </view>

      <view class="form">
        <view class="form-item">
          <text class="label">用户名</text>
          <input
            class="input"
            v-model="formData.username"
            placeholder="请输入用户名"
            placeholder-class="placeholder"
          />
        </view>

        <view class="form-item">
          <text class="label">密码</text>
          <input
            class="input"
            v-model="formData.password"
            type="password"
            placeholder="请输入密码"
            placeholder-class="placeholder"
          />
        </view>

        <view class="form-item" v-if="!isLogin">
          <text class="label">确认密码</text>
          <input
            class="input"
            v-model="formData.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            placeholder-class="placeholder"
          />
        </view>

        <button
          class="submit-btn"
          @click="handleSubmit"
          :loading="loading"
        >
          {{ isLogin ? '登录' : '注册' }}
        </button>

        <view class="tips" v-if="isLogin">
          <text class="tip-text" @click="guestMode">游客模式</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { login, register } from '../../api/auth.js'

export default {
  data() {
    return {
      isLogin: true,
      loading: false,
      formData: {
        username: '',
        password: '',
        confirmPassword: ''
      }
    }
  },

  methods: {
    switchTab(isLogin) {
      this.isLogin = isLogin
      this.formData = {
        username: '',
        password: '',
        confirmPassword: ''
      }
    },

    async handleSubmit() {
      const { username, password, confirmPassword } = this.formData

      if (!username || !password) {
        uni.showToast({
          title: '请填写完整信息',
          icon: 'none'
        })
        return
      }

      if (!this.isLogin && password !== confirmPassword) {
        uni.showToast({
          title: '两次密码不一致',
          icon: 'none'
        })
        return
      }

      this.loading = true

      try {
        if (this.isLogin) {
          await this.handleLogin()
        } else {
          await this.handleRegister()
        }
      } catch (error) {
        console.error(error)
      } finally {
        this.loading = false
      }
    },

    async handleLogin() {
      const res = await login({
        username: this.formData.username,
        password: this.formData.password
      })

      uni.setStorageSync('token', res.access_token)
      uni.setStorageSync('userInfo', res.user)

      uni.showToast({
        title: '登录成功',
        icon: 'success'
      })

      setTimeout(() => {
        uni.switchTab({
          url: '/pages/index/index'
        })
      }, 1500)
    },

    async handleRegister() {
      const res = await register({
        username: this.formData.username,
        password: this.formData.password
      })

      uni.showToast({
        title: '注册成功，请登录',
        icon: 'success'
      })

      setTimeout(() => {
        this.switchTab(true)
      }, 1500)
    },

    guestMode() {
      uni.showModal({
        title: '提示',
        content: '游客模式下只能使用单张识别功能，登录后可使用完整功能',
        success: (res) => {
          if (res.confirm) {
            uni.switchTab({
              url: '/pages/index/index'
            })
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 100rpx 60rpx;
}

.header {
  text-align: center;
  margin-bottom: 80rpx;
}

.title {
  display: block;
  font-size: 48rpx;
  font-weight: bold;
  color: #fff;
  margin-bottom: 20rpx;
}

.subtitle {
  display: block;
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.8);
}

.form-container {
  background: #fff;
  border-radius: 20rpx;
  padding: 60rpx 40rpx;
}

.tab-bar {
  display: flex;
  margin-bottom: 60rpx;
}

.tab-item {
  flex: 1;
  text-align: center;
  font-size: 32rpx;
  color: #999;
  padding-bottom: 20rpx;
  border-bottom: 4rpx solid transparent;
  transition: all 0.3s;
}

.tab-item.active {
  color: #667eea;
  border-bottom-color: #667eea;
  font-weight: bold;
}

.form-item {
  margin-bottom: 40rpx;
}

.label {
  display: block;
  font-size: 28rpx;
  color: #333;
  margin-bottom: 20rpx;
}

.input {
  width: 100%;
  height: 88rpx;
  background: #f5f5f5;
  border-radius: 10rpx;
  padding: 0 30rpx;
  font-size: 28rpx;
}

.placeholder {
  color: #ccc;
}

.submit-btn {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 44rpx;
  font-size: 32rpx;
  border: none;
  margin-top: 40rpx;
}

.tips {
  text-align: center;
  margin-top: 40rpx;
}

.tip-text {
  font-size: 28rpx;
  color: #667eea;
}
</style>
