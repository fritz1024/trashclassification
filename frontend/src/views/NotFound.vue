<template>
  <div class="not-found container">
    <div class="nf-card">
      <span class="nf-code">404</span>
      <h1>页面不存在</h1>
      <p>您访问的页面可能已被移除或暂时不可用</p>
      <el-button type="primary" round @click="$router.push('/')">
        <el-icon><HomeFilled /></el-icon> 返回首页
      </el-button>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.not-found {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - var(--navbar-height) - 80px);
  padding: var(--space-8);
}

.nf-card {
  text-align: center;
}

.nf-code {
  font-size: 120px;
  font-weight: var(--font-bold);
  color: var(--border-primary);
  line-height: 1;
}

.nf-card h1 {
  font-size: var(--text-2xl);
  color: var(--text-primary);
  margin: var(--space-4) 0 var(--space-2);
}

.nf-card p {
  color: var(--text-tertiary);
  margin-bottom: var(--space-6);
}
</style>
