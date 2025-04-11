<!-- 遥感影像列表页面 -->
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { RemoteSensingImage } from '@/types/image'
import { getImageList, deleteImage, getImageFileUrl } from '@/api/image'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
// 是否是管理员
const isAdmin = computed(() => userStore.userInfo?.role === 1)

// 查询参数
const queryParams = ref({
    current: 1,
    size: 10,
    name: '',
    format: '',
    status: 1  // 默认查询状态为正常的影像
})

// 表格数据
const tableData = ref<RemoteSensingImage[]>([])
const total = ref(0)
const loading = ref(false)

// 获取影像列表
const getList = async () => {
    try {
        loading.value = true
        const res = await getImageList(queryParams.value)
        if (res) {
            tableData.value = res.records
            total.value = res.total
        } else {
            tableData.value = []
            total.value = 0
        }
    } catch (error: any) {
        ElMessage.error(error.message || '获取影像列表失败')
        tableData.value = []
        total.value = 0
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
        name: '',
        format: '',
        status: 1  // 重置时也保持查询正常状态的影像
    }
    getList()
}

// 查看影像
const handleView = async (row: RemoteSensingImage) => {
    try {
        const url = await getImageFileUrl(row.bucketName, row.objectKey)
        window.open(url)
    } catch (error: any) {
        ElMessage.error(error.message || '获取影像文件失败')
    }
}

// 删除影像
const handleDelete = async (row: RemoteSensingImage) => {
    try {
        await ElMessageBox.confirm('确认要删除该影像吗？', '提示', {
            type: 'warning'
        })
        await deleteImage(row.id)
        ElMessage.success('删除成功')
        getList()
    } catch (error: any) {
        if (error !== 'cancel') {
            ElMessage.error(error.message || '删除失败')
        }
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

onMounted(() => {
    getList()
})
</script>

<template>
    <div class="app-container">
        <!-- 搜索区域 -->
        <el-card class="search-card">
            <el-form :model="queryParams" inline>
                <el-form-item label="影像名称">
                    <el-input
                        v-model="queryParams.name"
                        placeholder="请输入影像名称"
                        clearable
                        @keyup.enter="handleQuery"
                    />
                </el-form-item>
                <el-form-item label="文件格式">
                    <el-select v-model="queryParams.format" placeholder="请选择格式" clearable>
                        <el-option label="TIFF" value="tiff" />
                        <el-option label="JPEG" value="jpeg" />
                        <el-option label="PNG" value="png" />
                    </el-select>
                </el-form-item>
                <el-form-item label="状态">
                    <el-select v-model="queryParams.status" placeholder="请选择状态" clearable>
                        <el-option label="正常" :value="1" />
                        <el-option label="已删除" :value="0" />
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
                <!-- 管理员可以看到上传用户 -->
                <el-table-column 
                    v-if="isAdmin" 
                    prop="username" 
                    label="上传用户" 
                    width="120" 
                    show-overflow-tooltip 
                />
                <el-table-column prop="name" label="影像名称" min-width="150" show-overflow-tooltip />
                <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
                <el-table-column prop="format" label="格式" width="100" />
                <el-table-column prop="size" label="大小" width="120">
                    <template #default="{ row }">
                        {{ (row.size / 1024 / 1024).toFixed(2) }} MB
                    </template>
                </el-table-column>
                <el-table-column prop="width" label="宽度" width="100" />
                <el-table-column prop="height" label="高度" width="100" />
                <el-table-column prop="bands" label="波段数" width="100" />
                <el-table-column prop="status" label="状态" width="100">
                    <template #default="{ row }">
                        <el-tag :type="row.status === 1 ? 'success' : 'danger'">
                            {{ row.status === 1 ? '正常' : '已删除' }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column prop="createTime" label="创建时间" width="180" />
                <el-table-column label="操作" width="150" fixed="right">
                    <template #default="{ row }">
                        <el-button link type="primary" @click="handleView(row)">查看</el-button>
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