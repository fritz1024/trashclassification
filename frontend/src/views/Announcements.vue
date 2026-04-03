<template>
  <div class="announcements-page">
    <div class="page-header">
      <h1>系统公告</h1>
    </div>

    <div class="announcements-list" v-loading="loading">
      <el-empty v-if="!loading && announcements.length === 0" description="暂无公告" />

      <div v-for="item in announcements" :key="item.id" class="announcement-item" @click="goToDetail(item.id)">
        <h3>{{ item.title }}</h3>
        <p class="announcement-preview">{{ getPreview(item.content) }}</p>
        <div class="announcement-meta">
          <span>{{ formatTime(item.created_at) }}</span>
        </div>
      </div>

      <el-pagination
        v-if="total > pageSize"
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="loadAnnouncements"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getAnnouncements } from '@/api/announcement'

const router = useRouter()
const announcements = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const loadAnnouncements = async () => {
  loading.value = true
  try {
    const res = await getAnnouncements({
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      published_only: true
    })
    announcements.value = res.items
    total.value = res.total
  } catch (error) {
    ElMessage.error('加载公告失败')
  } finally {
    loading.value = false
  }
}

const goToDetail = (id) => {
  router.push(`/announcements/${id}`)
}

const getPreview = (html) => {
  if (!html) return '暂无内容'
  const text = html.replace(/<[^>]*>/g, '').replace(/&nbsp;/g, ' ').trim()
  return text.length > 120 ? text.substring(0, 120) + '...' : text
}

const formatTime = (time) => new Date(time).toLocaleString('zh-CN')

onMounted(() => loadAnnouncements())
</script>

<style scoped>
.announcements-page {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--space-6);
}

.page-header {
  margin-bottom: var(--space-6);
}

.page-header h1 {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
}

.announcements-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.announcement-item {
  background: var(--bg-elevated);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  cursor: pointer;
  transition: all 0.2s;
}

.announcement-item:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-md);
}

.announcement-item h3 {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-2);
}

.announcement-preview {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0 0 var(--space-3);
}

.announcement-meta {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}

.el-pagination {
  margin-top: var(--space-6);
  justify-content: center;
}
</style>
