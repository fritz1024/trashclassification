<template>
  <UserLayout>
    <div class="profile-page">
      <div class="page-header">
        <h1>个人信息</h1>
      </div>

      <!-- Avatar + Basic Info -->
      <div class="profile-hero">
        <div class="avatar-wrapper" @click="triggerAvatarUpload">
          <div class="avatar-large" v-if="!avatarUrl">
            <span>{{ initial }}</span>
          </div>
          <img v-else :src="avatarUrl" class="avatar-img" alt="头像" />
          <div class="avatar-overlay">
            <el-icon :size="20"><Camera /></el-icon>
            <span>更换头像</span>
          </div>
          <input ref="avatarInput" type="file" accept="image/*" style="display: none;" @change="handleAvatarChange" />
        </div>
        <div class="hero-info">
          <h2>{{ userStore.user?.username }}</h2>
          <div class="hero-meta">
            <el-tag round :type="userStore.user?.role === 'super_admin' ? 'danger' : userStore.user?.role === 'admin' ? 'warning' : 'success'">
              {{ userStore.user?.role === 'super_admin' ? '超级管理员' : userStore.user?.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
            <span class="meta-text">注册于 {{ formatDate(userStore.user?.created_at) }}</span>
          </div>
        </div>
      </div>

      <!-- Info Cards -->
      <div class="info-section">
        <h3>基本信息</h3>
        <div class="info-card">
          <!-- Username (readonly) -->
          <div class="info-row">
            <div class="info-label">
              <el-icon><User /></el-icon> 用户名
            </div>
            <div class="info-value">{{ userStore.user?.username }}</div>
            <div class="info-action">
              <el-tag type="info" size="small">不可修改</el-tag>
            </div>
          </div>

          <!-- Email (editable) -->
          <div class="info-row">
            <div class="info-label">
              <el-icon><Message /></el-icon> 邮箱
            </div>
            <div class="info-value" v-if="!editingEmail">
              {{ userStore.user?.email || '未设置' }}
            </div>
            <el-input
              v-else
              v-model="emailForm.email"
              placeholder="请输入邮箱"
              size="small"
              style="max-width: 280px;"
              @keyup.enter="saveEmail"
            />
            <div class="info-action">
              <template v-if="!editingEmail">
                <a href="javascript:;" class="action-link" @click="startEditEmail">修改</a>
              </template>
              <template v-else>
                <a href="javascript:;" class="action-link save" @click="saveEmail">保存</a>
                <a href="javascript:;" class="action-link cancel" @click="editingEmail = false">取消</a>
              </template>
            </div>
          </div>

          <!-- Role -->
          <div class="info-row">
            <div class="info-label">
              <el-icon><UserFilled /></el-icon> 角色
            </div>
            <div class="info-value">
              <el-tag :type="userStore.user?.role === 'super_admin' ? 'danger' : userStore.user?.role === 'admin' ? 'warning' : 'success'" size="small">
                {{ userStore.user?.role === 'super_admin' ? '超级管理员' : userStore.user?.role === 'admin' ? '管理员' : '普通用户' }}
              </el-tag>
            </div>
            <div class="info-action"></div>
          </div>

          <!-- Account Status -->
          <div class="info-row">
            <div class="info-label">
              <el-icon><CircleCheck /></el-icon> 账号状态
            </div>
            <div class="info-value">
              <el-tag :type="userStore.user?.is_active ? 'success' : 'danger'" size="small">
                {{ userStore.user?.is_active ? '正常' : '已禁用' }}
              </el-tag>
            </div>
            <div class="info-action"></div>
          </div>

          <!-- Created at -->
          <div class="info-row last">
            <div class="info-label">
              <el-icon><Calendar /></el-icon> 注册时间
            </div>
            <div class="info-value">{{ formatDate(userStore.user?.created_at) }}</div>
            <div class="info-action"></div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="info-section">
        <h3>快捷操作</h3>
        <div class="quick-actions">
          <div class="quick-card" @click="$router.push('/user/history')">
            <el-icon :size="24" color="var(--color-primary)"><List /></el-icon>
            <span>识别历史</span>
            <el-icon class="arrow"><ArrowRight /></el-icon>
          </div>
          <div class="quick-card" @click="$router.push('/user/stats')">
            <el-icon :size="24" color="var(--color-accent)"><DataAnalysis /></el-icon>
            <span>数据统计</span>
            <el-icon class="arrow"><ArrowRight /></el-icon>
          </div>
          <div class="quick-card" @click="$router.push('/user/security')">
            <el-icon :size="24" color="var(--color-warning)"><Lock /></el-icon>
            <span>账号安全</span>
            <el-icon class="arrow"><ArrowRight /></el-icon>
          </div>
          <div class="quick-card" @click="$router.push('/classify')">
            <el-icon :size="24" color="var(--color-success)"><Camera /></el-icon>
            <span>去识别垃圾</span>
            <el-icon class="arrow"><ArrowRight /></el-icon>
          </div>
        </div>
      </div>
    </div>
  </UserLayout>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '@/store/user'
import { updateProfile, uploadAvatar } from '@/api/auth'
import { ElMessage } from 'element-plus'
import UserLayout from '@/components/UserLayout.vue'

const userStore = useUserStore()

const initial = computed(() => {
  const name = userStore.user?.username || 'U'
  return name.charAt(0).toUpperCase()
})

const avatarUrl = computed(() => {
  if (!userStore.user?.avatar) return ''
  return '/' + userStore.user.avatar
})

const avatarInput = ref(null)

const triggerAvatarUpload = () => {
  avatarInput.value?.click()
}

const handleAvatarChange = async (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.warning('头像文件不能超过 2MB')
    return
  }
  const formData = new FormData()
  formData.append('file', file)
  try {
    const result = await uploadAvatar(formData)
    userStore.user.avatar = result.avatar
    ElMessage.success('头像更新成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '头像上传失败')
  }
  e.target.value = ''
}

const editingEmail = ref(false)
const emailForm = ref({ email: '' })

const startEditEmail = () => {
  emailForm.value.email = userStore.user?.email || ''
  editingEmail.value = true
}

const saveEmail = async () => {
  try {
    const result = await updateProfile({ email: emailForm.value.email || null })
    userStore.user.email = result.email
    editingEmail.value = false
    ElMessage.success('邮箱更新成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '更新失败')
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}
</script>

<style scoped>
.page-header {
  margin-bottom: var(--space-6);
}

.page-header h1 {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
}

/* Hero */
.profile-hero {
  display: flex;
  align-items: center;
  gap: var(--space-6);
  background: var(--bg-elevated);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
  margin-bottom: var(--space-6);
  box-shadow: var(--shadow-sm);
}

.avatar-wrapper {
  position: relative;
  cursor: pointer;
  flex-shrink: 0;
}

.avatar-large {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
}

.avatar-img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  display: block;
}

.avatar-overlay {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  color: white;
  font-size: var(--text-xs);
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.avatar-wrapper:hover .avatar-overlay {
  opacity: 1;
}

.hero-info h2 {
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}

.hero-meta {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.meta-text {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}

/* Info Section */
.info-section {
  margin-bottom: var(--space-6);
}

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

.info-row.last {
  border-bottom: none;
}

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

.info-action {
  display: flex;
  gap: var(--space-3);
  flex-shrink: 0;
}

.action-link {
  font-size: var(--text-sm);
  color: var(--color-primary);
  font-weight: var(--font-medium);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.action-link:hover {
  color: var(--color-primary-dark);
}

.action-link.cancel {
  color: var(--text-tertiary);
}

.action-link.cancel:hover {
  color: var(--text-secondary);
}

/* Quick Actions */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-3);
}

.quick-card {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  background: var(--bg-elevated);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-lg);
  padding: var(--space-4) var(--space-5);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.quick-card:hover {
  border-color: var(--color-primary-lighter);
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}

.quick-card span {
  flex: 1;
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.quick-card .arrow {
  color: var(--text-tertiary);
}

@media (max-width: 768px) {
  .profile-hero {
    flex-direction: column;
    text-align: center;
    padding: var(--space-6);
  }
  .hero-meta { justify-content: center; }
  .info-row { flex-wrap: wrap; gap: var(--space-2); }
  .info-label { width: 100%; }
  .quick-actions { grid-template-columns: 1fr; }
}
</style>
