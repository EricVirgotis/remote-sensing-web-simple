<!-- 分析结果查看页面 -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { AnalysisResult } from '@/types/result'
import type { AnalysisTask } from '@/types/task'
import { getTaskDetail } from '@/api/task'
import { getResultsByTaskId, getResultFileUrl } from '@/api/result'

const route = useRoute()
const taskId = Number(route.params.taskId)

// 任务信息
const task = ref<AnalysisTask>()
// 结果列表
const resultList = ref<AnalysisResult[]>([])
// 加载状态
const loading = ref(false)

// 获取任务详情
const getTask = async () => {
    try {
        task.value = await getTaskDetail(taskId)
    } catch (error: any) {
        ElMessage.error(error.message || '获取任务详情失败')
    }
}

// 获取结果列表
const getResults = async () => {
    try {
        loading.value = true
        resultList.value = await getResultsByTaskId(taskId)
    } catch (error: any) {
        ElMessage.error(error.message || '获取结果列表失败')
    } finally {
        loading.value = false
    }
}

// 查看结果文件
const handleViewResult = async (result: AnalysisResult) => {
    try {
        const url = await getResultFileUrl(result.bucketName, result.objectKey)
        window.open(url)
    } catch (error: any) {
        ElMessage.error(error.message || '获取结果文件失败')
    }
}

// 格式化评估指标
const formatMetrics = (metrics: string) => {
    try {
        const data = JSON.parse(metrics)
        return Object.entries(data)
            .map(([key, value]) => `${key}: ${(value as number).toFixed(4)}`)
            .join(', ')
    } catch {
        return metrics
    }
}

onMounted(() => {
    getTask()
    getResults()
})
</script>

<template>
    <div class="app-container">
        <!-- 任务信息 -->
        <el-card v-if="task" class="task-card">
            <template #header>
                <div class="card-header">
                    <span>任务信息</span>
                </div>
            </template>
            <el-descriptions :column="2" border>
                <el-descriptions-item label="任务名称">{{ task.name }}</el-descriptions-item>
                <el-descriptions-item label="算法">{{ task.algorithm }}</el-descriptions-item>
                <el-descriptions-item label="状态">
                    <el-tag :type="task.status === 2 ? 'success' : task.status === 3 ? 'danger' : 'warning'">
                        {{ task.status === 0 ? '等待中' : task.status === 1 ? '处理中' : task.status === 2 ? '已完成' : '失败' }}
                    </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="创建时间">{{ task.createTime }}</el-descriptions-item>
                <el-descriptions-item label="开始时间">{{ task.startTime || '-' }}</el-descriptions-item>
                <el-descriptions-item label="结束时间">{{ task.endTime || '-' }}</el-descriptions-item>
                <el-descriptions-item label="描述" :span="2">{{ task.description }}</el-descriptions-item>
                <el-descriptions-item label="参数" :span="2">{{ task.parameters }}</el-descriptions-item>
            </el-descriptions>
        </el-card>

        <!-- 结果列表 -->
        <el-card v-loading="loading" class="result-card">
            <template #header>
                <div class="card-header">
                    <span>结果列表</span>
                </div>
            </template>
            <el-table :data="resultList" border style="width: 100%">
                <el-table-column type="index" label="序号" width="60" />
                <el-table-column prop="name" label="结果名称" min-width="150" show-overflow-tooltip />
                <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
                <el-table-column prop="resultType" label="类型" width="120" />
                <el-table-column prop="metrics" label="评估指标" min-width="200">
                    <template #default="{ row }">
                        {{ formatMetrics(row.metrics) }}
                    </template>
                </el-table-column>
                <el-table-column prop="createTime" label="创建时间" width="180" />
                <el-table-column label="操作" width="100" fixed="right">
                    <template #default="{ row }">
                        <el-button link type="primary" @click="handleViewResult(row)">查看</el-button>
                    </template>
                </el-table-column>
            </el-table>
        </el-card>
    </div>
</template>

<style scoped>
.app-container {
    padding: 20px;
}

.task-card {
    margin-bottom: 20px;
}

.result-card {
    margin-bottom: 20px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
</style> 