<template>
  <div class="login-page">
    <div class="login-card glass-heavy">
      <div class="login-header">
        <div class="login-logo">
          <div class="logo-icon">
            <el-icon :size="24"><Delete /></el-icon>
          </div>
        </div>
        <h1>{{ isLogin ? '欢迎回来' : '创建账户' }}</h1>
        <p>{{ isLogin ? '登录以继续使用垃圾分类识别系统' : '注册新账户，开始智能垃圾分类之旅' }}</p>
      </div>

      <el-form :model="form" class="login-form" @keyup.enter="handleSubmit">
        <div class="form-group">
          <label>用户名</label>
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            size="large"
            :prefix-icon="User"
          />
        </div>

        <div class="form-group" v-if="!isLogin">
          <label>邮箱 <span class="optional">（选填）</span></label>
          <el-input
            v-model="form.email"
            placeholder="请输入邮箱"
            size="large"
            :prefix-icon="Message"
          />
        </div>

        <div class="form-group">
          <label>密码</label>
          <el-input
            v-model="form.password"
            type="password"
            show-password
            :placeholder="isLogin ? '请输入密码' : '设置密码（至少6位）'"
            size="large"
            :prefix-icon="Lock"
          />
        </div>

        <el-button
          type="primary"
          size="large"
          round
          @click="handleSubmit"
          :loading="loading"
          class="submit-btn"
        >
          {{ isLogin ? '登 录' : '注 册' }}
        </el-button>
      </el-form>

      <div class="login-footer">
        <span>{{ isLogin ? '还没有账号？' : '已有账号？' }}</span>
        <a href="javascript:;" class="switch-link" @click="isLogin = !isLogin">
          {{ isLogin ? '立即注册' : '立即登录' }}
        </a>
      </div>

      <div class="login-features">
        <div class="feature-tag" v-for="(f, i) in featureTags" :key="i">
          <el-icon :size="14"><Check /></el-icon> {{ f }}
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
import { User, Lock, Message } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const isLogin = ref(true)
const loading = ref(false)
const form = ref({ username: '', password: '', email: '' })

const featureTags = ['265类垃圾识别', 'AI智能助手', '数据统计分析', '识别历史追踪']

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
      const data = { username: form.value.username, password: form.value.password }
      if (form.value.email) data.email = form.value.email
      await userStore.register(data)
      ElMessage.success('注册成功')
      isLogin.value = true
      form.value.password = ''
      form.value.email = ''
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
  min-height: calc(100vh - var(--navbar-height));
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-8);
  background: linear-gradient(160deg, var(--color-primary-lightest) 0%, var(--bg-secondary) 40%, var(--bg-primary) 100%);
}

[data-theme="dark"] .login-page {
  background: linear-gradient(160deg, rgba(16, 185, 129, 0.06) 0%, var(--bg-secondary) 40%, var(--bg-primary) 100%);
}

.login-card {
  width: 100%;
  max-width: 420px;
  padding: var(--space-10);
  border-radius: var(--radius-2xl);
  border: 1px solid var(--border-secondary);
  box-shadow: var(--shadow-xl);
}

.login-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.login-logo {
  display: flex;
  justify-content: center;
  margin-bottom: var(--space-5);
}

.logo-icon {
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  border-radius: var(--radius-lg);
  color: white;
}

.login-header h1 {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}

.login-header p {
  font-size: var(--text-base);
  color: var(--text-tertiary);
}

.form-group {
  margin-bottom: var(--space-5);
}

.form-group label {
  display: block;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  margin-bottom: var(--space-2);
}

.optional {
  color: var(--text-tertiary);
  font-weight: var(--font-normal);
}

.submit-btn {
  width: 100%;
  margin-top: var(--space-3);
  height: 44px;
  font-size: var(--text-md);
  font-weight: var(--font-semibold);
}

.login-footer {
  text-align: center;
  margin-top: var(--space-5);
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}

.switch-link {
  color: var(--color-primary);
  font-weight: var(--font-semibold);
  margin-left: var(--space-1);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.switch-link:hover {
  color: var(--color-primary-dark);
  text-decoration: underline;
}

.login-features {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  justify-content: center;
  margin-top: var(--space-8);
  padding-top: var(--space-6);
  border-top: 1px solid var(--border-secondary);
}

.feature-tag {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-xs);
  color: var(--color-primary);
  background: var(--color-primary-lightest);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-weight: var(--font-medium);
}

@media (max-width: 768px) {
  .login-card {
    padding: var(--space-6);
    max-width: 100%;
  }
}
</style>
