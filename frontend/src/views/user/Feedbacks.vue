<template>
  <UserLayout>
    <div class="feedbacks-page">
      <div class="page-header">
        <h1>我的反馈</h1>
      </div>

      <div class="content-card">
        <el-table :data="feedbacks" v-loading="loading" stripe>
      <el-table-column label="序号" width="70">
        <template #default="{ $index, row }">
          <el-link type="primary" @click="handleShowDetail(row)">{{ $index + 1 }}</el-link>
        </template>
      </el-table-column>
      <el-table-column prop="correct_class" label="正确分类" width="150" />
      <el-table-column prop="comment" label="反馈说明" min-width="200" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'pending' ? 'warning' : 'success'" size="small">
            {{ row.status === 'pending' ? '待处理' : '已处理' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="process_result" label="处理结果" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.process_result === 'adopted'" type="success" size="small">已采纳</el-tag>
          <el-tag v-else-if="row.process_result === 'rejected'" type="danger" size="small">已拒绝</el-tag>
          <el-tag v-else-if="row.process_result === 'invalid'" type="info" size="small">无效</el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="process_comment" label="处理意见" min-width="150" show-overflow-tooltip />
      <el-table-column prop="created_at" label="提交时间" width="180">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
    </el-table>

    <el-empty v-if="!loading && feedbacks.length === 0" description="暂无反馈记录" />

        <div class="pagination-bar" v-if="total > 0">
          <span class="pagination-info">
            第 {{ (currentPage - 1) * pageSize + 1 }}-{{ Math.min(currentPage * pageSize, total) }} 条，共 {{ total }} 条
          </span>
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="total"
            layout="sizes, prev, pager, next"
            @size-change="loadFeedbacks"
            @current-change="loadFeedbacks"
          />
        </div>
      </div>
    </div>

    <!-- 识别记录详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="识别记录详情" width="600px">
      <div v-if="currentDetail" class="prediction-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="记录ID">{{ currentDetail.id }}</el-descriptions-item>
          <el-descriptions-item label="识别结果">
            <el-tag>{{ currentDetail.predicted_class }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="置信度">{{ currentDetail.confidence }}%</el-descriptions-item>
          <el-descriptions-item label="识别时间">{{ formatTime(currentDetail.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="识别图片">
            <el-image
              style="width: 200px; height: 200px; border-radius: var(--radius-sm);"
              :src="`/${currentDetail.image_path}`"
              fit="cover"
              :preview-src-list="[`/${currentDetail.image_path}`]"
            />
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <div v-else>识别记录不存在或已被删除</div>
    </el-dialog>
  </UserLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import UserLayout from '@/components/UserLayout.vue'

const feedbacks = ref([])
const loading = ref(false)
const showDetailDialog = ref(false)
const currentDetail = ref(null)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const loadFeedbacks = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    const res = await request.get('/predict/feedbacks', { params })
    feedbacks.value = res.items
    total.value = res.total
  } catch (error) {
    ElMessage.error('加载反馈列表失败')
  } finally {
    loading.value = false
  }
}

const handleShowDetail = (feedback) => {
  currentDetail.value = feedback.prediction_detail
  showDetailDialog.value = true
}

const formatTime = (time) => new Date(time).toLocaleString('zh-CN')

onMounted(() => loadFeedbacks())
</script>

<style scoped>
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-6); }
.page-header h1 { font-size: var(--text-2xl); font-weight: var(--font-bold); color: var(--text-primary); }
.content-card { background: var(--bg-elevated); border: 1px solid var(--border-secondary); border-radius: var(--radius-xl); padding: var(--space-6); box-shadow: var(--shadow-sm); }
.pagination-bar { display: flex; align-items: center; justify-content: space-between; margin-top: var(--space-5); padding-top: var(--space-4); border-top: 1px solid var(--border-secondary); }
.pagination-info { font-size: var(--text-sm); color: var(--text-tertiary); }
@media (max-width: 768px) {
  .page-header { flex-direction: column; gap: var(--space-3); align-items: flex-start; }
  .content-card { padding: var(--space-4); }
}
</style>
