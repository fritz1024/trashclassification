<template>
  <AdminLayout>
    <div class="admin-page">
      <div class="page-header">
        <h1>模型训练</h1>
        <div class="header-actions">
          <template v-if="activeTab === 'datasets'">
            <el-button type="danger" :disabled="selectedDatasetIds.length === 0" @click="handleBatchDeleteDatasets">
              批量删除 ({{ selectedDatasetIds.length }})
            </el-button>
            <el-button type="primary" @click="showCreateDatasetDialog = true">
              从历史生成数据集
            </el-button>
          </template>
          <template v-if="activeTab === 'jobs'">
            <el-button type="danger" :disabled="selectedJobIds.length === 0" @click="handleBatchDeleteJobs">
              批量删除 ({{ selectedJobIds.length }})
            </el-button>
            <el-button type="primary" @click="showCreateJobDialog = true">
              创建训练任务
            </el-button>
          </template>
        </div>
      </div>

      <div class="content-card">
        <el-tabs v-model="activeTab">
          <!-- 数据集管理 -->
          <el-tab-pane label="训练数据集" name="datasets">
            <el-table :data="datasets" v-loading="datasetsLoading" stripe @selection-change="handleDatasetSelectionChange">
              <el-table-column type="selection" width="55" />
              <el-table-column label="序号" width="70">
                <template #default="{ $index }">{{ (datasetPage - 1) * datasetPageSize + $index + 1 }}</template>
              </el-table-column>
              <el-table-column prop="name" label="数据集名称" min-width="200" />
              <el-table-column prop="source_type" label="来源" width="100">
                <template #default="{ row }">
                  <el-tag size="small">{{ row.source_type === 'history' ? '历史记录' : '上传' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="class_count" label="类别数" width="100" />
              <el-table-column prop="image_count" label="图片数" width="100" />
              <el-table-column prop="creator_name" label="创建者" width="120" />
              <el-table-column label="创建时间" width="180">
                <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
              </el-table-column>
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" size="small" link @click="handleViewDataset(row)">查看</el-button>
                  <el-button type="danger" size="small" link @click="handleDeleteDataset(row.id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>

            <div class="pagination-bar">
              <span class="pagination-info">
                第 {{ (datasetPage - 1) * datasetPageSize + 1 }}-{{ Math.min(datasetPage * datasetPageSize, datasetTotal) }} 条，共 {{ datasetTotal }} 条
              </span>
              <el-pagination
                v-model:current-page="datasetPage"
                v-model:page-size="datasetPageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="datasetTotal"
                layout="sizes, prev, pager, next"
                @size-change="loadDatasets"
                @current-change="loadDatasets"
              />
            </div>
          </el-tab-pane>

          <!-- 训练任务 -->
          <el-tab-pane label="训练任务" name="jobs">
            <div class="toolbar">
              <div class="toolbar-left"></div>
              <div class="toolbar-right">
                <el-radio-group v-model="jobStatusFilter" @change="loadJobs" size="small">
                  <el-radio-button label="">全部</el-radio-button>
                  <el-radio-button label="pending">待处理</el-radio-button>
                  <el-radio-button label="running">运行中</el-radio-button>
                  <el-radio-button label="completed">已完成</el-radio-button>
                </el-radio-group>
              </div>
            </div>

            <el-table :data="jobs" v-loading="jobsLoading" stripe @selection-change="handleJobSelectionChange">
              <el-table-column type="selection" width="55" />
              <el-table-column label="序号" width="70">
                <template #default="{ $index }">{{ (jobPage - 1) * jobPageSize + $index + 1 }}</template>
              </el-table-column>
              <el-table-column prop="name" label="模型名称" width="120" />
              <el-table-column prop="dataset_name" label="数据集" min-width="150" />
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="进度" width="200">
                <template #default="{ row }">
                  <div v-if="row.status === 'running' || row.status === 'completed'">
                    <el-progress :percentage="Math.round(row.progress)" :status="row.status === 'completed' ? 'success' : ''" />
                    <div style="font-size: 12px; color: var(--text-tertiary); margin-top: 4px;">
                      Epoch {{ row.current_epoch }}/{{ row.total_epochs }}
                      <span v-if="row.loss"> | Loss: {{ row.loss.toFixed(4) }}</span>
                      <span v-if="row.accuracy"> | Acc: {{ row.accuracy.toFixed(2) }}%</span>
                    </div>
                  </div>
                  <span v-else>-</span>
                </template>
              </el-table-column>
              <el-table-column label="创建时间" width="180">
                <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
              </el-table-column>
              <el-table-column label="操作" width="180" fixed="right">
                <template #default="{ row }">
                  <el-button v-if="row.status === 'pending'" type="primary" size="small" link @click="handleStartJob(row.id)">启动</el-button>
                  <el-button v-if="row.status === 'running'" type="warning" size="small" link @click="handleCancelJob(row.id)">取消</el-button>
                  <el-button type="danger" size="small" link @click="handleDeleteJob(row.id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>

            <div class="pagination-bar">
              <span class="pagination-info">
                第 {{ (jobPage - 1) * jobPageSize + 1 }}-{{ Math.min(jobPage * jobPageSize, jobTotal) }} 条，共 {{ jobTotal }} 条
              </span>
              <el-pagination
                v-model:current-page="jobPage"
                v-model:page-size="jobPageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="jobTotal"
                layout="sizes, prev, pager, next"
                @size-change="loadJobs"
                @current-change="loadJobs"
              />
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>

    <!-- 创建数据集对话框 -->
    <el-dialog v-model="showCreateDatasetDialog" title="从历史生成数据集" width="500px">
      <el-form :model="datasetForm" label-width="120px">
        <el-form-item label="数据集名称">
          <el-input v-model="datasetForm.name" placeholder="例如：垃圾分类数据集v1" />
        </el-form-item>
        <el-form-item label="最小图片数">
          <el-input-number v-model="datasetForm.minImages" :min="1" :max="100" />
          <div style="font-size: 12px; color: var(--text-tertiary); margin-top: 4px;">
            每个类别至少需要的图片数量
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDatasetDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateDataset" :loading="creatingDataset">创建</el-button>
      </template>
    </el-dialog>

    <!-- 创建训练任务对话框 -->
    <el-dialog v-model="showCreateJobDialog" title="创建训练任务" width="600px">
      <el-form :model="jobForm" label-width="100px">
        <el-form-item label="数据集">
          <el-select v-model="jobForm.dataset_id" placeholder="请选择数据集" style="width: 100%;">
            <el-option v-for="ds in datasets" :key="ds.id" :label="ds.name" :value="ds.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="模型名称">
          <el-input v-model="jobForm.name" placeholder="留空自动生成（如 G0001）" />
        </el-form-item>
        <el-form-item label="训练轮数">
          <el-input-number v-model="jobForm.epochs" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="批次大小">
          <el-input-number v-model="jobForm.batch_size" :min="1" :max="128" />
        </el-form-item>
        <el-form-item label="学习率">
          <el-input-number v-model="jobForm.learning_rate" :min="0.0001" :max="0.1" :step="0.001" :precision="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateJobDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateJob" :loading="creatingJob">创建</el-button>
      </template>
    </el-dialog>

    <!-- 查看数据集对话框 -->
    <el-dialog v-model="showViewDatasetDialog" title="数据集详情" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="数据集名称">{{ viewingDataset?.name }}</el-descriptions-item>
        <el-descriptions-item label="来源">{{ viewingDataset?.source_type === 'history' ? '历史记录' : '上传' }}</el-descriptions-item>
        <el-descriptions-item label="类别数">{{ viewingDataset?.class_count }}</el-descriptions-item>
        <el-descriptions-item label="图片数">{{ viewingDataset?.image_count }}</el-descriptions-item>
        <el-descriptions-item label="创建者">{{ viewingDataset?.creator_name }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDateTime(viewingDataset?.created_at) }}</el-descriptions-item>
      </el-descriptions>

      <div v-if="viewingDataset?.classes && viewingDataset.classes.length > 0" style="margin-top: 20px;">
        <h4 style="margin-bottom: 12px;">类别详情</h4>
        <el-table :data="viewingDataset.classes" border size="small" max-height="300">
          <el-table-column prop="name" label="类别名称" min-width="150" />
          <el-table-column prop="count" label="图片数量" width="100" align="center" />
        </el-table>
      </div>

      <template #footer>
        <el-button @click="showViewDatasetDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdminLayout from '@/components/AdminLayout.vue'
import { getDatasets, getDatasetDetail, createDatasetFromHistory, deleteDataset, getTrainingJobs, createTrainingJob, startTraining, cancelTraining, deleteTrainingJob } from '@/api/training'
import { formatDateTime } from '@/utils/date'

const activeTab = ref('datasets')

// 数据集相关
const datasets = ref([])
const datasetsLoading = ref(false)
const datasetPage = ref(1)
const datasetPageSize = ref(20)
const datasetTotal = ref(0)
const selectedDatasetIds = ref([])
const showCreateDatasetDialog = ref(false)
const creatingDataset = ref(false)
const datasetForm = ref({
  name: '',
  minImages: 10
})

// 查看数据集
const showViewDatasetDialog = ref(false)
const viewingDataset = ref(null)

// 训练任务相关
const jobs = ref([])
const jobsLoading = ref(false)
const jobPage = ref(1)
const jobPageSize = ref(20)
const jobTotal = ref(0)
const selectedJobIds = ref([])
const jobStatusFilter = ref('')
const showCreateJobDialog = ref(false)
const creatingJob = ref(false)
const jobForm = ref({
  dataset_id: null,
  name: '',
  epochs: 10,
  batch_size: 32,
  learning_rate: 0.001
})

let refreshTimer = null

const loadDatasets = async () => {
  datasetsLoading.value = true
  try {
    const params = {
      skip: (datasetPage.value - 1) * datasetPageSize.value,
      limit: datasetPageSize.value
    }
    const res = await getDatasets(params)
    datasets.value = res.items
    datasetTotal.value = res.total
  } catch (error) {
    ElMessage.error('加载数据集列表失败')
  } finally {
    datasetsLoading.value = false
  }
}

const loadJobs = async () => {
  jobsLoading.value = true
  try {
    const params = {
      skip: (jobPage.value - 1) * jobPageSize.value,
      limit: jobPageSize.value
    }
    if (jobStatusFilter.value) {
      params.status = jobStatusFilter.value
    }
    const res = await getTrainingJobs(params)
    jobs.value = res.items
    jobTotal.value = res.total
  } catch (error) {
    ElMessage.error('加载训练任务列表失败')
  } finally {
    jobsLoading.value = false
  }
}

const handleCreateDataset = async () => {
  if (!datasetForm.value.name) {
    ElMessage.warning('请输入数据集名称')
    return
  }

  creatingDataset.value = true
  try {
    const res = await createDatasetFromHistory(datasetForm.value.name, datasetForm.value.minImages)
    ElMessage.success(`数据集创建成功！包含 ${res.class_count} 个类别，${res.image_count} 张图片`)
    showCreateDatasetDialog.value = false
    datasetForm.value = { name: '', minImages: 10 }
    loadDatasets()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '创建数据集失败')
  } finally {
    creatingDataset.value = false
  }
}

const handleViewDataset = async (dataset) => {
  try {
    const detail = await getDatasetDetail(dataset.id)
    viewingDataset.value = detail
    showViewDatasetDialog.value = true
  } catch (error) {
    ElMessage.error('获取数据集详情失败')
  }
}

const handleDatasetSelectionChange = (selection) => {
  selectedDatasetIds.value = selection.map(item => item.id)
}

const handleDeleteDataset = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个数据集吗？', '提示', { type: 'warning' })
    await deleteDataset(id)
    ElMessage.success('删除成功')
    loadDatasets()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

const handleBatchDeleteDatasets = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedDatasetIds.value.length} 个数据集吗？`, '批量删除', { type: 'warning' })
    const promises = selectedDatasetIds.value.map(id => deleteDataset(id))
    await Promise.all(promises)
    ElMessage.success(`成功删除 ${selectedDatasetIds.value.length} 个数据集`)
    selectedDatasetIds.value = []
    loadDatasets()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const handleCreateJob = async () => {
  if (!jobForm.value.dataset_id) {
    ElMessage.warning('请选择数据集')
    return
  }

  creatingJob.value = true
  try {
    await createTrainingJob(jobForm.value)
    ElMessage.success('训练任务创建成功')
    showCreateJobDialog.value = false
    jobForm.value = { dataset_id: null, name: '', epochs: 10, batch_size: 32, learning_rate: 0.001 }
    loadJobs()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '创建任务失败')
  } finally {
    creatingJob.value = false
  }
}

const handleStartJob = async (id) => {
  try {
    await startTraining(id)
    ElMessage.success('训练已启动')
    loadJobs()
    startAutoRefresh()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '启动失败')
  }
}

const handleCancelJob = async (id) => {
  try {
    await ElMessageBox.confirm('确定要取消这个训练任务吗？', '提示', { type: 'warning' })
    await cancelTraining(id)
    ElMessage.success('任务已取消')
    loadJobs()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '取消失败')
    }
  }
}

const handleJobSelectionChange = (selection) => {
  selectedJobIds.value = selection.map(item => item.id)
}

const handleDeleteJob = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个训练任务吗？', '提示', { type: 'warning' })
    await deleteTrainingJob(id)
    ElMessage.success('删除成功')
    loadJobs()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

const handleBatchDeleteJobs = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedJobIds.value.length} 个训练任务吗？`, '批量删除', { type: 'warning' })
    const promises = selectedJobIds.value.map(id => deleteTrainingJob(id))
    await Promise.all(promises)
    ElMessage.success(`成功删除 ${selectedJobIds.value.length} 个训练任务`)
    selectedJobIds.value = []
    loadJobs()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const getStatusType = (status) => {
  const types = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    pending: '待处理',
    running: '运行中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return texts[status] || status
}

const startAutoRefresh = () => {
  if (refreshTimer) return
  refreshTimer = setInterval(() => {
    if (activeTab.value === 'jobs') {
      loadJobs()
    }
  }, 3000)
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

onMounted(() => {
  loadDatasets()
  loadJobs()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
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
