<template>
  <AdminLayout>
    <div class="admin-page">
      <!-- Page Header -->
      <div class="page-header">
        <h1>公告管理</h1>
        <div class="header-actions">
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            新建公告
          </el-button>
        </div>
      </div>

      <!-- Content Card -->
      <div class="content-card">
        <!-- Data Table -->
        <el-table
          :data="announcements"
          v-loading="loading"
          style="width: 100%"
          stripe
          class="admin-table"
        >
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="title" label="标题" min-width="200" />
          <el-table-column prop="type" label="类型" width="100">
            <template #default="scope">
              <el-tag :type="getTypeColor(scope.row.type)" size="small">
                {{ getTypeName(scope.row.type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="priority" label="优先级" width="100" />
          <el-table-column prop="is_published" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.is_published ? 'success' : 'info'" size="small">
                {{ scope.row.is_published ? '已发布' : '未发布' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="scope">
              <el-button type="primary" size="small" text @click="handleEdit(scope.row)">
                编辑
              </el-button>
              <el-button type="danger" size="small" text @click="handleDelete(scope.row.id)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- Pagination Bar -->
        <div class="pagination-bar">
          <span class="pagination-info">
            共 {{ total }} 条
          </span>
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[10, 20, 50]"
            layout="sizes, prev, pager, next"
            @size-change="fetchAnnouncements"
            @current-change="fetchAnnouncements"
          />
        </div>
      </div>
    </div>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingId ? '编辑公告' : '新建公告'"
      width="600px"
    >
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="form.title" placeholder="请输入公告标题" />
        </el-form-item>
        <el-form-item label="内容" required>
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="6"
            placeholder="请输入公告内容"
          />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.type" placeholder="请选择类型">
            <el-option label="信息" value="info" />
            <el-option label="警告" value="warning" />
            <el-option label="成功" value="success" />
            <el-option label="错误" value="error" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-input-number v-model="form.priority" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="发布状态">
          <el-switch v-model="form.is_published" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ editingId ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdminLayout from '@/components/AdminLayout.vue'

const announcements = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const showCreateDialog = ref(false)
const submitting = ref(false)
const editingId = ref(null)

const form = ref({
  title: '',
  content: '',
  type: 'info',
  priority: 0,
  is_published: true
})

// 获取公告列表
const fetchAnnouncements = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('/api/announcements/list', {
      params: {
        skip: (currentPage.value - 1) * pageSize.value,
        limit: pageSize.value
      },
      headers: { Authorization: `Bearer ${token}` }
    })
    announcements.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    ElMessage.error('获取公告列表失败')
  } finally {
    loading.value = false
  }
}

// 编辑公告
const handleEdit = (announcement) => {
  editingId.value = announcement.id
  form.value = {
    title: announcement.title,
    content: announcement.content,
    type: announcement.type,
    priority: announcement.priority,
    is_published: announcement.is_published
  }
  showCreateDialog.value = true
}

// 删除公告
const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这条公告吗？', '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const token = localStorage.getItem('token')
    await axios.delete(`/api/announcements/delete/${id}`, {
      headers: { Authorization: `Bearer ${token}` }
    })

    ElMessage.success('删除成功')
    fetchAnnouncements()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!form.value.title || !form.value.content) {
    ElMessage.warning('请填写完整信息')
    return
  }

  submitting.value = true
  try {
    const token = localStorage.getItem('token')

    if (editingId.value) {
      // 更新
      await axios.put(`/api/announcements/update/${editingId.value}`, form.value, {
        headers: { Authorization: `Bearer ${token}` }
      })
      ElMessage.success('更新成功')
    } else {
      // 创建
      await axios.post('/api/announcements/create', form.value, {
        headers: { Authorization: `Bearer ${token}` }
      })
      ElMessage.success('创建成功')
    }

    showCreateDialog.value = false
    resetForm()
    fetchAnnouncements()
  } catch (error) {
    ElMessage.error(editingId.value ? '更新失败' : '创建失败')
  } finally {
    submitting.value = false
  }
}

// 重置表单
const resetForm = () => {
  editingId.value = null
  form.value = {
    title: '',
    content: '',
    type: 'info',
    priority: 0,
    is_published: true
  }
}

// 获取类型颜色
const getTypeColor = (type) => {
  const colors = {
    info: '',
    warning: 'warning',
    success: 'success',
    error: 'danger'
  }
  return colors[type] || ''
}

// 获取类型名称
const getTypeName = (type) => {
  const names = {
    info: '信息',
    warning: '警告',
    success: '成功',
    error: '错误'
  }
  return names[type] || type
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  fetchAnnouncements()
})
</script>

<style scoped>
.admin-page {
  padding: 0;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-6);
}

.page-header h1 {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: var(--space-3);
}

.content-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
}

.admin-table {
  border-radius: var(--radius-md);
  overflow: hidden;
}

.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: var(--space-5);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-secondary);
}

.pagination-info {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}
</style>
