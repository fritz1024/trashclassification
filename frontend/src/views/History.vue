<template>
  <div class="history">
    <el-card>
      <template #header>
        <h2>识别历史</h2>
      </template>

      <el-table :data="historyList" style="width: 100%" v-loading="loading">
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
          <el-input
            v-model="feedbackForm.correct_class"
            placeholder="请输入正确的垃圾分类"
          />
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
import { formatDateTime } from '@/utils/date'

const route = useRoute()
const historyList = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

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
    const response = await getPredictionHistory({
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    })
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
