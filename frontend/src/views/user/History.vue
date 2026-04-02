<template>
  <UserLayout>
    <div class="history-page">
      <div class="page-header">
        <h1>识别历史</h1>
        <div class="header-actions">
          <el-button round type="danger" :icon="Delete" @click="handleBatchDelete" :disabled="selectedIds.length === 0">
            删除 ({{ selectedIds.length }})
          </el-button>
          <el-button round type="primary" :icon="Download" @click="handleExport" :loading="exportLoading">
            导出
          </el-button>
        </div>
      </div>

      <div class="content-card">
        <div class="filter-bar">
          <el-form :inline="true" :model="filterForm">
            <el-form-item label="分类">
              <el-select v-model="filterForm.category" placeholder="全部" clearable style="width: 140px">
                <el-option label="可回收物" value="可回收物" />
                <el-option label="有害垃圾" value="有害垃圾" />
                <el-option label="厨余垃圾" value="厨余垃圾" />
                <el-option label="其他垃圾" value="其他垃圾" />
              </el-select>
            </el-form-item>
            <el-form-item label="时间">
              <el-date-picker v-model="filterForm.dateRange" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" style="width: 220px" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" round @click="handleFilter">筛选</el-button>
              <el-button round @click="handleResetFilter">重置</el-button>
            </el-form-item>
          </el-form>
        </div>

        <el-table :data="historyList" v-loading="loading" @selection-change="handleSelectionChange" stripe>
          <el-table-column type="selection" width="50" />
          <el-table-column label="#" width="60">
            <template #default="scope">{{ (currentPage - 1) * pageSize + scope.$index + 1 }}</template>
          </el-table-column>
          <el-table-column label="图片" width="100">
            <template #default="scope">
              <el-image style="width: 64px; height: 64px; border-radius: var(--radius-sm);" :src="`/${scope.row.image_path}`" :preview-src-list="[`/${scope.row.image_path}`]" fit="cover" preview-teleported />
            </template>
          </el-table-column>
          <el-table-column prop="predicted_class" label="分类" />
          <el-table-column label="置信度" width="100">
            <template #default="scope">
              <span class="confidence-val">{{ scope.row.confidence }}%</span>
            </template>
          </el-table-column>
          <el-table-column label="时间" width="170">
            <template #default="scope">{{ formatDateTime(scope.row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="scope">
              <el-button text type="primary" size="small" @click="handleShowFeedback(scope.row)">反馈</el-button>
              <el-button text type="danger" size="small" @click="handleDelete(scope.row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-bar">
          <span class="pagination-info">共 {{ total }} 条</span>
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="total"
            layout="sizes, prev, pager, next"
            @size-change="fetchHistory"
            @current-change="fetchHistory"
          />
        </div>
      </div>

      <el-dialog v-model="showFeedbackDialog" title="提交识别反馈" width="460px" :close-on-click-modal="false">
        <el-form :model="feedbackForm" label-width="80px">
          <el-form-item label="识别结果"><el-input v-model="feedbackForm.predicted_class" disabled /></el-form-item>
          <el-form-item label="正确分类" required>
            <el-select v-model="feedbackForm.correct_class" placeholder="请选择" style="width: 100%">
              <el-option label="可回收物" value="可回收物" />
              <el-option label="有害垃圾" value="有害垃圾" />
              <el-option label="厨余垃圾" value="厨余垃圾" />
              <el-option label="其他垃圾" value="其他垃圾" />
            </el-select>
          </el-form-item>
          <el-form-item label="备注"><el-input v-model="feedbackForm.comment" type="textarea" :rows="3" placeholder="描述错误情况（可选）" /></el-form-item>
        </el-form>
        <template #footer>
          <el-button round @click="showFeedbackDialog = false">取消</el-button>
          <el-button type="primary" round @click="handleSubmitFeedback" :loading="submittingFeedback">提交</el-button>
        </template>
      </el-dialog>
    </div>
  </UserLayout>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getPredictionHistory, deletePrediction, submitFeedback } from '@/api/predict'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Delete } from '@element-plus/icons-vue'
import { formatDateTime } from '@/utils/date'
import * as XLSX from 'xlsx'
import UserLayout from '@/components/UserLayout.vue'

const route = useRoute()
const historyList = ref([])
const loading = ref(false)
const exportLoading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const selectedIds = ref([])
const selectedRows = ref([])
const filterForm = ref({ category: '', dateRange: null })
const showFeedbackDialog = ref(false)
const submittingFeedback = ref(false)
const feedbackForm = ref({ prediction_id: null, predicted_class: '', correct_class: '', comment: '' })

const fetchHistory = async () => {
  loading.value = true
  try {
    const params = { skip: (currentPage.value - 1) * pageSize.value, limit: pageSize.value }
    if (filterForm.value.category) params.predicted_class = filterForm.value.category
    if (filterForm.value.dateRange?.length === 2) {
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
    await ElMessageBox.confirm('确定要删除这条记录吗？', '提示', { type: 'warning' })
    await deletePrediction(id)
    ElMessage.success('删除成功')
    fetchHistory()
  } catch (error) { if (error !== 'cancel') ElMessage.error('删除失败') }
}

const handleFilter = () => { currentPage.value = 1; fetchHistory() }
const handleResetFilter = () => { filterForm.value = { category: '', dateRange: null }; currentPage.value = 1; fetchHistory() }
const handleSelectionChange = (selection) => { selectedRows.value = selection; selectedIds.value = selection.map(r => r.id) }

const handleBatchDelete = async () => {
  if (!selectedIds.value.length) return
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${selectedIds.value.length} 条记录？`, '批量删除', { type: 'warning' })
    for (const id of selectedIds.value) await deletePrediction(id)
    ElMessage.success('批量删除成功')
    selectedIds.value = []
    selectedRows.value = []
    fetchHistory()
  } catch (error) { if (error !== 'cancel') ElMessage.error('批量删除失败') }
}

const handleShowFeedback = (record) => {
  feedbackForm.value = { prediction_id: record.id, predicted_class: record.predicted_class, correct_class: '', comment: '' }
  showFeedbackDialog.value = true
}

const handleSubmitFeedback = async () => {
  if (!feedbackForm.value.correct_class) { ElMessage.warning('请选择正确的分类'); return }
  submittingFeedback.value = true
  try {
    await submitFeedback({ prediction_id: feedbackForm.value.prediction_id, correct_class: feedbackForm.value.correct_class, comment: feedbackForm.value.comment })
    ElMessage.success('感谢您的反馈！')
    showFeedbackDialog.value = false
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '提交反馈失败')
  } finally { submittingFeedback.value = false }
}

const handleExport = async () => {
  if (!selectedIds.value.length) { ElMessage.warning('请先勾选要导出的数据'); return }
  exportLoading.value = true
  try {
    const data = selectedRows.value.map((row, i) => ({ '序号': i + 1, '分类结果': row.predicted_class, '置信度': `${row.confidence}%`, '识别时间': formatDateTime(row.created_at), '图片文件名': row.image_path.split('/').pop() }))
    const ws = XLSX.utils.json_to_sheet(data)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '识别历史')
    XLSX.writeFile(wb, `识别历史_${new Date().getTime()}.xlsx`)
    ElMessage.success(`成功导出 ${selectedIds.value.length} 条数据`)
  } catch (error) { ElMessage.error('导出失败') } finally { exportLoading.value = false }
}

onMounted(() => fetchHistory())
watch(() => route.path, (p) => { if (p === '/user/history') fetchHistory() })
</script>

<style scoped>
.history-page { max-width: 1100px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-6); }
.page-header h1 { font-size: var(--text-2xl); font-weight: var(--font-bold); color: var(--text-primary); }
.header-actions { display: flex; gap: var(--space-3); }
.content-card { background: var(--bg-elevated); border: 1px solid var(--border-secondary); border-radius: var(--radius-xl); padding: var(--space-6); box-shadow: var(--shadow-sm); }
.filter-bar { margin-bottom: var(--space-5); padding: var(--space-4); background: var(--bg-secondary); border-radius: var(--radius-md); }
.filter-bar :deep(.el-form-item) { margin-bottom: 0; }
.confidence-val { font-weight: var(--font-semibold); color: var(--color-primary); }
.pagination-bar { display: flex; align-items: center; justify-content: space-between; margin-top: var(--space-5); padding-top: var(--space-4); border-top: 1px solid var(--border-secondary); }
.pagination-info { font-size: var(--text-sm); color: var(--text-tertiary); }
@media (max-width: 768px) {
  .page-header { flex-direction: column; gap: var(--space-3); align-items: flex-start; }
  .content-card { padding: var(--space-4); }
}
</style>
