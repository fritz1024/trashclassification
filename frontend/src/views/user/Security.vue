<template>
  <UserLayout>
    <div class="security-page">
      <div class="page-header">
        <h1>账号安全</h1>
      </div>

      <!-- Account Status -->
      <div class="info-section">
        <h3>账号状态</h3>
        <div class="info-card">
          <div class="info-row">
            <div class="info-label"><el-icon><CircleCheck /></el-icon> 账号状态</div>
            <div class="info-value">
              <el-tag :type="userStore.user?.is_active ? 'success' : 'danger'" size="small">
                {{ userStore.user?.is_active ? '正常' : '已禁用' }}
              </el-tag>
            </div>
          </div>
          <div class="info-row">
            <div class="info-label"><el-icon><User /></el-icon> 用户名</div>
            <div class="info-value">{{ userStore.user?.username }}</div>
          </div>
          <div class="info-row last">
            <div class="info-label"><el-icon><Calendar /></el-icon> 注册时间</div>
            <div class="info-value">{{ formatDate(userStore.user?.created_at) }}</div>
          </div>
        </div>
      </div>

      <!-- Change Password -->
      <div class="info-section">
        <h3>修改密码</h3>
        <div class="info-card" style="padding: var(--space-6);">
          <el-form :model="passwordForm" label-position="top" style="max-width: 400px;">
            <el-form-item label="当前密码">
              <el-input v-model="passwordForm.oldPassword" type="password" show-password placeholder="请输入当前密码" />
            </el-form-item>
            <el-form-item label="新密码">
              <el-input v-model="passwordForm.newPassword" type="password" show-password placeholder="至少 6 位" />
              <div class="password-strength" v-if="passwordForm.newPassword">
                <div class="strength-bar">
                  <div class="strength-fill" :style="{ width: strengthPercent + '%', background: strengthColor }"></div>
                </div>
                <span class="strength-text" :style="{ color: strengthColor }">{{ strengthLabel }}</span>
              </div>
            </el-form-item>
            <el-form-item label="确认新密码">
              <el-input v-model="passwordForm.confirmPassword" type="password" show-password placeholder="再次输入新密码" />
              <div v-if="passwordForm.confirmPassword && passwordForm.confirmPassword !== passwordForm.newPassword" class="match-error">
                两次密码输入不一致
              </div>
            </el-form-item>
            <el-button type="primary" round @click="handleUpdatePassword" :loading="passwordLoading" :disabled="!canSubmitPassword">
              确认修改
            </el-button>
          </el-form>
        </div>
      </div>

      <!-- Danger Zone -->
      <div class="info-section">
        <h3>危险操作</h3>
        <div class="danger-card">
          <div class="danger-row">
            <div>
              <strong>退出登录</strong>
              <p>退出当前账号，返回首页</p>
            </div>
            <el-button round type="danger" @click="handleLogout">退出登录</el-button>
          </div>
        </div>
      </div>
    </div>
  </UserLayout>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { updatePassword } from '@/api/auth'
import { ElMessage } from 'element-plus'
import UserLayout from '@/components/UserLayout.vue'

const router = useRouter()
const userStore = useUserStore()
const passwordLoading = ref(false)
const passwordForm = ref({ oldPassword: '', newPassword: '', confirmPassword: '' })

const passwordStrength = computed(() => {
  const p = passwordForm.value.newPassword
  if (!p) return 0
  let score = 0
  if (p.length >= 6) score++
  if (p.length >= 10) score++
  if (/[A-Z]/.test(p)) score++
  if (/[0-9]/.test(p)) score++
  if (/[^A-Za-z0-9]/.test(p)) score++
  return score
})

const strengthPercent = computed(() => (passwordStrength.value / 5) * 100)
const strengthColor = computed(() => {
  const s = passwordStrength.value
  if (s <= 1) return '#ef4444'
  if (s <= 2) return '#f59e0b'
  if (s <= 3) return '#10b981'
  return '#059669'
})
const strengthLabel = computed(() => {
  const s = passwordStrength.value
  if (s <= 1) return '弱'
  if (s <= 2) return '一般'
  if (s <= 3) return '较强'
  return '强'
})

const canSubmitPassword = computed(() => {
  const f = passwordForm.value
  return f.oldPassword && f.newPassword && f.newPassword.length >= 6 && f.newPassword === f.confirmPassword
})

const handleUpdatePassword = async () => {
  if (!canSubmitPassword.value) return
  passwordLoading.value = true
  try {
    await updatePassword({
      old_password: passwordForm.value.oldPassword,
      new_password: passwordForm.value.newPassword
    })
    ElMessage.success('密码修改成功，请重新登录')
    passwordForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
    setTimeout(() => {
      userStore.logout()
      router.push('/login')
    }, 1500)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '密码修改失败')
  } finally {
    passwordLoading.value = false
  }
}

const handleLogout = () => {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/')
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}
</script>

<style scoped>
.security-page { max-width: 640px; }
.page-header { margin-bottom: var(--space-6); }
.page-header h1 { font-size: var(--text-2xl); font-weight: var(--font-bold); color: var(--text-primary); }

.info-section { margin-bottom: var(--space-6); }
.info-section h3 {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-bottom: var(--space-4);
}

.info-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.info-row {
  display: flex;
  align-items: center;
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--border-secondary);
}
.info-row.last { border-bottom: none; }

.info-label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  width: 120px;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-tertiary);
  flex-shrink: 0;
}

.info-value {
  flex: 1;
  font-size: var(--text-base);
  color: var(--text-primary);
}

/* Password Strength */
.password-strength {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-top: var(--space-2);
}

.strength-bar {
  flex: 1;
  height: 4px;
  background: var(--border-secondary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: all var(--transition-normal);
}

.strength-text {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  min-width: 30px;
}

.match-error {
  font-size: var(--text-xs);
  color: var(--color-danger);
  margin-top: var(--space-1);
}

/* Danger Zone */
.danger-card {
  background: var(--bg-elevated);
  border: 1px solid var(--color-danger);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.danger-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-5) var(--space-6);
}

.danger-row strong {
  font-size: var(--text-base);
  color: var(--text-primary);
}

.danger-row p {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  margin-top: var(--space-1);
}

@media (max-width: 768px) {
  .info-row { flex-wrap: wrap; gap: var(--space-2); }
  .info-label { width: 100%; }
  .danger-row { flex-direction: column; gap: var(--space-3); align-items: flex-start; }
}
</style>
