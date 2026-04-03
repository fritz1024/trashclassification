<template>
  <AdminLayout>
    <div class="admin-page">
      <!-- Page Header -->
      <div class="page-header">
        <h1>知识库管理</h1>
        <div class="header-actions">
          <el-button
            type="danger"
            :disabled="selectedIds.length === 0"
            @click="handleBatchDelete"
          >
            批量删除 ({{ selectedIds.length }})
          </el-button>
          <el-button type="primary" @click="uploadDialogVisible = true">
            <el-icon><UploadFilled /></el-icon>
            上传文档
          </el-button>
        </div>
      </div>

      <!-- Content Card -->
      <div class="content-card">
        <el-table :data="documents" v-loading="loading" @selection-change="handleSelectionChange" stripe class="admin-table">
          <el-table-column type="selection" width="55" />
          <el-table-column label="序号" width="70">
            <template #default="scope">
              {{ (currentPage - 1) * pageSize + scope.$index + 1 }}
            </template>
          </el-table-column>
          <el-table-column prop="original_filename" label="文件名" min-width="200" />
          <el-table-column prop="file_type" label="类型" width="80" />
          <el-table-column prop="file_size" label="大小" width="100">
            <template #default="{ row }">{{ formatSize(row.file_size) }}</template>
          </el-table-column>
          <el-table-column prop="chunk_count" label="分块数" width="100" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="上传时间" width="180">
            <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="handleEdit(row.id)">编辑</el-button>
              <el-button link type="danger" @click="handleDelete(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

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
            @current-change="loadDocuments"
            @size-change="loadDocuments"
          />
        </div>
      </div>

      <!-- 编辑对话框 -->
      <el-dialog v-model="editDialogVisible" title="编辑文档" width="900px">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="编辑" name="edit">
            <el-input
              v-model="editContent"
              type="textarea"
              :rows="20"
              placeholder="请输入文档内容（支持 Markdown）"
            />
          </el-tab-pane>
          <el-tab-pane label="预览" name="preview">
            <div class="markdown-preview" v-html="renderMarkdown(editContent)"></div>
          </el-tab-pane>
        </el-tabs>
        <template #footer>
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveEdit" :loading="saving">保存</el-button>
        </template>
      </el-dialog>

      <!-- 上传对话框 -->
      <el-dialog v-model="uploadDialogVisible" title="上传文档" width="600px">
        <el-upload
          drag
          :auto-upload="false"
          :on-change="handleFileChange"
          accept=".md,.txt"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">拖拽文件到此处或<em>点击上传</em></div>
          <template #tip>
            <div class="el-upload__tip">
              支持 .md 和 .txt 文件，大小不超过 10MB<br>
              <span style="color: var(--color-warning)">提示：首次上传需要下载模型，处理时间约 2-5 分钟</span>
            </div>
          </template>
        </el-upload>
      </el-dialog>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import AdminLayout from '@/components/AdminLayout.vue'
import { uploadDocument, getDocuments, deleteDocument, getDocumentContent, updateDocument } from '@/api/knowledge'
import { useUserStore } from '@/store/user'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({ html: false, linkify: true, breaks: true })
const userStore = useUserStore()
const documents = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const editDialogVisible = ref(false)
const editContent = ref('')
const editingId = ref(null)
const saving = ref(false)
const activeTab = ref('edit')
const selectedIds = ref([])
const uploadDialogVisible = ref(false)

const renderMarkdown = (content) => md.render(content || '')

const loadDocuments = async () => {
  loading.value = true
  try {
    const res = await getDocuments({ skip: (currentPage.value - 1) * pageSize.value, limit: pageSize.value })
    documents.value = res.items
    total.value = res.total
  } catch (error) {
    ElMessage.error('加载文档列表失败')
  } finally {
    loading.value = false
  }
}

const handleFileChange = async (file) => {
  const rawFile = file.raw

  // 验证文件
  const isValid = rawFile.name.endsWith('.md') || rawFile.name.endsWith('.txt')
  const isLt10M = rawFile.size / 1024 / 1024 < 10

  if (!isValid) {
    ElMessage.error('只支持 .md 和 .txt 文件')
    return
  }
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB')
    return
  }

  // 上传文件
  const formData = new FormData()
  formData.append('file', rawFile)

  try {
    await uploadDocument(formData)
    ElMessage.success('文档上传成功，正在后台处理中...')
    loadDocuments()

    // 启动轮询
    let pollCount = 0
    const pollInterval = setInterval(() => {
      pollCount++
      loadDocuments()
      if (pollCount >= 12) clearInterval(pollInterval)
    }, 5000)
  } catch (error) {
    ElMessage.error('文档上传失败')
  }
}

const handleEdit = async (id) => {
  try {
    const res = await getDocumentContent(id)
    editContent.value = res.content
    editingId.value = id
    editDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取文档内容失败')
  }
}

const saveEdit = async () => {
  if (!editContent.value.trim()) {
    ElMessage.warning('文档内容不能为空')
    return
  }

  saving.value = true
  try {
    await updateDocument(editingId.value, editContent.value)
    ElMessage.success('文档更新成功，正在重新处理...')
    editDialogVisible.value = false
    loadDocuments()
  } catch (error) {
    ElMessage.error('更新文档失败')
  } finally {
    saving.value = false
  }
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个文档吗？', '提示', { type: 'warning' })
    await deleteDocument(id)
    ElMessage.success('文档已删除')
    loadDocuments()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}

const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map(item => item.id)
}

const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedIds.value.length} 个文档吗？`, '批量删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await Promise.all(selectedIds.value.map(id => deleteDocument(id)))
    ElMessage.success('批量删除成功')
    selectedIds.value = []
    loadDocuments()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('批量删除失败')
  }
}

const formatSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(1) + ' MB'
}

const formatTime = (time) => {
  return new Date(time).toLocaleString('zh-CN')
}

const getStatusType = (status) => {
  const map = { pending: 'warning', processed: 'success', failed: 'danger' }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = { pending: '处理中', processed: '已完成', failed: '失败' }
  return map[status] || status
}

onMounted(() => loadDocuments())
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

.markdown-preview {
  min-height: 400px;
  max-height: 600px;
  overflow-y: auto;
  padding: var(--space-4);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  background: var(--bg-secondary);
}

.markdown-preview :deep(h1), .markdown-preview :deep(h2), .markdown-preview :deep(h3) {
  margin: var(--space-3) 0 var(--space-2);
  font-weight: var(--font-semibold);
}

.markdown-preview :deep(p) { margin: var(--space-2) 0; line-height: 1.6; }
.markdown-preview :deep(ul), .markdown-preview :deep(ol) { margin: var(--space-2) 0; padding-left: var(--space-6); }
.markdown-preview :deep(code) { background: var(--bg-tertiary); padding: 2px 6px; border-radius: var(--radius-xs); font-family: monospace; color: var(--text-primary); }
.markdown-preview :deep(pre) { background: var(--bg-tertiary); color: var(--text-primary); padding: var(--space-3); border-radius: var(--radius-sm); overflow-x: auto; border: 1px solid var(--border-primary); }
.markdown-preview :deep(pre code) { background: transparent; color: inherit; }
.markdown-preview :deep(blockquote) { border-left: 3px solid var(--color-primary); padding-left: var(--space-3); color: var(--text-secondary); margin: var(--space-2) 0; }
</style>
