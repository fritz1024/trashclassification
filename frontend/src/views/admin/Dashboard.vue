<template>
  <div class="dashboard">
    <el-collapse v-model="activeNames" class="dashboard-collapse">
      <!-- 数据概览 -->
      <el-collapse-item title="数据概览" name="overview">
        <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="总用户数" :value="stats.total_users">
            <template #prefix>
              <el-icon class="stat-icon" color="#409eff"><User /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="总识别次数" :value="stats.total_predictions">
            <template #prefix>
              <el-icon class="stat-icon" color="#67c23a"><Picture /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="活跃用户" :value="stats.active_users">
            <template #prefix>
              <el-icon class="stat-icon" color="#e6a23c"><UserFilled /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="今日识别" :value="todayCount">
            <template #prefix>
              <el-icon class="stat-icon" color="#f56c6c"><TrendCharts /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>
      </el-collapse-item>

      <!-- 识别数据分析 -->
      <el-collapse-item title="识别数据分析" name="prediction">
        <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>分类统计 Top 10</span>
            </div>
          </template>
          <div ref="categoryChart" style="width: 100%; height: 350px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>最近30天识别趋势</span>
            </div>
          </template>
          <div ref="trendChart" style="width: 100%; height: 350px;"></div>
        </el-card>
      </el-col>
    </el-row>
      </el-collapse-item>

      <!-- 用户活跃度分析 -->
      <el-collapse-item title="用户活跃度分析" name="activity">
        <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>用户活跃度趋势（最近30天）</span>
            </div>
          </template>
          <div ref="activeUsersChart" style="width: 100%; height: 350px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>活跃用户排行榜 Top 10</span>
            </div>
          </template>
          <div ref="topUsersChart" style="width: 100%; height: 350px;"></div>
        </el-card>
      </el-col>
    </el-row>
      </el-collapse-item>

      <!-- 数据报表 -->
      <el-collapse-item title="数据报表" name="report">
        <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <h3 style="margin: 0;">数据报表</h3>
              <el-button
                v-if="reportData"
                type="success"
                @click="exportToExcel"
              >
                导出 Excel
              </el-button>
            </div>
          </template>

          <!-- 报表类型选择 -->
          <el-tabs v-model="activeReportTab" @tab-change="handleReportTabChange">
            <el-tab-pane label="周报" name="weekly" />
            <el-tab-pane label="月报" name="monthly" />
            <el-tab-pane label="自定义报表" name="custom" />
          </el-tabs>

          <!-- 自定义时间段选择 -->
          <div v-if="activeReportTab === 'custom'" style="margin: 20px 0;">
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
              style="margin-left: 10px;"
            >
              生成报表
            </el-button>
          </div>

          <!-- 报表图表 -->
          <div v-if="reportData" v-loading="reportLoading">
            <el-row :gutter="20" style="margin-top: 20px;">
              <el-col :span="12">
                <el-card>
                  <template #header>识别趋势</template>
                  <div ref="reportTrendChart" style="width: 100%; height: 300px;"></div>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card>
                  <template #header>分类统计</template>
                  <div ref="reportCategoryChart" style="width: 100%; height: 300px;"></div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>
    </el-row>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import * as XLSX from 'xlsx'
import { ElMessage } from 'element-plus'
import { User, Picture, UserFilled, TrendCharts } from '@element-plus/icons-vue'

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

onMounted(() => {
  fetchStats()
  fetchActivityStats()
  fetchReport('weekly')  // 默认加载周报
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

/* 折叠面板样式 */
.dashboard-collapse {
  border: none;
}

.dashboard-collapse :deep(.el-collapse-item) {
  margin-bottom: 20px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}

.dashboard-collapse :deep(.el-collapse-item__header) {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  background: #f5f7fa;
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
}

.dashboard-collapse :deep(.el-collapse-item__wrap) {
  border: none;
  background: #fff;
}

.dashboard-collapse :deep(.el-collapse-item__content) {
  padding: 20px;
}

/* 统计卡片 */
.stat-card {
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-icon {
  font-size: 24px;
}

/* 图表卡片 */
.chart-card {
  margin-bottom: 20px;
}

.card-header {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* 迷你统计卡片 */
.mini-stat {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #ebeef5;
  transition: all 0.3s;
}

.mini-stat:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.mini-stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.mini-stat-content {
  flex: 1;
}

.mini-stat-title {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.mini-stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.mini-stat-desc {
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 2px;
}
</style>
