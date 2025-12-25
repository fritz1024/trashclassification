<template>
  <div class="history">
    <el-card>
      <template #header>
        <div class="header-wrapper">
          <h2>识别历史</h2>
          <div class="header-actions">
            <el-button
              type="danger"
              :icon="Delete"
              @click="handleBatchDelete"
              :disabled="selectedIds.length === 0"
            >
              批量删除 ({{ selectedIds.length }})
            </el-button>
            <el-button
              type="primary"
              :icon="Download"
              @click="handleExport"
              :loading="exportLoading"
            >
              导出数据
            </el-button>
          </div>
        </div>
      </template>

      <!-- 筛选工具栏 -->
      <div class="filter-toolbar">
        <el-form :inline="true" :model="filterForm">
          <el-form-item label="分类">
            <el-select v-model="filterForm.category" placeholder="全部分类" clearable style="width: 150px">
              <el-option label="可回收物" value="可回收物" />
              <el-option label="有害垃圾" value="有害垃圾" />
              <el-option label="厨余垃圾" value="厨余垃圾" />
              <el-option label="其他垃圾" value="其他垃圾" />
            </el-select>
          </el-form-item>
          <el-form-item label="时间范围">
            <el-date-picker
              v-model="filterForm.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              style="width: 240px"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleFilter">筛选</el-button>
            <el-button @click="handleResetFilter">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table
        :data="historyList"
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
        <el-table-column label="图片">
          <template #default="scope">
            <el-image
              style="width: 100px; height: 100px"
              :src="`/${scope.row.image_path}`"
              fit="cover"
            />
          </template>
        </el-table-column>
        <el-table-column prop="predicted_class" label="分类" />
        <el-table-column prop="confidence" label="置信度">
          <template #default="scope">
            {{ scope.row.confidence }}%
          </template>
        </el-table-column>
        <el-table-column label="识别时间" width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button
              type="warning"
              size="small"
              @click="handleShowFeedback(scope.row)"
            >
              反馈
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

      <div class="pagination-wrapper">
        <span class="pagination-info">
          第 {{ (currentPage - 1) * pageSize + 1 }}-{{ Math.min(currentPage * pageSize, total) }} 条，共 {{ total }} 条
        </span>
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="sizes, prev, pager, next"
          @size-change="fetchHistory"
          @current-change="fetchHistory"
        />
      </div>
    </el-card>

    <!-- 反馈对话框 -->
    <el-dialog
      v-model="showFeedbackDialog"
      title="提交识别反馈"
      width="500px"
    >
      <el-form :model="feedbackForm" label-width="100px">
        <el-form-item label="识别结果">
          <el-input v-model="feedbackForm.predicted_class" disabled />
        </el-form-item>
        <el-form-item label="正确分类" required>
          <el-select
            v-model="feedbackForm.correct_class"
            placeholder="请选择正确的垃圾分类"
            style="width: 100%"
          >
            <el-option label="可回收物" value="可回收物" />
            <el-option label="有害垃圾" value="有害垃圾" />
            <el-option label="厨余垃圾" value="厨余垃圾" />
            <el-option label="其他垃圾" value="其他垃圾" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注说明">
          <el-input
            v-model="feedbackForm.comment"
            type="textarea"
            :rows="4"
            placeholder="请描述识别错误的情况（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showFeedbackDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitFeedback" :loading="submittingFeedback">
          提交反馈
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getPredictionHistory, deletePrediction, submitFeedback } from '@/api/predict'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Delete } from '@element-plus/icons-vue'
import { formatDateTime } from '@/utils/date'
import * as XLSX from 'xlsx'

const route = useRoute()
const historyList = ref([])
const loading = ref(false)
const exportLoading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const selectedIds = ref([])
const selectedRows = ref([])

// 筛选条件
const filterForm = ref({
  category: '',
  dateRange: null
})

// 反馈相关
const showFeedbackDialog = ref(false)
const submittingFeedback = ref(false)
const feedbackForm = ref({
  prediction_id: null,
  predicted_class: '',
  correct_class: '',
  comment: ''
})

const fetchHistory = async () => {
  loading.value = true
  try {
    // 构建查询参数
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }

    // 添加筛选条件
    if (filterForm.value.category) {
      params.predicted_class = filterForm.value.category
    }

    if (filterForm.value.dateRange && filterForm.value.dateRange.length === 2) {
      params.start_date = filterForm.value.dateRange[0].toISOString().split('T')[0]
      params.end_date = filterForm.value.dateRange[1].toISOString().split('T')[0]
    }

    const response = await getPredictionHistory(params)
    historyList.value = response.items
    total.value = response.total
  } catch (error) {
    ElMessage.error('获取历史记录失败')
  } finally {
    loading.value = false
  }
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deletePrediction(id)
    ElMessage.success('删除成功')
    fetchHistory()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 筛选
const handleFilter = () => {
  currentPage.value = 1 // 重置到第一页
  fetchHistory()
}

// 重置筛选
const handleResetFilter = () => {
  filterForm.value = {
    category: '',
    dateRange: null
  }
  currentPage.value = 1
  fetchHistory()
}

// 处理选择变化
const handleSelectionChange = (selection) => {
  selectedRows.value = selection
  selectedIds.value = selection.map(row => row.id)
}

// 批量删除
const handleBatchDelete = async () => {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请先选择要删除的记录')
    return
  }

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

    // 逐个删除
    for (const id of selectedIds.value) {
      await deletePrediction(id)
    }

    ElMessage.success('批量删除成功')
    selectedIds.value = []
    selectedRows.value = []
    fetchHistory()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

// 显示反馈对话框
const handleShowFeedback = (record) => {
  feedbackForm.value = {
    prediction_id: record.id,
    predicted_class: record.predicted_class,
    correct_class: '',
    comment: ''
  }
  showFeedbackDialog.value = true
}

// 提交反馈
const handleSubmitFeedback = async () => {
  if (!feedbackForm.value.correct_class) {
    ElMessage.warning('请输入正确的分类')
    return
  }

  submittingFeedback.value = true
  try {
    await submitFeedback({
      prediction_id: feedbackForm.value.prediction_id,
      correct_class: feedbackForm.value.correct_class,
      comment: feedbackForm.value.comment
    })
    ElMessage.success('感谢您的反馈！这将帮助我们改进识别准确度')
    showFeedbackDialog.value = false
  } catch (error) {
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error('提交反馈失败，请重试')
    }
  } finally {
    submittingFeedback.value = false
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
    // 准备导出数据（使用序号而不是ID）
    const exportData = selectedRows.value.map((row, index) => ({
      '序号': index + 1,
      '分类结果': row.predicted_class,
      '置信度': `${row.confidence}%`,
      '识别时间': formatDateTime(row.created_at),
      '图片文件名': row.image_path.split('/').pop()
    }))

    // 创建工作表
    const worksheet = XLSX.utils.json_to_sheet(exportData)

    // 创建工作簿
    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, '识别历史')

    // 生成文件并下载
    const filename = `识别历史_${new Date().getTime()}.xlsx`
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
  fetchHistory()
})

// 监听路由变化，当进入此页面时重新加载数据
watch(() => route.path, (newPath) => {
  if (newPath === '/history') {
    fetchHistory()
  }
})
</script>

<style scoped>
.history {
  max-width: 1200px;
  margin: 0 auto;
}

.header-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-wrapper h2 {
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.filter-toolbar {
  margin-bottom: 20px;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.filter-toolbar :deep(.el-form-item) {
  margin-bottom: 0;
}

.pagination-wrapper {
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
