<template>
  <div class="login-page">
    <div class="login-card glass-heavy">
      <div class="login-header">
        <div class="login-logo">
          <div class="logo-icon">
            <el-icon :size="24"><Setting /></el-icon>
          </div>
        </div>
        <h1>管理后台</h1>
        <p>登录以进入垃圾分类识别管理系统</p>
      </div>

      <el-form :model="loginForm" class="login-form" @keyup.enter="handleLogin">
        <div class="form-group">
          <label>用户名</label>
          <el-input
            v-model="loginForm.username"
            placeholder="请输入管理员用户名"
            size="large"
            :prefix-icon="User"
          />
        </div>

        <div class="form-group">
          <label>密码</label>
          <el-input
            v-model="loginForm.password"
            :type="passwordVisible ? 'text' : 'password'"
            placeholder="请输入密码"
            size="large"
            :prefix-icon="Lock"
            @keyup.enter="handleLogin"
          >
            <template #suffix>
              <el-icon @click="passwordVisible = !passwordVisible" style="cursor: pointer;">
                <View v-if="!passwordVisible" />
                <Hide v-else />
              </el-icon>
            </template>
          </el-input>
        </div>

        <el-button
          type="primary"
          size="large"
          round
          @click="handleLogin"
          :loading="loginLoading"
          class="submit-btn"
        >
          登 录
        </el-button>
      </el-form>

      <div class="login-footer">
        <el-button text type="primary" @click="$router.push('/login')">
          返回用户端登录
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const loginForm = ref({
  username: '',
  password: ''
})
const loginLoading = ref(false)
const passwordVisible = ref(false)

const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    ElMessage.warning('请填写完整信息')
    return
  }

  loginLoading.value = true
  try {
    await userStore.login(loginForm.value)

    if (userStore.user?.role !== 'admin') {
      ElMessage.error('需要管理员权限')
      userStore.logout()
      return
    }

    ElMessage.success('登录成功')
    router.push('/admin/dashboard')
  } catch (error) {
    ElMessage.error('登录失败')
  } finally {
    loginLoading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
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

@media (max-width: 768px) {
  .login-card {
    padding: var(--space-6);
    max-width: 100%;
  }
}
</style>
