<template>
  <AdminLayout>
    <div class="admin-page">
      <!-- Page Header -->
      <div class="page-header">
        <h1>反馈管理</h1>
        <div class="header-actions">
          <el-button
            type="success"
            :disabled="selectedIds.length === 0"
            @click="handleBatchProcess"
          >
            批量标记已处理 ({{ selectedIds.length }})
          </el-button>
        </div>
      </div>

      <!-- Content Card -->
      <div class="content-card">
        <!-- Toolbar -->
        <div class="toolbar">
          <div class="toolbar-left"></div>
          <div class="toolbar-right">
            <el-radio-group v-model="statusFilter" @change="handleFilterChange">
              <el-radio-button label="">全部</el-radio-button>
              <el-radio-button label="pending">待处理</el-radio-button>
              <el-radio-button label="processed">已处理</el-radio-button>
            </el-radio-group>
          </div>
        </div>

        <!-- Data Table -->
        <el-table
          :data="feedbackList"
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
          <el-table-column label="记录ID" width="120">
            <template #default="scope">
              <el-link type="primary" @click="handleShowPredictionDetail(scope.row)">
                {{ scope.row.prediction_id }}
              </el-link>
            </template>
          </el-table-column>
          <el-table-column prop="correct_class" label="正确分类" min-width="150" />
          <el-table-column prop="comment" label="备注" min-width="200" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.status === 'pending' ? 'warning' : 'success'" size="small">
                {{ scope.row.status === 'pending' ? '待处理' : '已处理' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="时间" width="180">
            <template #default="scope">
              {{ formatDateTime(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="scope">
              <el-button
                v-if="scope.row.status === 'pending'"
                type="success"
                size="small"
                link
                @click="handleProcess(scope.row.id)"
              >
                标记已处理
              </el-button>
              <el-tag v-else type="success" size="small">已处理</el-tag>
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
            @size-change="fetchFeedbacks"
            @current-change="fetchFeedbacks"
          />
        </div>
      </div>
    </div>

    <!-- Prediction Detail Dialog -->
    <el-dialog
      v-model="showDetailDialog"
      title="识别记录详情"
      width="600px"
    >
      <div v-if="currentPredictionDetail" class="prediction-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="记录ID">
            {{ currentPredictionDetail.id }}
          </el-descriptions-item>
          <el-descriptions-item label="识别结果">
            <el-tag>{{ currentPredictionDetail.predicted_class }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="置信度">
            {{ currentPredictionDetail.confidence }}%
          </el-descriptions-item>
          <el-descriptions-item label="识别时间">
            {{ formatDateTime(currentPredictionDetail.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="识别图片">
            <el-image
              style="width: 200px; height: 200px; border-radius: var(--radius-sm);"
              :src="`/${currentPredictionDetail.image_path}`"
              fit="cover"
              :preview-src-list="[`/${currentPredictionDetail.image_path}`]"
            />
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <div v-else class="detail-empty">
        识别记录不存在或已被删除
      </div>
    </el-dialog>

    <!-- 处理反馈对话框 -->
    <el-dialog v-model="showProcessDialog" title="处理反馈" width="500px">
      <el-form :model="processForm" label-width="80px">
        <el-form-item label="处理结果">
          <el-radio-group v-model="processForm.result">
            <el-radio label="adopted">采纳</el-radio>
            <el-radio label="rejected">拒绝</el-radio>
            <el-radio label="invalid">无效</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="处理意见">
          <el-input v-model="processForm.comment" type="textarea" :rows="4" placeholder="请输入处理意见（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showProcessDialog = false">取消</el-button>
        <el-button type="primary" @click="submitProcess" :loading="processing">确定</el-button>
      </template>
    </el-dialog>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAllFeedbacks, updateFeedbackStatus } from '@/api/admin'
import { ElMessage, ElMessageBox } from 'element-plus'
import { formatDateTime } from '@/utils/date'
import AdminLayout from '@/components/AdminLayout.vue'

const feedbackList = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const statusFilter = ref('')
const selectedIds = ref([])

// 识别记录详情相关
const showDetailDialog = ref(false)
const currentPredictionDetail = ref(null)

// 处理反馈相关
const showProcessDialog = ref(false)
const processing = ref(false)
const currentFeedbackId = ref(null)
const processForm = ref({
  result: 'adopted',
  comment: ''
})

const fetchFeedbacks = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }

    if (statusFilter.value) {
      params.status = statusFilter.value
    }

    const response = await getAllFeedbacks(params)
    feedbackList.value = response.items
    total.value = response.total
  } catch (error) {
    ElMessage.error('获取反馈列表失败')
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  currentPage.value = 1
  fetchFeedbacks()
}

const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map(item => item.id)
}

const handleProcess = (feedbackId) => {
  currentFeedbackId.value = feedbackId
  processForm.value = { result: 'adopted', comment: '' }
  showProcessDialog.value = true
}

const submitProcess = async () => {
  processing.value = true
  try {
    await updateFeedbackStatus(currentFeedbackId.value, processForm.value.result, processForm.value.comment)
    ElMessage.success('反馈处理成功')
    showProcessDialog.value = false
    fetchFeedbacks()
  } catch (error) {
    ElMessage.error('处理失败')
  } finally {
    processing.value = false
  }
}

const handleBatchProcess = async () => {
  if (selectedIds.value.length === 0) return

  try {
    const { value: result } = await ElMessageBox.prompt(
      `将对选中的 ${selectedIds.value.length} 条反馈应用相同的处理结果`,
      '批量处理',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPlaceholder: '处理意见（可选）',
        inputType: 'textarea',
        beforeClose: async (action, instance, done) => {
          if (action === 'confirm') {
            const comment = instance.inputValue
            const promises = selectedIds.value.map(id =>
              updateFeedbackStatus(id, 'adopted', comment)
            )
            await Promise.all(promises)
            done()
          } else {
            done()
          }
        }
      }
    )

    ElMessage.success(`成功处理 ${selectedIds.value.length} 条反馈`)
    selectedIds.value = []
    fetchFeedbacks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量处理失败')
    }
  }
}

// 显示识别记录详情
const handleShowPredictionDetail = (feedback) => {
  currentPredictionDetail.value = feedback.prediction_detail
  showDetailDialog.value = true
}

onMounted(() => {
  fetchFeedbacks()
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

.detail-empty {
  text-align: center;
  padding: var(--space-6);
  color: var(--text-tertiary);
}
</style>
