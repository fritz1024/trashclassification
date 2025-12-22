<template>
  <div class="admin-page">
    <el-card>
      <!-- 页面标题 -->
      <template #header>
        <div class="page-header">
          <h3>用户反馈管理</h3>
        </div>
      </template>

      <!-- 操作栏 -->
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button
            type="success"
            :disabled="selectedIds.length === 0"
            @click="handleBatchProcess"
          >
            批量标记已处理 ({{ selectedIds.length }})
          </el-button>
        </div>
        <div class="toolbar-right">
          <el-radio-group v-model="statusFilter" @change="handleFilterChange">
            <el-radio-button label="">全部</el-radio-button>
            <el-radio-button label="pending">待处理</el-radio-button>
            <el-radio-button label="processed">已处理</el-radio-button>
          </el-radio-group>
        </div>
      </div>

      <!-- 数据表格 -->
      <el-table
        :data="feedbackList"
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
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column label="识别记录ID" width="120">
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
            <el-tag :type="scope.row.status === 'pending' ? 'warning' : 'success'">
              {{ scope.row.status === 'pending' ? '待处理' : '已处理' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="提交时间" width="180">
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
              @click="handleProcess(scope.row.id)"
            >
              标记已处理
            </el-button>
            <el-tag v-else type="success">已处理</el-tag>
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
          @size-change="fetchFeedbacks"
          @current-change="fetchFeedbacks"
        />
      </div>
    </el-card>

    <!-- 识别记录详情对话框 -->
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
              style="width: 200px; height: 200px"
              :src="`/${currentPredictionDetail.image_path}`"
              fit="cover"
              :preview-src-list="[`/${currentPredictionDetail.image_path}`]"
            />
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <div v-else style="text-align: center; padding: 20px; color: #999;">
        识别记录不存在或已被删除
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAllFeedbacks, updateFeedbackStatus } from '@/api/admin'
import { ElMessage, ElMessageBox } from 'element-plus'
import { formatDateTime } from '@/utils/date'

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

const handleProcess = async (feedbackId) => {
  try {
    await updateFeedbackStatus(feedbackId, 'processed')
    ElMessage.success('已标记为已处理')
    fetchFeedbacks()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleBatchProcess = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要将选中的 ${selectedIds.value.length} 条反馈标记为已处理吗？`,
      '批量处理',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const promises = selectedIds.value.map(id => updateFeedbackStatus(id, 'processed'))
    await Promise.all(promises)

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
