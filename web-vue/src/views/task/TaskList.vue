<!-- 分析任务列表页面 -->
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { AnalysisTask } from '@/types/task'
import { getTaskList, deleteTask, getTaskStatus } from '@/api/task'
import { getResultsByTaskId } from '@/api/result'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
// 是否是管理员
const isAdmin = computed(() => userStore.userInfo?.role === 1)

// 查询参数
const queryParams = ref({
    current: 1,
    size: 10,
    name: undefined,
    algorithm: undefined,
    status: undefined,
    imageId: undefined
})

// 表格数据
const tableData = ref<AnalysisTask[]>([])
const total = ref(0)
const loading = ref(false)

// 获取任务列表
const getList = async () => {
    try {
        loading.value = true
        const res = await getTaskList(queryParams.value)
        tableData.value = res.records
        total.value = res.total
    } catch (error: any) {
        ElMessage.error(error.message || '获取任务列表失败')
    } finally {
        loading.value = false
    }
}

// 查询
const handleQuery = () => {
    queryParams.value.current = 1
    getList()
}

// 重置
const handleReset = () => {
    queryParams.value = {
        current: 1,
        size: 10,
        name: undefined,
        algorithm: undefined,
        status: undefined,
        imageId: undefined
    }
    getList()
}

// 查看结果
const handleViewResults = async (row: AnalysisTask) => {
    try {
        const results = await getResultsByTaskId(row.id)
        // TODO: 显示结果列表
        console.log(results)
    } catch (error: any) {
        ElMessage.error(error.message || '获取结果失败')
    }
}

// 删除任务
const handleDelete = async (row: AnalysisTask) => {
    try {
        await ElMessageBox.confirm('确认要删除该任务吗？', '提示', {
            type: 'warning'
        })
        await deleteTask(row.id)
        ElMessage.success('删除成功')
        getList()
    } catch (error: any) {
        if (error !== 'cancel') {
            ElMessage.error(error.message || '删除失败')
        }
    }
}

// 刷新任务状态
const handleRefreshStatus = async (row: AnalysisTask) => {
    try {
        const status = await getTaskStatus(row.id)
        row.status = status
    } catch (error: any) {
        ElMessage.error(error.message || '获取状态失败')
    }
}

// 页码改变
const handleCurrentChange = (current: number) => {
    queryParams.value.current = current
    getList()
}

// 页大小改变
const handleSizeChange = (size: number) => {
    queryParams.value.size = size
    queryParams.value.current = 1
    getList()
}

// 获取状态标签类型
const getStatusType = (status: number) => {
    switch (status) {
        case 0:
            return 'info'
        case 1:
            return 'warning'
        case 2:
            return 'success'
        case 3:
            return 'danger'
        default:
            return 'info'
    }
}

// 获取状态文本
const getStatusText = (status: number) => {
    switch (status) {
        case 0:
            return '等待中'
        case 1:
            return '处理中'
        case 2:
            return '已完成'
        case 3:
            return '失败'
        default:
            return '未知'
    }
}

onMounted(() => {
    getList()
})
</script>

<template>
    <div class="app-container">
        <!-- 搜索区域 -->
        <el-card class="search-card">
            <el-form :model="queryParams" inline>
                <el-form-item label="任务名称">
                    <el-input
                        v-model="queryParams.name"
                        placeholder="请输入任务名称"
                        clearable
                        @keyup.enter="handleQuery"
                    />
                </el-form-item>
                <el-form-item label="算法">
                    <el-input
                        v-model="queryParams.algorithm"
                        placeholder="请输入算法名称"
                        clearable
                        @keyup.enter="handleQuery"
                    />
                </el-form-item>
                <el-form-item label="状态">
                    <el-select v-model="queryParams.status" placeholder="请选择状态" clearable>
                        <el-option label="等待中" :value="0" />
                        <el-option label="处理中" :value="1" />
                        <el-option label="已完成" :value="2" />
                        <el-option label="失败" :value="3" />
                    </el-select>
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click="handleQuery">查询</el-button>
                    <el-button @click="handleReset">重置</el-button>
                </el-form-item>
            </el-form>
        </el-card>

        <!-- 表格区域 -->
        <el-card class="table-card">
            <el-table
                v-loading="loading"
                :data="tableData"
                border
                style="width: 100%"
            >
                <el-table-column type="index" label="序号" width="60" />
                <!-- 管理员可以看到创建者 -->
                <el-table-column 
                    v-if="isAdmin" 
                    prop="username" 
                    label="创建者" 
                    width="120" 
                    show-overflow-tooltip 
                />
                <el-table-column prop="name" label="任务名称" min-width="150" show-overflow-tooltip />
                <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
                <el-table-column prop="algorithm" label="算法" width="120" />
                <el-table-column prop="status" label="状态" width="100">
                    <template #default="{ row }">
                        <el-tag :type="getStatusType(row.status)">
                            {{ getStatusText(row.status) }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column prop="startTime" label="开始时间" width="180" />
                <el-table-column prop="endTime" label="结束时间" width="180" />
                <el-table-column prop="createTime" label="创建时间" width="180" />
                <el-table-column label="操作" width="200" fixed="right">
                    <template #default="{ row }">
                        <el-button link type="primary" @click="handleViewResults(row)">查看结果</el-button>
                        <el-button link type="warning" @click="handleRefreshStatus(row)">刷新状态</el-button>
                        <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
                    </template>
                </el-table-column>
            </el-table>

            <!-- 分页 -->
            <div class="pagination">
                <el-pagination
                    v-model:current-page="queryParams.current"
                    v-model:page-size="queryParams.size"
                    :total="total"
                    :page-sizes="[10, 20, 50, 100]"
                    layout="total, sizes, prev, pager, next, jumper"
                    @size-change="handleSizeChange"
                    @current-change="handleCurrentChange"
                />
            </div>
        </el-card>
    </div>
</template>

<style scoped>
.app-container {
    padding: 20px;
}

.search-card {
    margin-bottom: 20px;
}

.table-card {
    margin-bottom: 20px;
}

.pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
}
</style> 