<template>
  <div class="home">
    <div class="hero-section">
      <div class="hero-badge">智能环保守护者</div>
      <h1>基于深度学习的<br/>智能垃圾分类系统</h1>
      <p>上传图片，即时识别。让AI为您提供精准的垃圾分类指导，共建绿色生活。</p>
      <el-button type="success" size="large" round @click="$router.push('/classify')">
        立即开始体验
      </el-button>

      <div class="upload-demo">
        <div class="demo-box">
          <el-icon size="60" color="#10b981"><Picture /></el-icon>
          <p>将垃圾图片拖拽至此，或点击上传</p>
        </div>
      </div>
    </div>

    <div class="announcements-section" v-if="announcements.length > 0">
      <h2>📢 通知公告</h2>
      <div class="announcement-list">
        <div v-for="item in announcements" :key="item.id" class="announcement-item">
          <el-tag :type="getTypeColor(item.type)" size="small">{{ getTypeName(item.type) }}</el-tag>
          <span class="announcement-title">{{ item.title }}</span>
          <span class="announcement-content">{{ item.content }}</span>
        </div>
      </div>
    </div>

    <div class="features-section">
      <h2>强大的AI识别能力</h2>
      <p class="subtitle">结合前沿的深度学习技术，让垃圾分类变得简单而有趣</p>

      <el-row :gutter="20" class="feature-cards">
        <el-col :span="8">
          <div class="feature-card">
            <el-icon size="40" color="#10b981"><MagicStick /></el-icon>
            <h3>深度学习引擎</h3>
            <p>采用业内领先的深度学习算法，并上传你的图像进行识别分类，精确度高达90%以上。</p>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="feature-card">
            <el-icon size="40" color="#10b981"><Odometer /></el-icon>
            <h3>10大常见垃圾</h3>
            <p>全面覆盖生活中的10种，塑料、金属、玻璃等10种垃圾类型识别，满足您的各类需求。</p>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="feature-card">
            <el-icon size="40" color="#10b981"><Timer /></el-icon>
            <h3>实时云端记录</h3>
            <p>自动保存你的识别历史记录并进行云端同步，随时随地查看您的历史记录。</p>
          </div>
        </el-col>
      </el-row>
    </div>

    <div class="categories-section">
      <h2>支持的垃圾类别</h2>
      <p class="subtitle">我们训练了海量数据，覆盖生活中各种垃圾类别</p>

      <div class="category-tags">
        <el-tag size="large" effect="plain">厨余垃圾</el-tag>
        <el-tag size="large" effect="plain">塑料</el-tag>
        <el-tag size="large" effect="plain">干电池</el-tag>
        <el-tag size="large" effect="plain">旧衣服</el-tag>
        <el-tag size="large" effect="plain">玻璃</el-tag>
        <el-tag size="large" effect="plain">纸板</el-tag>
        <el-tag size="large" effect="plain">金属</el-tag>
        <el-tag size="large" effect="plain">陶瓷罐</el-tag>
        <el-tag size="large" effect="plain">鞋</el-tag>
        <el-tag size="large" effect="plain">纸张</el-tag>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const announcements = ref([])

const fetchAnnouncements = async () => {
  try {
    const response = await axios.get('/api/announcements/list', {
      params: { published_only: true, limit: 5 }
    })
    announcements.value = response.data.items
  } catch (error) {
    console.error('获取公告失败:', error)
  }
}

const getTypeColor = (type) => {
  const colors = { info: '', warning: 'warning', success: 'success', error: 'danger' }
  return colors[type] || ''
}

const getTypeName = (type) => {
  const names = { info: '信息', warning: '警告', success: '成功', error: '错误' }
  return names[type] || type
}

onMounted(() => {
  fetchAnnouncements()
})
</script>

<style scoped>
.home {
  width: 100%;
  padding: 0;
  margin: 0;
}

.hero-section {
  text-align: center;
  padding: 80px 40px;
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 50%, #6ee7b7 100%);
  margin: 0;
}

.hero-badge {
  display: inline-block;
  background: rgba(16, 185, 129, 0.2);
  color: #047857;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  margin-bottom: 20px;
  border: 1px solid #10b981;
}

.hero-section h1 {
  font-size: 42px;
  margin-bottom: 20px;
  color: #064e3b;
  font-weight: 700;
  line-height: 1.3;
}

.hero-section p {
  font-size: 16px;
  margin-bottom: 30px;
  color: #065f46;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.upload-demo {
  margin-top: 40px;
}

.demo-box {
  background: white;
  border: 2px dashed #10b981;
  border-radius: 12px;
  padding: 40px;
  max-width: 500px;
  margin: 0 auto;
}

.demo-box p {
  margin-top: 16px;
  color: #10b981;
  font-size: 14px;
}

.announcements-section {
  padding: 60px 40px;
  background: #f0fdf4;
}

.announcements-section h2 {
  font-size: 32px;
  color: #1f2937;
  margin-bottom: 30px;
  text-align: center;
}

.announcement-list {
  max-width: 1000px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.announcement-item {
  background: white;
  padding: 20px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.announcement-title {
  font-weight: 600;
  color: #1f2937;
  font-size: 16px;
  min-width: 150px;
}

.announcement-content {
  color: #6b7280;
  font-size: 14px;
  flex: 1;
}

.features-section {
  text-align: center;
  padding: 60px 40px;
  background: white;
}

.features-section h2 {
  font-size: 32px;
  color: #1f2937;
  margin-bottom: 12px;
}

.subtitle {
  color: #6b7280;
  font-size: 16px;
  margin-bottom: 40px;
}

.feature-cards {
  margin-top: 40px;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
  padding: 0 40px;
}

.feature-card {
  background: #f9fafb;
  padding: 30px 20px;
  border-radius: 12px;
  transition: transform 0.3s, box-shadow 0.3s;
  text-align: center;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(16, 185, 129, 0.2);
}

.feature-card h3 {
  margin: 20px 0 12px;
  color: #1f2937;
  font-size: 18px;
}

.feature-card p {
  color: #6b7280;
  font-size: 14px;
  line-height: 1.6;
}

.categories-section {
  text-align: center;
  padding: 60px 40px;
  background: #f9fafb;
}

.categories-section h2 {
  font-size: 32px;
  color: #1f2937;
  margin-bottom: 12px;
}

.category-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
  margin-top: 30px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.category-tags .el-tag {
  padding: 10px 20px;
  font-size: 15px;
  border-color: #10b981;
  color: #047857;
}
</style>
