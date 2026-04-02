<template>
  <AdminLayout>
    <div class="model-page">
      <!-- Page Header -->
      <div class="page-header">
        <h1 class="page-title">模型管理</h1>
        <div class="header-actions">
          <el-button @click="showCompareDialog = true">
            <el-icon><DataAnalysis /></el-icon>
            模型对比
          </el-button>
          <el-button type="primary" @click="showUploadDialog = true">
            <el-icon><Upload /></el-icon>
            上传模型
          </el-button>
        </div>
      </div>

      <!-- Current Model Info -->
      <h2 class="section-title">当前模型信息</h2>
      <div class="info-grid" v-loading="infoLoading">
        <div class="info-card">
          <span class="info-label">模型名称</span>
          <span class="info-value">{{ modelInfo.model_name }}</span>
        </div>
        <div class="info-card">
          <span class="info-label">模型文件</span>
          <span class="info-value">{{ modelInfo.model_file }}</span>
        </div>
        <div class="info-card">
          <span class="info-label">模型大小</span>
          <span class="info-value">{{ modelInfo.model_size_mb }} MB</span>
        </div>
        <div class="info-card">
          <span class="info-label">最后更新</span>
          <span class="info-value">{{ modelInfo.model_updated || '未知' }}</span>
        </div>
      </div>

      <!-- Model List -->
      <div class="section-header">
        <h2 class="section-title">所有模型</h2>
        <el-button text @click="fetchModelList" :loading="listLoading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
      <div class="content-card">
        <el-table :data="modelList" v-loading="listLoading" style="width: 100%">
          <el-table-column label="模型文件" min-width="200">
            <template #default="scope">
              <div style="display: flex; align-items: center; gap: 8px;">
                <span>{{ scope.row.name }}</span>
                <el-tag v-if="scope.row.is_current" type="success" size="small">当前使用</el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="size_mb" label="大小 (MB)" width="120" />
          <el-table-column prop="updated_at" label="更新时间" width="180" />
          <el-table-column label="操作" width="200">
            <template #default="scope">
              <el-button
                v-if="!scope.row.is_current"
                type="primary"
                size="small"
                @click="handleSwitchModel(scope.row.name)"
              >
                切换
              </el-button>
              <el-button
                v-if="!scope.row.is_current"
                type="danger"
                size="small"
                @click="handleDeleteModel(scope.row.name)"
              >
                删除
              </el-button>
              <el-tag v-else type="info" size="small">使用中</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Performance Stats -->
      <h2 class="section-title">性能统计</h2>
      <div class="stats-grid" v-loading="performanceLoading">
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #6366f1, #818cf8)">
            <el-icon color="#fff" :size="24"><DataAnalysis /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ performance.total_predictions }}</span>
            <span class="stat-label">总识别次数</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #10b981, #34d399)">
            <el-icon color="#fff" :size="24"><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ performance.avg_confidence }}%</span>
            <span class="stat-label">平均置信度</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #10b981, #6ee7b7)">
            <el-icon color="#fff" :size="24"><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ performance.high_confidence_rate }}%</span>
            <span class="stat-label">高置信度率</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #ef4444, #f87171)">
            <el-icon color="#fff" :size="24"><WarningFilled /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ performance.low_confidence_count }}</span>
            <span class="stat-label">低置信度数</span>
          </div>
        </div>
      </div>

      <!-- Category Distribution Chart -->
      <div class="chart-card">
        <h3>分类识别分布</h3>
        <div ref="categoryChart" class="chart-area"></div>
      </div>

      <!-- Error Cases -->
      <h2 class="section-title">错误识别案例</h2>
      <div class="content-card">
        <el-table :data="errorCases" v-loading="errorLoading" style="width: 100%">
          <el-table-column prop="index" label="序号" width="80" />
          <el-table-column label="图片" width="120">
            <template #default="scope">
              <el-image
                :src="`/${scope.row.image_path}`"
                :preview-src-list="[`/${scope.row.image_path}`]"
                fit="cover"
                style="width: 80px; height: 80px; border-radius: 4px;"
              />
            </template>
          </el-table-column>
          <el-table-column prop="predicted_class" label="预测分类" width="120">
            <template #default="scope">
              <el-tag type="danger">{{ scope.row.predicted_class }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="correct_class" label="正确分类" width="120">
            <template #default="scope">
              <el-tag type="success">{{ scope.row.correct_class }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="confidence" label="置信度" width="100">
            <template #default="scope">
              {{ scope.row.confidence }}%
            </template>
          </el-table-column>
          <el-table-column prop="comment" label="用户反馈" min-width="200" />
          <el-table-column prop="created_at" label="识别时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- Upload Model Dialog -->
    <el-dialog v-model="showUploadDialog" title="上传模型" width="500px">
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :limit="1"
        accept=".pth"
        :on-change="handleFileChange"
      >
        <template #trigger>
          <el-button type="primary">选择文件</el-button>
        </template>
        <template #tip>
          <div class="el-upload__tip">
            只支持 .pth 格式的模型文件
          </div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpload" :loading="uploading">
          上传
        </el-button>
      </template>
    </el-dialog>

    <!-- Compare Dialog -->
    <el-dialog v-model="showCompareDialog" title="模型性能对比" width="800px">
      <el-table :data="comparisonData" v-loading="compareLoading" style="width: 100%">
        <el-table-column prop="model_name" label="模型名称" min-width="150" />
        <el-table-column prop="total_predictions" label="识别次数" width="120" />
        <el-table-column prop="avg_confidence" label="平均置信度" width="120">
          <template #default="scope">
            {{ scope.row.avg_confidence }}%
          </template>
        </el-table-column>
        <el-table-column prop="high_confidence_rate" label="高置信度率" width="120">
          <template #default="scope">
            {{ scope.row.high_confidence_rate }}%
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import AdminLayout from '@/components/AdminLayout.vue'

const modelInfo = ref({
  model_name: '',
  model_file: '',
  model_size_mb: 0,
  model_updated: '',
  num_classes: 0,
  categories: []
})

const modelList = ref([])
const performance = ref({
  total_predictions: 0,
  avg_confidence: 0,
  high_confidence_rate: 0,
  low_confidence_count: 0,
  category_distribution: []
})

const errorCases = ref([])
const infoLoading = ref(false)
const listLoading = ref(false)
const performanceLoading = ref(false)
const errorLoading = ref(false)
const categoryChart = ref(null)
const showUploadDialog = ref(false)
const uploading = ref(false)
const uploadFile = ref(null)
const uploadRef = ref(null)
const showCompareDialog = ref(false)
const compareLoading = ref(false)
const comparisonData = ref([])

// Track chart instance for cleanup
let chartInstance = null

// 获取模型信息
const fetchModelInfo = async () => {
  infoLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('/api/model/info', {
      headers: { Authorization: `Bearer ${token}` }
    })
    modelInfo.value = response.data
  } catch (error) {
    ElMessage.error('获取模型信息失败')
  } finally {
    infoLoading.value = false
  }
}

// 获取模型列表
const fetchModelList = async () => {
  listLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('/api/model/list', {
      headers: { Authorization: `Bearer ${token}` }
    })
    modelList.value = response.data.models
  } catch (error) {
    ElMessage.error('获取模型列表失败')
  } finally {
    listLoading.value = false
  }
}

// 获取性能统计
const fetchPerformance = async () => {
  performanceLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('/api/model/performance', {
      headers: { Authorization: `Bearer ${token}` }
    })
    performance.value = response.data
    await nextTick()
    initCategoryChart()
  } catch (error) {
    ElMessage.error('获取性能统计失败')
  } finally {
    performanceLoading.value = false
  }
}

// 获取错误案例
const fetchErrorCases = async () => {
  errorLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('/api/model/error-cases', {
      headers: { Authorization: `Bearer ${token}` }
    })
    errorCases.value = response.data.items
  } catch (error) {
    ElMessage.error('获取错误案例失败')
  } finally {
    errorLoading.value = false
  }
}

// 切换模型
const handleSwitchModel = async (modelName) => {
  try {
    await ElMessageBox.confirm(
      `确定要切换到模型 ${modelName} 吗？`,
      '切换模型',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const token = localStorage.getItem('token')
    await axios.post('/api/model/switch', null, {
      params: { model_name: modelName },
      headers: { Authorization: `Bearer ${token}` }
    })

    ElMessage.success('模型切换成功')
    fetchModelInfo()
    fetchModelList()
    fetchPerformance()
    fetchErrorCases()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '模型切换失败')
    }
  }
}

// 删除模型
const handleDeleteModel = async (modelName) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模型 ${modelName} 吗？此操作不可恢复！`,
      '删除模型',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const token = localStorage.getItem('token')
    await axios.delete('/api/model/delete', {
      params: { model_name: modelName },
      headers: { Authorization: `Bearer ${token}` }
    })

    ElMessage.success('模型删除成功')
    fetchModelList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '模型删除失败')
    }
  }
}

// 文件选择
const handleFileChange = (file) => {
  uploadFile.value = file.raw
}

// 上传模型
const handleUpload = async () => {
  if (!uploadFile.value) {
    ElMessage.warning('请选择文件')
    return
  }

  uploading.value = true
  try {
    const token = localStorage.getItem('token')
    const formData = new FormData()
    formData.append('file', uploadFile.value)

    await axios.post('/api/model/upload', formData, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'multipart/form-data'
      }
    })

    ElMessage.success('模型上传成功')
    showUploadDialog.value = false
    uploadFile.value = null
    uploadRef.value?.clearFiles()
    fetchModelList()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '模型上传失败')
  } finally {
    uploading.value = false
  }
}

// 初始化分类分布图表
const initCategoryChart = () => {
  if (categoryChart.value && performance.value.category_distribution.length > 0) {
    if (chartInstance && !chartInstance.isDisposed()) {
      chartInstance.dispose()
    }
    chartInstance = echarts.init(categoryChart.value)
    chartInstance.setOption({
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        right: 10,
        top: 'center'
      },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{c}'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        data: performance.value.category_distribution.map(item => ({
          name: item.category,
          value: item.count
        }))
      }]
    })
  }
}

// 获取模型对比数据
const fetchComparisonData = async () => {
  compareLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('/api/model/compare', {
      headers: { Authorization: `Bearer ${token}` }
    })
    comparisonData.value = response.data.models
  } catch (error) {
    ElMessage.error('获取模型对比数据失败')
  } finally {
    compareLoading.value = false
  }
}

// 监听对比对话框打开
watch(showCompareDialog, (newVal) => {
  if (newVal) {
    fetchComparisonData()
  }
})

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// Resize handler
const handleResize = () => {
  if (chartInstance && !chartInstance.isDisposed()) {
    chartInstance.resize()
  }
}

onMounted(() => {
  fetchModelInfo()
  fetchModelList()
  fetchPerformance()
  fetchErrorCases()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance && !chartInstance.isDisposed()) {
    chartInstance.dispose()
  }
  chartInstance = null
})
</script>

<style scoped>
.model-page {
  padding: var(--space-2) 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
}

.page-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: var(--space-3);
}

.section-title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: var(--space-8) 0 var(--space-5) 0;
}

.section-title:first-of-type {
  margin-top: 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: var(--space-8) 0 var(--space-5) 0;
}

.section-header .section-title {
  margin: 0;
}

/* Info Grid */
.info-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-5);
}

.info-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--space-5) var(--space-6);
  background: var(--bg-elevated);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.info-label {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  font-weight: var(--font-medium);
}

.info-value {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  word-break: break-all;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-5);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-5) var(--space-6);
  background: var(--bg-elevated);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
}

.stat-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.stat-value {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  font-weight: var(--font-medium);
}

/* Content Card */
.content-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: var(--space-5) var(--space-6);
  overflow: hidden;
}

/* Chart Card */
.chart-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: var(--space-5) var(--space-6);
  margin-top: var(--space-5);
}

.chart-card h3 {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-4) 0;
}

.chart-area {
  width: 100%;
  height: 300px;
}

/* Responsive */
@media (max-width: 1200px) {
  .info-grid,
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-4);
  }

  .info-grid,
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
