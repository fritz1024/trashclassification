<template>
  <AdminLayout>
    <div class="admin-page">
      <div class="page-header">
        <h1>系统设置</h1>
      </div>
      <div class="content-card">
        <div class="empty-state">
          <el-icon :size="48" color="var(--text-tertiary)"><Setting /></el-icon>
          <h3>系统设置功能开发中</h3>
          <p>敬请期待更多配置选项</p>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import AdminLayout from '@/components/AdminLayout.vue'
</script>

<style scoped>
.admin-page { padding: 0; }
.page-header { margin-bottom: var(--space-6); }
.page-header h1 { font-size: var(--text-2xl); font-weight: var(--font-bold); color: var(--text-primary); }
.content-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
}
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-16) 0;
  text-align: center;
}
.empty-state h3 { font-size: var(--text-lg); color: var(--text-secondary); font-weight: var(--font-semibold); }
.empty-state p { font-size: var(--text-sm); color: var(--text-tertiary); }
</style>
