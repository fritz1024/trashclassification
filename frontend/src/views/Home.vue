<template>
  <div class="home">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-bg"></div>
      <div class="hero-content container">
        <div class="hero-badge">
          <el-icon :size="14"><Promotion /></el-icon>
          智能环保守护者
        </div>
        <h1>基于深度学习的<br/>智能垃圾分类系统</h1>
        <p class="hero-desc">上传图片，即时识别。让 AI 为您提供精准的垃圾分类指导，共建绿色生活。</p>
        <div class="hero-actions">
          <el-button type="primary" size="large" round @click="$router.push('/classify')">
            <el-icon><MagicStick /></el-icon> 立即体验
          </el-button>
          <el-button size="large" round @click="$router.push('/ai-chat')">
            <el-icon><ChatDotRound /></el-icon> AI 助手
          </el-button>
        </div>

        <div class="hero-upload-hint" @click="$router.push('/classify')">
          <div class="upload-box">
            <el-icon :size="40" color="var(--color-primary-light)"><UploadFilled /></el-icon>
            <p>将垃圾图片拖拽至此，或点击上传</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Announcements -->
    <section class="announcements container" v-if="announcements.length > 0">
      <div class="section-header">
        <h2>通知公告</h2>
      </div>
      <div class="announcement-list">
        <div v-for="item in announcements" :key="item.id" class="announcement-card">
          <el-tag :type="getTypeColor(item.type)" size="small" round>{{ getTypeName(item.type) }}</el-tag>
          <div class="announcement-body">
            <span class="announcement-title">{{ item.title }}</span>
            <span class="announcement-text">{{ item.content }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features">
      <div class="container">
        <div class="section-header">
          <h2>强大的 AI 识别能力</h2>
          <p>结合前沿的深度学习技术，让垃圾分类变得简单而有趣</p>
        </div>

        <div class="feature-grid">
          <div class="feature-card" v-for="(feat, i) in features" :key="i">
            <div class="feature-icon" :style="{ background: feat.bg }">
              <el-icon :size="24" color="#fff"><component :is="feat.icon" /></el-icon>
            </div>
            <h3>{{ feat.title }}</h3>
            <p>{{ feat.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Categories Section -->
    <section class="categories">
      <div class="container">
        <div class="section-header">
          <h2>支持的垃圾类别</h2>
          <p>覆盖生活中各种垃圾类别，4 大分类共 265 种细分类别</p>
        </div>

        <div class="category-grid">
          <div class="category-card" v-for="(cat, i) in categories" :key="i" :style="{ '--cat-color': cat.color }">
            <div class="category-icon">{{ cat.emoji }}</div>
            <h4>{{ cat.name }}</h4>
            <span class="category-count">{{ cat.count }} 种</span>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const announcements = ref([])

const features = [
  { icon: 'MagicStick', title: '深度学习引擎', desc: '采用 MobileNetV2 模型，上传图片即可精准识别垃圾类别。', bg: 'linear-gradient(135deg, #10b981, #059669)' },
  { icon: 'Odometer', title: '265 种垃圾类别', desc: '全面覆盖厨余垃圾、可回收物、有害垃圾、其他垃圾四大类。', bg: 'linear-gradient(135deg, #6366f1, #4f46e5)' },
  { icon: 'Timer', title: '实时云端记录', desc: '自动保存识别历史，数据统计一目了然，支持导出报告。', bg: 'linear-gradient(135deg, #f59e0b, #d97706)' },
]

const categories = [
  { name: '厨余垃圾', count: 52, emoji: '🍎', color: '#10b981' },
  { name: '可回收物', count: 149, emoji: '♻️', color: '#6366f1' },
  { name: '其他垃圾', count: 50, emoji: '🗑️', color: '#64748b' },
  { name: '有害垃圾', count: 14, emoji: '☠️', color: '#ef4444' },
]

const fetchAnnouncements = async () => {
  try {
    const response = await axios.get('/api/announcements/list', { params: { published_only: true, limit: 5 } })
    announcements.value = response.data.items
  } catch (error) {
    console.error('获取公告失败:', error)
  }
}

const getTypeColor = (type) => ({ info: '', warning: 'warning', success: 'success', error: 'danger' }[type] || '')
const getTypeName = (type) => ({ info: '信息', warning: '警告', success: '成功', error: '错误' }[type] || type)

onMounted(() => fetchAnnouncements())
</script>

<style scoped>
/* === Hero === */
.hero {
  position: relative;
  padding: var(--space-20) 0;
  text-align: center;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(160deg, var(--color-primary-lightest) 0%, var(--bg-secondary) 50%, var(--bg-primary) 100%);
  z-index: 0;
}

[data-theme="dark"] .hero-bg {
  background: linear-gradient(160deg, rgba(16, 185, 129, 0.08) 0%, var(--bg-secondary) 50%, var(--bg-primary) 100%);
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  background: var(--color-primary-lightest);
  color: var(--color-primary-dark);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  margin-bottom: var(--space-6);
  border: 1px solid var(--color-primary-lighter);
}

.hero h1 {
  font-size: var(--text-5xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  line-height: var(--leading-tight);
  margin-bottom: var(--space-5);
}

.hero-desc {
  font-size: var(--text-lg);
  color: var(--text-secondary);
  max-width: 560px;
  margin: 0 auto var(--space-8);
  line-height: var(--leading-relaxed);
}

.hero-actions {
  display: flex;
  gap: var(--space-4);
  justify-content: center;
  margin-bottom: var(--space-12);
}

.hero-upload-hint {
  cursor: pointer;
  max-width: 480px;
  margin: 0 auto;
}

.upload-box {
  background: var(--bg-elevated);
  border: 2px dashed var(--border-primary);
  border-radius: var(--radius-xl);
  padding: var(--space-10) var(--space-8);
  transition: all var(--transition-normal);
}

.upload-box:hover {
  border-color: var(--color-primary);
  background: var(--bg-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-primary);
}

.upload-box p {
  margin-top: var(--space-3);
  color: var(--text-tertiary);
  font-size: var(--text-base);
}

/* === Sections Common === */
.section-header {
  text-align: center;
  margin-bottom: var(--space-10);
}

.section-header h2 {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin-bottom: var(--space-3);
}

.section-header p {
  font-size: var(--text-md);
  color: var(--text-secondary);
}

/* === Announcements === */
.announcements {
  padding: var(--space-12) var(--space-6);
}

.announcement-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  max-width: 800px;
  margin: 0 auto;
}

.announcement-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  background: var(--bg-elevated);
  padding: var(--space-4) var(--space-5);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-secondary);
  transition: all var(--transition-fast);
}

.announcement-card:hover {
  box-shadow: var(--shadow-sm);
}

.announcement-body {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  flex: 1;
  min-width: 0;
}

.announcement-title {
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  font-size: var(--text-base);
  white-space: nowrap;
}

.announcement-text {
  color: var(--text-tertiary);
  font-size: var(--text-sm);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* === Features === */
.features {
  padding: var(--space-16) 0;
  background: var(--bg-primary);
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-6);
}

.feature-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-xl);
  padding: var(--space-8) var(--space-6);
  text-align: center;
  transition: all var(--transition-normal);
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-card-hover);
  border-color: var(--color-primary-lighter);
}

.feature-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-5);
}

.feature-card h3 {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-bottom: var(--space-3);
}

.feature-card p {
  font-size: var(--text-base);
  color: var(--text-secondary);
  line-height: var(--leading-relaxed);
}

/* === Categories === */
.categories {
  padding: var(--space-16) 0;
  background: var(--bg-secondary);
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-5);
}

.category-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-xl);
  padding: var(--space-8) var(--space-5);
  text-align: center;
  transition: all var(--transition-normal);
  cursor: default;
}

.category-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--cat-color);
}

.category-icon {
  font-size: 40px;
  margin-bottom: var(--space-4);
}

.category-card h4 {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}

.category-count {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  font-weight: var(--font-medium);
}

/* === Responsive === */
@media (max-width: 1024px) {
  .feature-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .category-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .hero {
    padding: var(--space-12) 0;
  }
  .hero h1 {
    font-size: var(--text-3xl);
  }
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
  .feature-grid {
    grid-template-columns: 1fr;
  }
  .category-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .announcement-body {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-1);
  }
}
</style>
