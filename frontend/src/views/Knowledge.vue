<template>
  <div class="knowledge">
    <el-card>
      <template #header>
        <h2>垃圾分类知识科普</h2>
      </template>

      <el-tabs v-model="activeCategory" @tab-change="handleCategoryChange">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="可回收垃圾" name="recyclable" />
        <el-tab-pane label="有害垃圾" name="harmful" />
        <el-tab-pane label="厨余垃圾" name="kitchen" />
        <el-tab-pane label="其他垃圾" name="other" />
      </el-tabs>

      <el-row :gutter="20" v-loading="loading">
        <el-col :span="8" v-for="item in knowledgeList" :key="item.id">
          <el-card shadow="hover" class="knowledge-card">
            <h3>{{ item.title }}</h3>
            <el-tag :type="getCategoryType(item.category)">{{ getCategoryName(item.category) }}</el-tag>
            <p>{{ item.content }}</p>
            <el-divider />
            <div v-if="item.examples && item.examples.length > 0">
              <strong>常见示例：</strong>
              <el-tag
                v-for="(example, index) in item.examples"
                :key="index"
                size="small"
                style="margin: 5px;"
              >
                {{ example }}
              </el-tag>
            </div>
            <div v-if="item.tips" style="margin-top: 10px;">
              <strong>处理建议：</strong>
              <p style="color: #666;">{{ item.tips }}</p>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-empty v-if="!loading && knowledgeList.length === 0" description="暂无知识数据" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getKnowledgeList } from '@/api/knowledge'

const activeCategory = ref('all')
const knowledgeList = ref([])
const loading = ref(false)

// 分类映射（英文值 -> 中文显示名）
const categoryNameMap = {
  'recyclable': '可回收垃圾',
  'harmful': '有害垃圾',
  'kitchen': '厨余垃圾',
  'other': '其他垃圾'
}

const getCategoryName = (category) => {
  return categoryNameMap[category] || category
}

const getCategoryType = (category) => {
  const typeMap = {
    'recyclable': 'success',
    'harmful': 'danger',
    'kitchen': 'warning',
    'other': 'info'
  }
  return typeMap[category] || 'info'
}

const fetchKnowledge = async () => {
  loading.value = true
  try {
    const params = {}
    if (activeCategory.value !== 'all') {
      params.category = activeCategory.value
    }

    const response = await getKnowledgeList(params)
    knowledgeList.value = response.items || []
  } catch (error) {
    console.error('获取知识库失败:', error)
    ElMessage.error('获取知识库失败')
  } finally {
    loading.value = false
  }
}

const handleCategoryChange = () => {
  fetchKnowledge()
}

onMounted(() => {
  fetchKnowledge()
})
</script>

<style scoped>
.knowledge {
  max-width: 1200px;
  margin: 0 auto;
}

.knowledge-card {
  margin-bottom: 20px;
  min-height: 300px;
}

.knowledge-card h3 {
  margin-bottom: 10px;
}

.knowledge-card p {
  margin: 10px 0;
  line-height: 1.6;
}
</style>
