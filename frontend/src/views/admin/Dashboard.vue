<template>
  <AdminLayout>
    <div class="dashboard-page">
      <h1 class="page-title">数据概览</h1>

      <!-- Stats Grid -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #6366f1, #818cf8)">
            <el-icon :size="24" color="#fff"><User /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.total_users }}</span>
            <span class="stat-label">总用户数</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #10b981, #34d399)">
            <el-icon :size="24" color="#fff"><Picture /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.total_predictions }}</span>
            <span class="stat-label">总识别次数</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #f59e0b, #fbbf24)">
            <el-icon :size="24" color="#fff"><UserFilled /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.active_users }}</span>
            <span class="stat-label">活跃用户</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #ef4444, #f87171)">
            <el-icon :size="24" color="#fff"><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ todayCount }}</span>
            <span class="stat-label">今日识别</span>
          </div>
        </div>
      </div>

      <!-- Charts: Prediction Analysis -->
      <h2 class="section-title">识别数据分析</h2>
      <div class="charts-grid">
        <div class="chart-card">
          <h3>分类统计 Top 10</h3>
          <div ref="categoryChart" class="chart-area"></div>
        </div>
        <div class="chart-card">
          <h3>最近30天识别趋势</h3>
          <div ref="trendChart" class="chart-area"></div>
        </div>
      </div>

      <!-- Charts: User Activity -->
      <h2 class="section-title">用户活跃度分析</h2>
      <div class="charts-grid">
        <div class="chart-card">
          <h3>用户活跃度趋势（最近30天）</h3>
          <div ref="activeUsersChart" class="chart-area"></div>
        </div>
        <div class="chart-card">
          <h3>活跃用户排行榜 Top 10</h3>
          <div ref="topUsersChart" class="chart-area"></div>
        </div>
      </div>

      <!-- Report Section -->
      <h2 class="section-title">数据报表</h2>
      <div class="content-card">
        <div class="report-header">
          <el-tabs v-model="activeReportTab" @tab-change="handleReportTabChange">
            <el-tab-pane label="周报" name="weekly" />
            <el-tab-pane label="月报" name="monthly" />
            <el-tab-pane label="自定义报表" name="custom" />
          </el-tabs>
          <el-button
            v-if="reportData"
            type="success"
            @click="exportToExcel"
          >
            导出 Excel
          </el-button>
        </div>

        <!-- Custom date range -->
        <div v-if="activeReportTab === 'custom'" class="custom-range">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
          <el-button
            type="primary"
            @click="fetchCustomReport"
            :loading="reportLoading"
          >
            生成报表
          </el-button>
        </div>

        <!-- Report charts -->
        <div v-if="reportData" v-loading="reportLoading" class="report-charts">
          <div class="charts-grid">
            <div class="chart-card">
              <h3>识别趋势</h3>
              <div ref="reportTrendChart" class="chart-area"></div>
            </div>
            <div class="chart-card">
              <h3>分类统计</h3>
              <div ref="reportCategoryChart" class="chart-area"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import * as XLSX from 'xlsx'
import { ElMessage } from 'element-plus'
import { User, Picture, UserFilled, TrendCharts } from '@element-plus/icons-vue'
import AdminLayout from '@/components/AdminLayout.vue'

// 控制折叠面板展开状态（默认展开数据概览和识别数据分析）
const activeNames = ref(['overview', 'prediction'])

const stats = ref({
  total_users: 0,
  total_predictions: 0,
  active_users: 0,
  category_stats: [],
  daily_stats: []
})

const activityStats = ref({
  daily_active_users: [],
  top_active_users: []
})

const categoryChart = ref(null)
const trendChart = ref(null)
const activeUsersChart = ref(null)
const topUsersChart = ref(null)

// 报表相关变量
const activeReportTab = ref('weekly')
const dateRange = ref(null)
const reportData = ref(null)
const reportLoading = ref(false)
const reportTrendChart = ref(null)
const reportCategoryChart = ref(null)

// Track chart instances for cleanup
const chartInstances = []

const todayCount = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  const todayData = stats.value.daily_stats.find(item => item.date === today)
  return todayData ? todayData.count : 0
})

const fetchStats = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('/api/stats/global', {
      headers: { Authorization: `Bearer ${token}` }
    })
    stats.value = response.data
    await nextTick()
    initCharts()
  } catch (error) {
    ElMessage.error('获取统计数据失败')
  }
}

const fetchActivityStats = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('/api/stats/user-activity', {
      headers: { Authorization: `Bearer ${token}` }
    })
    activityStats.value = response.data
    await nextTick()
    initActivityCharts()
  } catch (error) {
    ElMessage.error('获取活跃度数据失败')
  }
}

const initCharts = () => {
  if (categoryChart.value) {
    const chart1 = echarts.init(categoryChart.value)
    chartInstances.push(chart1)
    chart1.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: stats.value.category_stats.map(item => item.category)
      },
      yAxis: { type: 'value' },
      series: [{
        type: 'bar',
        data: stats.value.category_stats.map(item => item.count),
        itemStyle: { color: '#409eff' }
      }]
    })
  }

  if (trendChart.value) {
    const chart2 = echarts.init(trendChart.value)
    chartInstances.push(chart2)
    chart2.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: stats.value.daily_stats.map(item => item.date)
      },
      yAxis: { type: 'value' },
      series: [{
        type: 'line',
        data: stats.value.daily_stats.map(item => item.count),
        smooth: true,
        areaStyle: { color: 'rgba(64, 158, 255, 0.2)' }
      }]
    })
  }
}

const initActivityCharts = () => {
  // 用户活跃度趋势图
  if (activeUsersChart.value) {
    const chart3 = echarts.init(activeUsersChart.value)
    chartInstances.push(chart3)
    chart3.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: activityStats.value.daily_active_users.map(item => item.date)
      },
      yAxis: {
        type: 'value',
        name: '活跃用户数'
      },
      series: [{
        type: 'line',
        data: activityStats.value.daily_active_users.map(item => item.count),
        smooth: true,
        itemStyle: { color: '#67c23a' },
        areaStyle: { color: 'rgba(103, 194, 58, 0.2)' }
      }]
    })
  }

  // 活跃用户排行榜
  if (topUsersChart.value) {
    const chart4 = echarts.init(topUsersChart.value)
    chartInstances.push(chart4)
    chart4.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'value',
        name: '识别次数'
      },
      yAxis: {
        type: 'category',
        data: activityStats.value.top_active_users.map(item => item.username).reverse()
      },
      series: [{
        type: 'bar',
        data: activityStats.value.top_active_users.map(item => item.prediction_count).reverse(),
        itemStyle: { color: '#e6a23c' }
      }]
    })
  }
}

// 报表相关函数
const fetchReport = async (type) => {
  reportLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`/api/reports/${type}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    reportData.value = response.data
    await nextTick()
    initReportCharts()
  } catch (error) {
    ElMessage.error('获取报表数据失败')
  } finally {
    reportLoading.value = false
  }
}

const fetchCustomReport = async () => {
  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请选择日期范围')
    return
  }

  reportLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('/api/reports/custom', {
      params: {
        start_date: dateRange.value[0],
        end_date: dateRange.value[1]
      },
      headers: { Authorization: `Bearer ${token}` }
    })
    reportData.value = response.data
    await nextTick()
    initReportCharts()
  } catch (error) {
    ElMessage.error('获取报表数据失败')
  } finally {
    reportLoading.value = false
  }
}

const handleReportTabChange = (tab) => {
  if (tab === 'weekly' || tab === 'monthly') {
    fetchReport(tab)
  } else {
    reportData.value = null
  }
}

const exportToExcel = () => {
  if (!reportData.value) {
    ElMessage.warning('没有可导出的数据')
    return
  }

  try {
    // 创建工作簿
    const wb = XLSX.utils.book_new()

    // 准备识别趋势数据
    const trendData = reportData.value.daily_stats.map(item => ({
      '日期': item.date,
      '识别次数': item.count
    }))
    const trendSheet = XLSX.utils.json_to_sheet(trendData)
    XLSX.utils.book_append_sheet(wb, trendSheet, '识别趋势')

    // 准备分类统计数据
    const categoryData = reportData.value.category_stats.map(item => ({
      '分类': item.category,
      '识别次数': item.count
    }))
    const categorySheet = XLSX.utils.json_to_sheet(categoryData)
    XLSX.utils.book_append_sheet(wb, categorySheet, '分类统计')

    // 生成文件名
    const reportType = activeReportTab.value === 'weekly' ? '周报' :
                       activeReportTab.value === 'monthly' ? '月报' : '自定义报表'
    const filename = `${reportType}_${new Date().toISOString().split('T')[0]}.xlsx`

    // 导出文件
    XLSX.writeFile(wb, filename)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const initReportCharts = () => {
  // 识别趋势图
  if (reportTrendChart.value && reportData.value) {
    const chart1 = echarts.init(reportTrendChart.value)
    chartInstances.push(chart1)
    chart1.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: reportData.value.daily_stats.map(item => item.date)
      },
      yAxis: { type: 'value', name: '识别次数' },
      series: [{
        type: 'line',
        data: reportData.value.daily_stats.map(item => item.count),
        smooth: true,
        itemStyle: { color: '#409eff' },
        areaStyle: { color: 'rgba(64, 158, 255, 0.2)' }
      }]
    })
  }

  // 分类统计图
  if (reportCategoryChart.value && reportData.value) {
    const chart2 = echarts.init(reportCategoryChart.value)
    chartInstances.push(chart2)
    chart2.setOption({
      tooltip: { trigger: 'item' },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [{
        type: 'pie',
        radius: '60%',
        data: reportData.value.category_stats.map(item => ({
          name: item.category,
          value: item.count
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    })
  }
}

// Resize handler
const handleResize = () => {
  chartInstances.forEach(chart => {
    if (chart && !chart.isDisposed()) {
      chart.resize()
    }
  })
}

onMounted(() => {
  fetchStats()
  fetchActivityStats()
  fetchReport('weekly')  // 默认加载周报
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstances.forEach(chart => {
    if (chart && !chart.isDisposed()) {
      chart.dispose()
    }
  })
  chartInstances.length = 0
})
</script>

<style scoped>
.dashboard-page {
  padding: var(--space-2) 0;
}

.page-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0 0 var(--space-6) 0;
}

.section-title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: var(--space-8) 0 var(--space-5) 0;
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

/* Charts Grid */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-5);
}

.chart-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: var(--space-5) var(--space-6);
}

.chart-card h3 {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-4) 0;
}

.chart-area {
  width: 100%;
  height: 350px;
}

/* Content Card */
.content-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: var(--space-6);
}

/* Report */
.report-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.report-header :deep(.el-tabs) {
  flex: 1;
}

.report-header :deep(.el-tabs__header) {
  margin-bottom: 0;
}

.custom-range {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin: var(--space-5) 0;
}

.report-charts {
  margin-top: var(--space-5);
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
