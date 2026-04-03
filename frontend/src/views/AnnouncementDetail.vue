<template>
  <div class="announcement-detail-page">
    <div v-if="loading" class="loading">
      <el-icon class="is-loading"><Loading /></el-icon>
    </div>

    <div v-else-if="announcement" class="announcement-content">
      <el-button @click="goBack" class="back-btn">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>

      <h1>{{ announcement.title }}</h1>
      <div class="meta">{{ formatTime(announcement.created_at) }}</div>
      <div class="content" v-html="announcement.content"></div>
    </div>

    <el-empty v-else description="公告不存在" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Loading } from '@element-plus/icons-vue'
import { getAnnouncement } from '@/api/announcement'

const route = useRoute()
const router = useRouter()
const announcement = ref(null)
const loading = ref(true)

const loadAnnouncement = async () => {
  try {
    announcement.value = await getAnnouncement(route.params.id)
  } catch (error) {
    ElMessage.error('加载公告失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => router.back()
const formatTime = (time) => new Date(time).toLocaleString('zh-CN')

onMounted(() => loadAnnouncement())
</script>

<style scoped>
.announcement-detail-page {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--space-6);
}

.loading {
  text-align: center;
  padding: var(--space-10);
  font-size: var(--text-2xl);
  color: var(--color-primary);
}

.announcement-content {
  background: var(--bg-elevated);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
}

.back-btn {
  margin-bottom: var(--space-4);
}

.announcement-content h1 {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0 0 var(--space-3);
}

.meta {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  margin-bottom: var(--space-6);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--border-secondary);
}

.content {
  line-height: 1.8;
  color: var(--text-primary);
}

.content :deep(h1), .content :deep(h2), .content :deep(h3) {
  margin: var(--space-4) 0 var(--space-2);
  font-weight: var(--font-semibold);
}

.content :deep(p) {
  margin: var(--space-2) 0;
}

.content :deep(ul), .content :deep(ol) {
  margin: var(--space-2) 0;
  padding-left: var(--space-6);
}

.content :deep(img) {
  max-width: 100%;
  border-radius: var(--radius-md);
}
</style>
