<template>
  <div class="admin-page">
    <el-card>
      <!-- 页面标题 -->
      <template #header>
        <div class="page-header">
          <h3>知识库管理</h3>
        </div>
      </template>

      <!-- 操作栏 -->
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button type="primary" @click="handleAdd">添加知识</el-button>
          <el-button
            type="danger"
            :disabled="selectedIds.length === 0"
            @click="handleBatchDelete"
          >
            批量删除 ({{ selectedIds.length }})
          </el-button>
        </div>
        <div class="toolbar-right">
          <el-select v-model="categoryFilter" placeholder="分类筛选" clearable style="width: 150px;" @change="handleFilterChange">
            <el-option label="全部" value="" />
            <el-option label="可回收垃圾" value="recyclable" />
            <el-option label="有害垃圾" value="harmful" />
            <el-option label="厨余垃圾" value="kitchen" />
            <el-option label="其他垃圾" value="other" />
          </el-select>
        </div>
      </div>

      <!-- 数据表格 -->
      <el-table
        :data="knowledgeList"
        style="width: 100%"
        v-loading="loading"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column label="序号" width="80">
          <template #default="scope">
            {{ (currentPage - 1) * pageSize + scope.$index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="120">
          <template #default="scope">
            <el-tag>{{ getCategoryName(scope.row.category) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="150" />
        <el-table-column prop="content" label="内容" min-width="200" show-overflow-tooltip />
        <el-table-column label="创建时间" width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              @click="handleEdit(scope.row)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(scope.row.id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <span class="pagination-info">
          第 {{ (currentPage - 1) * pageSize + 1 }}-{{ Math.min(currentPage * pageSize, total) }} 条，共 {{ total }} 条
        </span>
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="sizes, prev, pager, next"
          @size-change="fetchKnowledge"
          @current-change="fetchKnowledge"
        />
      </div>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingId ? '编辑知识' : '添加知识'"
      width="600px"
    >
      <el-form :model="knowledgeForm" label-width="80px">
        <el-form-item label="分类">
          <el-select v-model="knowledgeForm.category" placeholder="请选择分类">
            <el-option label="可回收垃圾" value="recyclable" />
            <el-option label="有害垃圾" value="harmful" />
            <el-option label="厨余垃圾" value="kitchen" />
            <el-option label="其他垃圾" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="knowledgeForm.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input
            v-model="knowledgeForm.content"
            type="textarea"
            :rows="5"
            placeholder="请输入内容"
          />
        </el-form-item>
        <el-form-item label="示例">
          <el-input
            v-model="knowledgeForm.examples"
            type="textarea"
            :rows="3"
            placeholder="请输入示例（可选）"
          />
        </el-form-item>
        <el-form-item label="处理建议">
          <el-input
            v-model="knowledgeForm.tips"
            type="textarea"
            :rows="3"
            placeholder="请输入处理建议（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saveLoading">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAllKnowledgeAdmin, createKnowledge, updateKnowledge, deleteKnowledge } from '@/api/admin'
import { ElMessage, ElMessageBox } from 'element-plus'
import { formatDateTime } from '@/utils/date'

const knowledgeList = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const showAddDialog = ref(false)
const saveLoading = ref(false)
const editingId = ref(null)
const selectedIds = ref([])
const categoryFilter = ref('')

const knowledgeForm = ref({
  category: '',
  title: '',
  content: '',
  examples: '',
  tips: ''
})

const categoryMap = {
  recyclable: '可回收垃圾',
  harmful: '有害垃圾',
  kitchen: '厨余垃圾',
  other: '其他垃圾'
}

const getCategoryName = (category) => {
  return categoryMap[category] || category
}

const fetchKnowledge = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }

    if (categoryFilter.value) {
      params.category = categoryFilter.value
    }

    const response = await getAllKnowledgeAdmin(params)
    console.log('知识库API响应:', response)
    console.log('items:', response.items)
    console.log('total:', response.total)

    knowledgeList.value = response.items
    total.value = response.total
  } catch (error) {
    console.error('获取知识列表失败:', error)
    ElMessage.error('获取知识列表失败')
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  currentPage.value = 1
  fetchKnowledge()
}

const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map(item => item.id)
}

const handleAdd = () => {
  resetForm()
  showAddDialog.value = true
}

const handleEdit = (row) => {
  editingId.value = row.id
  knowledgeForm.value = {
    category: row.category,
    title: row.title,
    content: row.content,
    examples: row.examples || '',
    tips: row.tips || ''
  }
  showAddDialog.value = true
}

const handleCancel = () => {
  showAddDialog.value = false
  resetForm()
}

const handleSave = async () => {
  if (!knowledgeForm.value.category || !knowledgeForm.value.title || !knowledgeForm.value.content) {
    ElMessage.warning('请填写必填项')
    return
  }

  saveLoading.value = true
  try {
    if (editingId.value) {
      await updateKnowledge(editingId.value, knowledgeForm.value)
      ElMessage.success('更新成功')
    } else {
      await createKnowledge(knowledgeForm.value)
      ElMessage.success('添加成功')
    }

    showAddDialog.value = false
    resetForm()
    fetchKnowledge()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saveLoading.value = false
  }
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这条知识吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteKnowledge(id)
    ElMessage.success('删除成功')
    fetchKnowledge()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedIds.value.length} 条知识吗？`,
      '批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const promises = selectedIds.value.map(id => deleteKnowledge(id))
    await Promise.all(promises)

    ElMessage.success(`成功删除 ${selectedIds.value.length} 条知识`)
    selectedIds.value = []
    fetchKnowledge()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const resetForm = () => {
  editingId.value = null
  knowledgeForm.value = {
    category: '',
    title: '',
    content: '',
    examples: '',
    tips: ''
  }
}

onMounted(() => {
  fetchKnowledge()
})
</script>

<style scoped>
.admin-page {
  /* 统一的管理页面样式 */
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px;
  background-color: var(--theme-card-bg);
  border-radius: 4px;
}

.toolbar-left {
  display: flex;
  gap: 10px;
}

.toolbar-right {
  display: flex;
  gap: 10px;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
}

.pagination-info {
  font-size: 14px;
  color: #606266;
}
</style>
