<template>
  <div class="train-task-detail">
    <!-- 返回按钮 -->
    <el-button
      :icon="ArrowLeft"
      style="margin-bottom: 20px"
      @click="handleBack"
    >
      返回列表
    </el-button>
    
    <!-- 任务详情 -->
    <el-descriptions
      v-loading="loading"
      title="任务详情"
      :column="2"
      border
    >
      <el-descriptions-item label="任务名称">
        {{ taskDetail?.name }}
      </el-descriptions-item>
      <el-descriptions-item label="任务状态">
        <el-tag
          :type="taskDetail?.status === 0 ? 'warning' : taskDetail?.status === 1 ? 'success' : 'danger'"
        >
          {{ taskDetail?.status === 0 ? '进行中' : taskDetail?.status === 1 ? '已完成' : '失败' }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="训练轮数">
        {{ taskDetail?.epochs }}
      </el-descriptions-item>
      <el-descriptions-item label="批次大小">
        {{ taskDetail?.batchSize }}
      </el-descriptions-item>
      <el-descriptions-item label="学习率">
        {{ taskDetail?.learningRate }}
      </el-descriptions-item>
      <el-descriptions-item label="训练准确率">
        {{ taskDetail?.accuracy ? (taskDetail.accuracy * 100).toFixed(2) + '%' : '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="训练损失">
        {{ taskDetail?.loss ? taskDetail.loss.toFixed(4) : '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="创建时间">
        {{ taskDetail?.createTime }}
      </el-descriptions-item>
      <el-descriptions-item label="更新时间">
        {{ taskDetail?.updateTime }}
      </el-descriptions-item>
      <el-descriptions-item
        v-if="taskDetail?.status === 2"
        label="失败原因"
        :span="2"
      >
        {{ taskDetail?.errorMsg }}
      </el-descriptions-item>
    </el-descriptions>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getTrainTaskDetail } from '@/api/train'
import type { TrainTask } from '@/types/train'
import { TrainTaskStatus } from '@/types/train'

const route = useRoute()
const router = useRouter()

// 加载状态
const loading = ref(false)

// 任务详情
const taskDetail = ref<TrainTask>()

// 自动刷新定时器
const autoRefreshInterval = ref<number>()

// 获取任务详情
const getDetail = async () => {
  loading.value = true
  try {
    const id = Number(route.params.id)
    if (isNaN(id)) {
      ElMessage.error('任务ID不正确')
      return
    }
    
    const detail = await getTrainTaskDetail(id)
    taskDetail.value = detail
    
    // 如果任务进行中，开启自动刷新
    if (detail.status === TrainTaskStatus.RUNNING) {
      startAutoRefresh()
    } else {
      stopAutoRefresh()
    }
  } catch (error) {
    console.error('获取任务详情失败：', error)
    ElMessage.error('获取任务详情失败')
  } finally {
    loading.value = false
  }
}

// 开启自动刷新
const startAutoRefresh = () => {
  if (!autoRefreshInterval.value) {
    autoRefreshInterval.value = window.setInterval(() => {
      getDetail()
    }, 5000)
  }
}

// 停止自动刷新
const stopAutoRefresh = () => {
  if (autoRefreshInterval.value) {
    window.clearInterval(autoRefreshInterval.value)
    autoRefreshInterval.value = undefined
  }
}

// 返回按钮
const handleBack = () => {
  router.back()
}

// 组件挂载时获取详情
onMounted(() => {
  getDetail()
})

// 组件卸载前停止自动刷新
onBeforeUnmount(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.train-task-detail {
  padding: 20px;
}
</style> 