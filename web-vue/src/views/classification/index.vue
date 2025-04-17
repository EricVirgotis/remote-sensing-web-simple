<!-- 图像分类任务列表页面 -->
<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { pageQuery, deleteTask, createTask } from '@/api/classification'
import type { ClassificationTask } from '@/types/classification'
import { fileRequest } from '@/api/file_request'
import { Refresh } from '@element-plus/icons-vue'
import { pageTrainTasks } from '@/api/train'
import type { TrainTask } from '@/types/train'
import { TrainTaskStatus } from '@/types/train'

const loading = ref(false)
const total = ref(0)
const pageSize = ref(10)
const currentPage = ref(1)
const taskList = ref<ClassificationTask[]>([])

// 训练任务相关
const trainTaskOptions = ref<TrainTask[]>([])

// 上传相关
const uploadDialogVisible = ref(false)
const uploadForm = ref({
    name: '',
    image: null as File | null,
    trainTaskId: undefined as number | undefined
})
const uploadLoading = ref(false)

// 自动刷新相关
const autoRefreshInterval = ref<number | null>(null)

// 工具函数：获取文件URL
const getObjectURL = (file: File | null): string => {
    if (!file) return ''
    return window.URL.createObjectURL(file)
}

// 开始自动刷新
const startAutoRefresh = () => {
    // 如果已经有定时器在运行，先清除
    stopAutoRefresh()
    
    // 检查是否有进行中的任务
    const hasRunningTask = taskList.value.some(task => task.status === 0)
    if (hasRunningTask) {
        // 每5秒刷新一次
        autoRefreshInterval.value = window.setInterval(() => {
            getTaskList()
        }, 5000)
    }
}

// 停止自动刷新
const stopAutoRefresh = () => {
    if (autoRefreshInterval.value) {
        clearInterval(autoRefreshInterval.value)
        autoRefreshInterval.value = null
    }
}

// 获取任务列表
const getTaskList = async () => {
    try {
        loading.value = true
        const res = await pageQuery({
            pageNum: currentPage.value,
            pageSize: pageSize.value
        })
        taskList.value = res.records
        total.value = res.total
        
        // 检查是否需要开启自动刷新
        startAutoRefresh()
    } catch (error: any) {
        ElMessage.error(error.message || '获取任务列表失败')
    } finally {
        loading.value = false
    }
}

// 处理页码变化
const handleCurrentChange = (val: number) => {
    currentPage.value = val
    getTaskList()
}

// 处理每页条数变化
const handleSizeChange = (val: number) => {
    pageSize.value = val
    currentPage.value = 1
    getTaskList()
}

// 删除任务
const handleDelete = async (row: ClassificationTask) => {
    try {
        await ElMessageBox.confirm('确认删除该任务吗？', '提示', {
            type: 'warning'
        })
        await deleteTask(row.id)
        ElMessage.success('删除成功')
        getTaskList()
    } catch (error: any) {
        if (error !== 'cancel') {
            ElMessage.error(error.message || '删除失败')
        }
    }
}

// 处理文件选择
const handleFileChange = (uploadFile: any) => {
    uploadForm.value.image = uploadFile.raw
}

// 获取训练成功的模型列表
const getTrainTaskOptions = async () => {
    try {
        const res = await pageTrainTasks({
            current: 1,
            size: 1000,
            status: TrainTaskStatus.COMPLETED
        })
        trainTaskOptions.value = res.records
    } catch (error: any) {
        ElMessage.error(error.message || '获取模型列表失败')
    }
}

// 创建任务
const handleCreate = async () => {
    if (!uploadForm.value.name) {
        ElMessage.warning('请输入任务名称')
        return
    }
    if (!uploadForm.value.image) {
        ElMessage.warning('请选择图片')
        return
    }
    if (!uploadForm.value.trainTaskId) {
        ElMessage.warning('请选择训练模型')
        return
    }
    
    try {
        uploadLoading.value = true
        const formData = new FormData()
        formData.append('name', uploadForm.value.name)
        formData.append('file', uploadForm.value.image)
        formData.append('trainTaskId', uploadForm.value.trainTaskId.toString())
        
        await createTask(formData)
        ElMessage.success('创建成功')
        uploadDialogVisible.value = false
        uploadForm.value = {
            name: '',
            image: null,
            trainTaskId: undefined
        }
        getTaskList()
    } catch (error: any) {
        ElMessage.error(error.message || '创建失败')
    } finally {
        uploadLoading.value = false
    }
}

// 获取状态文本
const getStatusText = (status: number) => {
    switch (status) {
        case 0:
            return '进行中'
        case 1:
            return '已完成'
        case 2:
            return '失败'
        default:
            return '未知'
    }
}

// 获取状态类型
const getStatusType = (status: number) => {
    switch (status) {
        case 0:
            return 'warning'
        case 1:
            return 'success'
        case 2:
            return 'danger'
        default:
            return 'info'
    }
}

// 打开上传对话框
const handleOpenUploadDialog = () => {
    uploadDialogVisible.value = true
    getTrainTaskOptions()
}

onMounted(() => {
    getTaskList()
})

onBeforeUnmount(() => {
    stopAutoRefresh()
})
</script>

<template>
    <div class="classification-container">
        <!-- 顶部操作栏 -->
        <div class="operation-bar">
            <el-button type="primary" @click="handleOpenUploadDialog">
                创建任务
            </el-button>
            <el-button @click="getTaskList">
                <el-icon><Refresh /></el-icon>
                刷新状态
            </el-button>
        </div>
        
        <!-- 任务列表 -->
        <el-table
            v-loading="loading"
            :data="taskList"
            border
            style="width: 100%"
        >
            <el-table-column prop="name" label="任务名称" min-width="120" />
            
            <el-table-column label="预览图" width="120">
                <template #default="{ row }">
                    <!-- 添加 v-if 判断 -->
                    <el-image
                      v-if="row.bucket && row.objectKey"
                      style="width: 100px; height: 100px"
                      :src="fileRequest.getFileUrl(row.bucket, row.objectKey)"
                      :preview-src-list="[fileRequest.getFileUrl(row.bucket, row.objectKey)]"
                      fit="cover"
                      lazy
                    >
                      <template #error>
                        <div class="image-slot">
                          <el-icon><icon-picture /></el-icon>
                        </div>
                      </template>
                    </el-image>
                    <span v-else>无效图片数据</span>
                </template>
            </el-table-column>
            
            <el-table-column label="预测结果" min-width="180">
                <template #default="{ row }">
                    <template v-if="row.status === 1">
                        <div>类别：{{ row.className }}（{{ row.classNameZh }}）</div>
                        <div>置信度：{{ (row.confidence * 100).toFixed(2) }}%</div>
                    </template>
                    <template v-else-if="row.status === 2">
                        <el-tooltip :content="row.errorMsg">
                            <span class="error-text">预测失败</span>
                        </el-tooltip>
                    </template>
                    <template v-else>
                        <span>预测中...</span>
                    </template>
                </template>
            </el-table-column>
            
            <el-table-column label="状态" width="100">
                <template #default="{ row }">
                    <el-tag :type="getStatusType(row.status)">
                        {{ getStatusText(row.status) }}
                    </el-tag>
                </template>
            </el-table-column>
            
            <el-table-column prop="createTime" label="创建时间" width="180" />
            
            <el-table-column label="操作" width="120" fixed="right">
                <template #default="{ row }">
                    <el-button
                        type="danger"
                        link
                        @click="handleDelete(row)"
                    >
                        删除
                    </el-button>
                </template>
            </el-table-column>
        </el-table>
        
        <!-- 分页 -->
        <div class="pagination">
            <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :total="total"
                :page-sizes="[10, 20, 50, 100]"
                layout="total, sizes, prev, pager, next"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
            />
        </div>
        
        <!-- 上传对话框 -->
        <el-dialog
            v-model="uploadDialogVisible"
            title="创建分类任务"
            width="500px"
            :close-on-click-modal="false"
            @close="uploadForm = { name: '', image: null, trainTaskId: undefined }"
        >
            <el-form :model="uploadForm" label-width="100px">
                <el-form-item label="任务名称" required>
                    <el-input v-model="uploadForm.name" placeholder="请输入任务名称" />
                </el-form-item>
                
                <el-form-item label="选择模型" required>
                    <el-select v-model="uploadForm.trainTaskId" placeholder="请选择训练成功的模型" style="width: 100%">
                        <el-option
                            v-for="item in trainTaskOptions"
                            :key="item.id"
                            :label="item.name"
                            :value="item.id"
                        >
                            <div style="display: flex; justify-content: space-between; align-items: center">
                                <span>{{ item.name }}</span>
                                <span style="color: #8492a6; font-size: 13px">准确率: {{ (item.accuracy * 100).toFixed(2) }}%</span>
                            </div>
                        </el-option>
                    </el-select>
                </el-form-item>
                
                <el-form-item label="上传图片" required>
                    <el-upload
                        class="upload-demo"
                        :auto-upload="false"
                        :show-file-list="false"
                        accept="image/*"
                        @change="handleFileChange"
                    >
                        <template v-if="uploadForm.image">
                            <img :src="getObjectURL(uploadForm.image)" style="width: 200px; height: 200px; object-fit: cover" />
                        </template>
                        <template v-else>
                            <el-button type="primary">选择图片</el-button>
                        </template>
                    </el-upload>
                </el-form-item>
            </el-form>
            
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="uploadDialogVisible = false">取消</el-button>
                    <el-button type="primary" :loading="uploadLoading" @click="handleCreate">
                        创建
                    </el-button>
                </span>
            </template>
        </el-dialog>
    </div>
</template>

<style scoped>
.classification-container {
    padding: 20px;
}

.operation-bar {
    margin-bottom: 20px;
    display: flex;
    gap: 10px;
}

.pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
}

.image-slot {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100%;
    background: #f5f7fa;
    color: #909399;
}

.error-text {
    color: #f56c6c;
}

.preview {
    margin-top: 10px;
}
</style>