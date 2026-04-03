<template>
  <div class="profile-page container">
    <div class="page-header">
      <h1>个人中心</h1>
    </div>

    <div class="profile-grid">
      <!-- User Info Card -->
      <div class="info-card">
        <div class="avatar-section">
          <div class="avatar-circle">
            <el-icon :size="32"><User /></el-icon>
          </div>
          <h2>{{ userStore.user?.username }}</h2>
          <el-tag round :type="userStore.user?.role === 'super_admin' ? 'danger' : userStore.user?.role === 'admin' ? 'warning' : 'success'">
            {{ userStore.user?.role === 'super_admin' ? '超级管理员' : userStore.user?.role === 'admin' ? '管理员' : '普通用户' }}
          </el-tag>
        </div>

        <div class="info-list">
          <div class="info-item">
            <span class="info-label">邮箱</span>
            <span class="info-value">{{ userStore.user?.email || '未设置' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">注册时间</span>
            <span class="info-value">{{ userStore.user?.created_at || '-' }}</span>
          </div>
        </div>

        <div class="info-actions">
          <el-button type="primary" round @click="showPasswordDialog = true">
            <el-icon><Lock /></el-icon> 修改密码
          </el-button>
          <el-button round type="danger" @click="handleLogout">
            <el-icon><SwitchButton /></el-icon> 退出登录
          </el-button>
        </div>
      </div>
    </div>

    <!-- Password Dialog -->
    <el-dialog v-model="showPasswordDialog" title="修改密码" width="420px" :close-on-click-modal="false">
      <el-form :model="passwordForm" label-width="80px">
        <el-form-item label="旧密码">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password placeholder="请输入旧密码" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.newPassword" type="password" show-password placeholder="请输入新密码（至少6位）" />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password placeholder="再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button round @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" round @click="handleUpdatePassword" :loading="passwordLoading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { updatePassword } from '@/api/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const showPasswordDialog = ref(false)
const passwordLoading = ref(false)
const passwordForm = ref({ oldPassword: '', newPassword: '', confirmPassword: '' })

const handleUpdatePassword = async () => {
  if (!passwordForm.value.oldPassword) { ElMessage.warning('请输入旧密码'); return }
  if (!passwordForm.value.newPassword) { ElMessage.warning('请输入新密码'); return }
  if (passwordForm.value.newPassword.length < 6) { ElMessage.warning('新密码长度不能少于6位'); return }
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) { ElMessage.error('两次密码输入不一致'); return }

  passwordLoading.value = true
  try {
    await updatePassword({ old_password: passwordForm.value.oldPassword, new_password: passwordForm.value.newPassword })
    ElMessage.success('密码修改成功，请重新登录')
    showPasswordDialog.value = false
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
</script>

<style scoped>
.profile-page {
  padding: var(--space-8) var(--space-6);
  max-width: 520px;
}

.page-header {
  margin-bottom: var(--space-6);
}

.page-header h1 {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
}

.info-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
  box-shadow: var(--shadow-sm);
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-6);
  padding-bottom: var(--space-6);
  border-bottom: 1px solid var(--border-secondary);
}

.avatar-circle {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.avatar-section h2 {
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  font-weight: var(--font-medium);
}

.info-value {
  font-size: var(--text-base);
  color: var(--text-primary);
}

.info-actions {
  display: flex;
  gap: var(--space-3);
}

@media (max-width: 768px) {
  .profile-page { padding: var(--space-4); }
  .info-card { padding: var(--space-5); }
  .info-actions { flex-direction: column; }
}
</style>
