<template>
  <div class="login-page">
    <div class="login-container">
      <div class="left-panel">
        <div class="brand">
          <el-icon size="24"><Delete /></el-icon>
          <span>RubbishCheck AI</span>
          <span class="subtitle">Garbage Image Recognition System</span>
        </div>

        <div class="features-list">
          <div class="feature-badge">基于深度学习的分类平台</div>
          <h2>登录后开始垃圾图像识别</h2>
          <p>上传图片，即时识别。让AI为您提供精准的垃圾分类指导（识别、统计、干电池）与垃圾数据统计，并支持导出生成报告。</p>

          <div class="stats">
            <div class="stat-item">
              <div class="stat-number">10</div>
              <div class="stat-label">Waste Classified</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">AI</div>
              <div class="stat-label">Intelligence</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">Logs</div>
              <div class="stat-label">History Track</div>
            </div>
          </div>

          <ul class="feature-items">
            <li><el-icon><Check /></el-icon> 10类垃圾实时识别</li>
            <li><el-icon><Check /></el-icon> 智能数据统计分析</li>
            <li><el-icon><Check /></el-icon> 历史记录追踪</li>
            <li><el-icon><Check /></el-icon> 多端数据同步</li>
          </ul>

          <div class="extra-features">
            <div><el-icon><Check /></el-icon> 精准度高达90%</div>
            <div><el-icon><Check /></el-icon> 持续数据更新</div>
            <div><el-icon><Check /></el-icon> 环保知识库</div>
            <div><el-icon><Check /></el-icon> 社区互动分享</div>
          </div>
        </div>
      </div>

      <div class="right-panel">
        <div class="form-container">
          <h2>{{ isLogin ? '欢迎回来' : '创建账户' }}</h2>
          <p class="form-subtitle">{{ isLogin ? '输入账号密码，继续使用垃圾分类识别系统' : '注册新账户，开始使用垃圾分类识别系统' }}</p>

          <el-form :model="form" class="login-form">
            <el-form-item label="用户名">
              <el-input v-model="form.username" placeholder="请输入用户名" size="large" />
            </el-form-item>

            <el-form-item label="密码">
              <el-input v-model="form.password" type="password" :placeholder="isLogin ? '请输入密码（至少6位数字/字母）' : '设置密码（至少6位）'" size="large" />
            </el-form-item>

            <el-button type="success" size="large" @click="handleSubmit" :loading="loading" style="width: 100%; margin-top: 10px;">
              {{ isLogin ? '登录系统' : '注册账户' }}
            </el-button>

            <div class="form-footer">
              <span>{{ isLogin ? '还没有账号？' : '已有账号？' }}</span>
              <el-button text type="success" @click="isLogin = !isLogin">
                {{ isLogin ? '立即注册' : '立即登录' }}
              </el-button>
            </div>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const isLogin = ref(true)
const loading = ref(false)
const form = ref({
  username: '',
  password: ''
})

const handleSubmit = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请填写完整信息')
    return
  }

  loading.value = true
  try {
    if (isLogin.value) {
      await userStore.login(form.value)
      ElMessage.success('登录成功')
      router.push('/')
    } else {
      await userStore.register(form.value)
      ElMessage.success('注册成功')
      isLogin.value = true
      form.value.password = ''
    }
  } catch (error) {
    ElMessage.error(error.message || (isLogin.value ? '登录失败' : '注册失败'))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-container {
  display: flex;
  max-width: 1100px;
  width: 100%;
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.left-panel {
  flex: 1;
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  color: white;
  padding: 50px 40px;
}

.brand {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-bottom: 40px;
}

.brand span:first-of-type {
  font-size: 20px;
  font-weight: bold;
}

.brand .subtitle {
  font-size: 12px;
  opacity: 0.9;
}

.feature-badge {
  display: inline-block;
  background: rgba(255, 255, 255, 0.2);
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  margin-bottom: 20px;
}

.features-list h2 {
  font-size: 28px;
  margin-bottom: 15px;
  line-height: 1.3;
}

.features-list > p {
  font-size: 14px;
  line-height: 1.6;
  opacity: 0.95;
  margin-bottom: 30px;
}

.stats {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}

.stat-item {
  flex: 1;
  background: rgba(255, 255, 255, 0.15);
  padding: 15px;
  border-radius: 8px;
  text-align: center;
}

.stat-number {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 11px;
  opacity: 0.9;
}

.feature-items {
  list-style: none;
  padding: 0;
  margin-bottom: 25px;
}

.feature-items li {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  font-size: 14px;
}

.extra-features {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  font-size: 13px;
}

.extra-features div {
  display: flex;
  align-items: center;
  gap: 8px;
}

.right-panel {
  flex: 1;
  padding: 50px 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-container {
  width: 100%;
  max-width: 400px;
}

.form-container h2 {
  font-size: 28px;
  color: #1f2937;
  margin-bottom: 8px;
}

.form-subtitle {
  color: #6b7280;
  font-size: 14px;
  margin-bottom: 30px;
}

.login-form {
  margin-top: 20px;
}

.form-footer {
  text-align: center;
  margin-top: 20px;
  color: #6b7280;
  font-size: 14px;
}
</style>
