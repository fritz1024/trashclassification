<template>
  <AdminLayout>
    <div class="admin-page">
      <!-- Page Header -->
      <div class="page-header">
        <h1>识别记录管理</h1>
        <div class="header-actions">
          <el-button
            type="danger"
            :disabled="selectedIds.length === 0"
            @click="handleBatchDelete"
          >
            批量删除 ({{ selectedIds.length }})
          </el-button>
          <el-button type="success" :icon="Download" @click="handleExport" :loading="exportLoading">
            导出数据
          </el-button>
        </div>
      </div>

      <!-- Content Card -->
      <div class="content-card">
        <!-- Toolbar -->
        <div class="toolbar">
          <div class="toolbar-left"></div>
          <div class="toolbar-right">
            <el-input
              v-model="searchClass"
              placeholder="搜索分类"
              style="width: 200px;"
              clearable
              @clear="handleSearch"
              @keyup.enter="handleSearch"
            />
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="handleReset">重置</el-button>
          </div>
        </div>

        <!-- Data Table -->
        <el-table
          :data="predictionList"
          style="width: 100%"
          v-loading="loading"
          stripe
          @selection-change="handleSelectionChange"
          class="admin-table"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column label="序号" width="70">
            <template #default="scope">
              {{ (currentPage - 1) * pageSize + scope.$index + 1 }}
            </template>
          </el-table-column>
          <el-table-column prop="username" label="用户" width="120" />
          <el-table-column label="图片" width="120">
            <template #default="scope">
              <el-image
                style="width: 60px; height: 60px; border-radius: var(--radius-sm);"
                :src="`/${scope.row.image_path}`"
                fit="cover"
                :preview-src-list="[`/${scope.row.image_path}`]"
                preview-teleported
              />
            </template>
          </el-table-column>
          <el-table-column prop="predicted_class" label="分类" />
          <el-table-column prop="confidence" label="置信度" width="100">
            <template #default="scope">
              {{ scope.row.confidence }}%
            </template>
          </el-table-column>
          <el-table-column label="时间" width="180">
            <template #default="scope">
              {{ formatDateTime(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="scope">
              <el-button
                type="danger"
                size="small"
                link
                @click="handleDelete(scope.row.id)"
              >
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
            :page-sizes="[10, 20, 50, 100]"
            :total="total"
            layout="sizes, prev, pager, next"
            @size-change="fetchPredictions"
            @current-change="fetchPredictions"
          />
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAllPredictions, deletePredictionAdmin } from '@/api/admin'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import { formatDateTime } from '@/utils/date'
import * as XLSX from 'xlsx'
import AdminLayout from '@/components/AdminLayout.vue'

const predictionList = ref([])
const loading = ref(false)
const exportLoading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchClass = ref('')
const selectedIds = ref([])

const fetchPredictions = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }

    if (searchClass.value) {
      params.predicted_class = searchClass.value
    }

    const response = await getAllPredictions(params)
    predictionList.value = response.items
    total.value = response.total
  } catch (error) {
    ElMessage.error('获取识别记录失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchPredictions()
}

const handleReset = () => {
  searchClass.value = ''
  currentPage.value = 1
  fetchPredictions()
}

const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map(item => item.id)
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deletePredictionAdmin(id)
    ElMessage.success('删除成功')
    fetchPredictions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedIds.value.length} 条记录吗？`,
      '批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 批量删除
    const deletePromises = selectedIds.value.map(id => deletePredictionAdmin(id))
    await Promise.all(deletePromises)

    ElMessage.success(`成功删除 ${selectedIds.value.length} 条记录`)
    selectedIds.value = []
    fetchPredictions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

// 导出数据
const handleExport = async () => {
  // 检查是否有选中的数据
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请先勾选要导出的数据')
    return
  }

  exportLoading.value = true
  try {
    // 准备导出数据（只导出选中的）
    const exportData = predictionList.value
      .filter(row => selectedIds.value.includes(row.id))
      .map((row, index) => ({
        '序号': index + 1,
        '用户名': row.username,
        '分类结果': row.predicted_class,
        '置信度': `${row.confidence}%`,
        '识别时间': formatDateTime(row.created_at),
        '图片文件名': row.image_path.split('/').pop()
      }))

    // 创建工作表
    const worksheet = XLSX.utils.json_to_sheet(exportData)

    // 创建工作簿
    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, '识别记录')

    // 生成文件并下载
    const filename = `识别记录_${new Date().getTime()}.xlsx`
    XLSX.writeFile(workbook, filename)

    ElMessage.success(`成功导出 ${selectedIds.value.length} 条数据`)
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败，请重试')
  } finally {
    exportLoading.value = false
  }
}

onMounted(() => {
  fetchPredictions()
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

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-5);
  padding: var(--space-4);
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
}

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: var(--space-3);
  align-items: center;
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
