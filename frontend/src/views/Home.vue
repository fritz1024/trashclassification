<template>
  <div class="home">
    <!-- 公告区域 -->
    <el-row :gutter="20" v-if="announcements.length > 0">
      <el-col :span="24">
        <el-alert
          v-for="announcement in announcements"
          :key="announcement.id"
          :title="announcement.title"
          :type="announcement.type"
          :closable="true"
          show-icon
          style="margin-bottom: 16px;"
        >
          {{ announcement.content }}
        </el-alert>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="24">
        <div class="hero-section">
          <h1>智能垃圾分类识别系统</h1>
          <p>基于 MobileNetV2 深度学习模型，准确率达 80%</p>
          <el-button type="primary" size="large" @click="$router.push('/classify')">
            开始识别
          </el-button>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="features">
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon size="40"><Camera /></el-icon>
            </div>
          </template>
          <h3>智能识别</h3>
          <p>上传垃圾图片，AI 自动识别分类</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon size="40"><DataAnalysis /></el-icon>
            </div>
          </template>
          <h3>数据统计</h3>
          <p>查看识别历史和数据分析</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon size="40"><Reading /></el-icon>
            </div>
          </template>
          <h3>知识科普</h3>
          <p>学习垃圾分类知识和环保理念</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const announcements = ref([])

// 获取已发布的公告
const fetchAnnouncements = async () => {
  try {
    const response = await axios.get('/api/announcements/list', {
      params: {
        skip: 0,
        limit: 5,
        published_only: true
      }
    })
    announcements.value = response.data.items
  } catch (error) {
    console.error('获取公告失败:', error)
  }
}

onMounted(() => {
  fetchAnnouncements()
})
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.hero-section {
  text-align: center;
  padding: 80px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  color: white;
  margin-bottom: 40px;
}

.hero-section h1 {
  font-size: 48px;
  margin-bottom: 20px;
}

.hero-section p {
  font-size: 20px;
  margin-bottom: 30px;
}

.features {
  margin-top: 40px;
}

.card-header {
  text-align: center;
  color: #409eff;
}

.el-card h3 {
  text-align: center;
  margin: 20px 0 10px;
}

.el-card p {
  text-align: center;
  color: #666;
}
</style>
