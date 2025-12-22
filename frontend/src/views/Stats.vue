<template>
  <div class="stats">
    <el-card>
      <template #header>
        <h2>数据统计</h2>
      </template>

      <el-row :gutter="20" v-loading="loading">
        <el-col :span="6">
          <el-statistic title="总识别次数" :value="stats.total_predictions" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="平均置信度" :value="stats.avg_confidence" suffix="%" />
        </el-col>
      </el-row>

      <el-divider />

      <el-row :gutter="20">
        <el-col :span="12">
          <div ref="categoryChart" style="width: 100%; height: 400px;"></div>
        </el-col>
        <el-col :span="12">
          <div ref="trendChart" style="width: 100%; height: 400px;"></div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getUserStats } from '@/api/stats'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const route = useRoute()
const stats = ref({
  total_predictions: 0,
  avg_confidence: 0,
  category_stats: [],
  daily_stats: []
})
const loading = ref(false)
const categoryChart = ref(null)
const trendChart = ref(null)

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

const initCharts = () => {
  // 分类统计饼图
  if (categoryChart.value) {
    const chart1 = echarts.init(categoryChart.value)
    chart1.setOption({
      title: { text: '垃圾分类统计' },
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: '50%',
        data: stats.value.category_stats.map(item => ({
          name: item.category,
          value: item.count
        }))
      }]
    })
  }

  // 识别趋势折线图
  if (trendChart.value) {
    const chart2 = echarts.init(trendChart.value)
    chart2.setOption({
      title: { text: '最近7天识别趋势' },
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: stats.value.daily_stats.map(item => item.date)
      },
      yAxis: { type: 'value' },
      series: [{
        type: 'line',
        data: stats.value.daily_stats.map(item => item.count),
        smooth: true
      }]
    })
  }
}

onMounted(() => {
  fetchStats()
})

// 监听路由变化，当进入此页面时重新加载数据
watch(() => route.path, (newPath) => {
  if (newPath === '/stats') {
    fetchStats()
  }
})
</script>

<style scoped>
.stats {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
