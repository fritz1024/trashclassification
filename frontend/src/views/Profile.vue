<template>
  <div class="profile">
    <el-card>
      <template #header>
        <h2>个人中心</h2>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="用户名">
          {{ userStore.user?.username }}
        </el-descriptions-item>
        <el-descriptions-item label="邮箱">
          {{ userStore.user?.email || '未设置' }}
        </el-descriptions-item>
        <el-descriptions-item label="角色">
          <el-tag>{{ userStore.user?.role === 'admin' ? '管理员' : '普通用户' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="注册时间">
          {{ userStore.user?.created_at }}
        </el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <el-button type="primary" @click="showPasswordDialog = true">
        修改密码
      </el-button>
    </el-card>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="showPasswordDialog" title="修改密码" width="400px">
      <el-form :model="passwordForm" label-width="100px">
        <el-form-item label="旧密码">
          <el-input
            v-model="passwordForm.oldPassword"
            :type="oldPasswordVisible ? 'text' : 'password'"
            placeholder="请输入旧密码"
          >
            <template #suffix>
              <el-icon @click="oldPasswordVisible = !oldPasswordVisible" style="cursor: pointer;">
                <View v-if="!oldPasswordVisible" />
                <Hide v-else />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="新密码">
          <el-input
            v-model="passwordForm.newPassword"
            :type="newPasswordVisible ? 'text' : 'password'"
            placeholder="请输入新密码"
          >
            <template #suffix>
              <el-icon @click="newPasswordVisible = !newPasswordVisible" style="cursor: pointer;">
                <View v-if="!newPasswordVisible" />
                <Hide v-else />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input
            v-model="passwordForm.confirmPassword"
            :type="confirmPasswordVisible ? 'text' : 'password'"
            placeholder="请再次输入新密码"
          >
            <template #suffix>
              <el-icon @click="confirmPasswordVisible = !confirmPasswordVisible" style="cursor: pointer;">
                <View v-if="!confirmPasswordVisible" />
                <Hide v-else />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpdatePassword" :loading="passwordLoading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useUserStore } from '@/store/user'
import { updatePassword } from '@/api/auth'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const showPasswordDialog = ref(false)
const passwordLoading = ref(false)
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})
const oldPasswordVisible = ref(false)
const newPasswordVisible = ref(false)
const confirmPasswordVisible = ref(false)

const handleUpdatePassword = async () => {
  // 验证表单
  if (!passwordForm.value.oldPassword) {
    ElMessage.warning('请输入旧密码')
    return
  }

  if (!passwordForm.value.newPassword) {
    ElMessage.warning('请输入新密码')
    return
  }

  if (passwordForm.value.newPassword.length < 6) {
    ElMessage.warning('新密码长度不能少于6位')
    return
  }

  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    ElMessage.error('两次密码输入不一致')
    return
  }

  passwordLoading.value = true
  try {
    await updatePassword({
      old_password: passwordForm.value.oldPassword,
      new_password: passwordForm.value.newPassword
    })

    ElMessage.success('密码修改成功，请重新登录')
    showPasswordDialog.value = false
    passwordForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }

    // 登出并跳转到首页
    setTimeout(() => {
      userStore.logout()
      window.location.href = '/'
    }, 1500)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '密码修改失败')
  } finally {
    passwordLoading.value = false
  }
}
</script>

<style scoped>
.profile {
  max-width: 800px;
  margin: 0 auto;
}
</style>
