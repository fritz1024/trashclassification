<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="总用户数" :value="stats.total_users">
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="总识别次数" :value="stats.total_predictions">
            <template #prefix>
              <el-icon><Picture /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="活跃用户" :value="stats.active_users">
            <template #prefix>
              <el-icon><UserFilled /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="今日识别" :value="todayCount">
            <template #prefix>
              <el-icon><TrendCharts /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <h3>分类统计 Top 10</h3>
          </template>
          <div ref="categoryChart" style="width: 100%; height: 400px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <h3>最近30天识别趋势</h3>
          </template>
          <div ref="trendChart" style="width: 100%; height: 400px;"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

const stats = ref({
  total_users: 0,
  total_predictions: 0,
  active_users: 0,
  category_stats: [],
  daily_stats: []
})

const categoryChart = ref(null)
const trendChart = ref(null)

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

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.dashboard {
  /* 样式由 App.vue 的 el-main 提供 */
}
</style>
