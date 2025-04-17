<template>
  <!-- 该组件不需要UI元素，仅处理WebSocket消息 -->
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import wsClient from '@/utils/websocket'
import type { WebSocketMessage } from '@/utils/websocket'
import { TrainTaskStatus } from '@/types/train'
import { ElMessage } from 'element-plus'

// 定义消息处理函数
const handleTrainingStatus = (message: WebSocketMessage) => {
  try {
    const { taskId, status, accuracy, loss } = message.data
    
    // 确保状态值与TrainTaskStatus枚举一致
    // 检查WebSocket消息中的状态值是否与枚举定义匹配
    // 根据TrainTaskStatus枚举：PENDING=0, RUNNING=1, FAILED=2, COMPLETED=3
    console.log(`收到训练状态更新：任务ID=${taskId}, 状态=${status}`)
    
    // 确保状态值与TrainTaskStatus枚举一致
    let mappedStatus: TrainTaskStatus
    
    // 根据后端返回的状态值正确映射到前端枚举
    // 这里假设后端可能使用不同的状态值，需要映射
    switch(Number(status)) {
      case 0: mappedStatus = TrainTaskStatus.PENDING; break;
      case 1: mappedStatus = TrainTaskStatus.RUNNING; break;
      case 2: mappedStatus = TrainTaskStatus.FAILED; break;
      case 3: mappedStatus = TrainTaskStatus.COMPLETED; break;
      default: mappedStatus = Number(status) as TrainTaskStatus; // 兜底处理
    }
    
    // 触发自定义事件通知父组件更新状态
    const event = new CustomEvent('training-status-update', {
      detail: {
        taskId,
        status: mappedStatus,
        accuracy,
        loss
      }
    })
    window.dispatchEvent(event)

    // 根据状态显示相应的消息
    if (mappedStatus === TrainTaskStatus.COMPLETED) {
      ElMessage.success(`训练任务 ${taskId} 已完成`)
    } else if (mappedStatus === TrainTaskStatus.FAILED) {
      ElMessage.error(`训练任务 ${taskId} 失败`)
    }
  } catch (error) {
    console.error('处理训练状态消息失败:', error)
  }
}

// 组件挂载时订阅消息
onMounted(() => {
  wsClient.addMessageHandler(handleTrainingStatus)
})

// 组件卸载时取消订阅
onUnmounted(() => {
  wsClient.removeMessageHandler(handleTrainingStatus)
})
</script>