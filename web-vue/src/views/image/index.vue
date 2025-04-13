<!-- 遥感影像功能入口页面 -->
<template>
  <div class="app-container">
    <el-result
      icon="warning"
      title="功能开发中"
      sub-title="遥感影像处理功能正在完善中，敬请期待..."
    >
      <template #extra>
        <el-button type="primary" @click="goHome">返回首页</el-button>
      </template>
    </el-result>
    
    <el-card class="feature-info-card">
      <template #header>
        <div class="card-header">
          <h3>关于遥感影像功能</h3>
        </div>
      </template>
      <div class="feature-info-content">
        <p>尊敬的用户，我们正在对遥感影像处理功能进行全面升级，特别是对TIFF格式遥感影像的处理支持。</p>
        <p>目前该功能暂时不可用，我们的技术团队正在加紧开发中，预计将在后续版本中推出更加强大、稳定的遥感影像处理功能。</p>
        <p>感谢您的理解与支持！</p>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

// 返回首页
const goHome = () => {
  router.push('/home')
}
</script>

<style scoped>
.app-container {
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 30px;
}

.feature-info-card {
  width: 100%;
  max-width: 800px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.feature-info-content {
  line-height: 1.8;
  color: #606266;
}
</style>