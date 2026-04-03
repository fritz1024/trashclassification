<template>
  <AdminLayout>
    <div class="admin-page">
      <!-- Page Header -->
      <div class="page-header">
        <h1>公告管理</h1>
        <div class="header-actions">
          <el-button
            type="danger"
            :disabled="selectedIds.length === 0"
            @click="handleBatchDelete"
          >
            批量删除 ({{ selectedIds.length }})
          </el-button>
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
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column label="序号" width="70">
            <template #default="scope">
              {{ (currentPage - 1) * pageSize + scope.$index + 1 }}
            </template>
          </el-table-column>
          <el-table-column prop="title" label="标题" min-width="200" />
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
            第 {{ (currentPage - 1) * pageSize + 1 }}-{{ Math.min(currentPage * pageSize, total) }} 条，共 {{ total }} 条
          </span>
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[10, 20, 50, 100]"
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
          <div style="border: 1px solid var(--border-primary); border-radius: var(--radius-md);">
            <Toolbar :editor="editorRef" :defaultConfig="toolbarConfig" mode="default" style="border-bottom: 1px solid var(--border-primary)" />
            <Editor v-model="form.content" :defaultConfig="editorConfig" mode="default" style="height: 400px; overflow-y: hidden;" @onCreated="handleCreated" />
          </div>
        </el-form-item>
        <el-form-item label="发布状态">
          <el-switch v-model="form.is_published" active-text="发布" inactive-text="草稿" />
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
import { ref, onMounted, shallowRef, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdminLayout from '@/components/AdminLayout.vue'
import { getAnnouncements, createAnnouncement, updateAnnouncement, deleteAnnouncement } from '@/api/announcement'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import '@wangeditor/editor/dist/css/style.css'

const announcements = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const showCreateDialog = ref(false)
const submitting = ref(false)
const editingId = ref(null)
const selectedIds = ref([])

const form = ref({
  title: '',
  content: '',
  is_published: true
})

const editorRef = shallowRef()
const toolbarConfig = {}
const editorConfig = { placeholder: '请输入公告内容...' }

const handleCreated = (editor) => {
  editorRef.value = editor
}

// 获取公告列表
const fetchAnnouncements = async () => {
  loading.value = true
  try {
    const response = await getAnnouncements({
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    })
    announcements.value = response.items
    total.value = response.total
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

    await deleteAnnouncement(id)
    ElMessage.success('删除成功')
    fetchAnnouncements()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map(item => item.id)
}

const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedIds.value.length} 条公告吗？`, '批量删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await Promise.all(selectedIds.value.map(id => deleteAnnouncement(id)))
    ElMessage.success('批量删除成功')
    selectedIds.value = []
    fetchAnnouncements()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
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
    if (editingId.value) {
      await updateAnnouncement(editingId.value, form.value)
      ElMessage.success('更新成功')
    } else {
      await createAnnouncement(form.value)
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
    is_published: true
  }
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

onBeforeUnmount(() => {
  if (editorRef.value) {
    editorRef.value.destroy()
  }
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
