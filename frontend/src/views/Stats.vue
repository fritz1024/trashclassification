<template>
  <div class="stats-page container">
    <div class="page-header">
      <h1>数据统计</h1>
    </div>

    <div class="stats-grid" v-loading="loading">
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #10b981, #059669);">
          <el-icon :size="24" color="#fff"><DataAnalysis /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.total_predictions }}</span>
          <span class="stat-label">总识别次数</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #6366f1, #4f46e5);">
          <el-icon :size="24" color="#fff"><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.avg_confidence }}<small>%</small></span>
          <span class="stat-label">平均置信度</span>
        </div>
      </div>
    </div>

    <div class="charts-row">
      <div class="chart-card">
        <h3>垃圾分类统计</h3>
        <div ref="categoryChart" class="chart-area"></div>
      </div>
      <div class="chart-card">
        <h3>最近 7 天识别趋势</h3>
        <div ref="trendChart" class="chart-area"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useThemeStore } from '@/store/theme'
import { getUserStats } from '@/api/stats'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const route = useRoute()
const themeStore = useThemeStore()
const stats = ref({ total_predictions: 0, avg_confidence: 0, category_stats: [], daily_stats: [] })
const loading = ref(false)
const categoryChart = ref(null)
const trendChart = ref(null)
let chart1 = null
let chart2 = null

const fetchStats = async () => {
  loading.value = true
  try {
    stats.value = await getUserStats()
    await nextTick()
    initCharts()
  } catch (error) {
    ElMessage.error('获取统计数据失败')
  } finally {
    loading.value = false
  }
}

const getChartTheme = () => {
  const isDark = themeStore.isDark
  return {
    textColor: isDark ? '#94a3b8' : '#64748b',
    borderColor: isDark ? '#334155' : '#e2e8f0',
    bgColor: 'transparent',
  }
}

const initCharts = () => {
  const theme = getChartTheme()

  if (categoryChart.value) {
    chart1?.dispose()
    chart1 = echarts.init(categoryChart.value)
    chart1.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 0, textStyle: { color: theme.textColor } },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        itemStyle: { borderRadius: 8, borderColor: theme.bgColor, borderWidth: 2 },
        label: { color: theme.textColor },
        data: stats.value.category_stats.map(item => ({ name: item.category, value: item.count })),
        color: ['#10b981', '#6366f1', '#f59e0b', '#ef4444', '#64748b']
      }]
    })
  }

  if (trendChart.value) {
    chart2?.dispose()
    chart2 = echarts.init(trendChart.value)
    chart2.setOption({
      tooltip: { trigger: 'axis' },
      grid: { top: 20, right: 20, bottom: 30, left: 50 },
      xAxis: { type: 'category', data: stats.value.daily_stats.map(item => item.date), axisLine: { lineStyle: { color: theme.borderColor } }, axisLabel: { color: theme.textColor } },
      yAxis: { type: 'value', splitLine: { lineStyle: { color: theme.borderColor } }, axisLabel: { color: theme.textColor } },
      series: [{
        type: 'line',
        data: stats.value.daily_stats.map(item => item.count),
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { width: 3, color: '#10b981' },
        itemStyle: { color: '#10b981' },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(16, 185, 129, 0.25)' }, { offset: 1, color: 'rgba(16, 185, 129, 0.02)' }]) }
      }]
    })
  }
}

const handleResize = () => { chart1?.resize(); chart2?.resize() }

onMounted(() => {
  fetchStats()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  chart1?.dispose()
  chart2?.dispose()
  window.removeEventListener('resize', handleResize)
})

watch(() => route.path, (p) => { if (p === '/stats') fetchStats() })
watch(() => themeStore.isDark, () => { if (stats.value.total_predictions > 0) initCharts() })
</script>

<style scoped>
.stats-page {
  padding: var(--space-8) var(--space-6);
  max-width: 1100px;
}

.page-header {
  margin-bottom: var(--space-6);
}

.page-header h1 {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-5);
  margin-bottom: var(--space-6);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--space-5);
  background: var(--bg-elevated);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
}

.stat-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-value {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  line-height: 1;
}

.stat-value small {
  font-size: var(--text-lg);
  font-weight: var(--font-medium);
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  margin-top: var(--space-1);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.charts-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-5);
}

.chart-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
}

.chart-card h3 {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-bottom: var(--space-4);
}

.chart-area {
  width: 100%;
  height: 340px;
}

@media (max-width: 768px) {
  .stats-page { padding: var(--space-4); }
  .stats-grid { grid-template-columns: 1fr; }
  .charts-row { grid-template-columns: 1fr; }
  .chart-area { height: 260px; }
}
</style>
