<!-- 分析任务创建页面 -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { RemoteSensingImage } from '@/types/image'
import type { Algorithm, TaskCreateParams } from '@/types/task'
import { getImageList } from '@/api/image'
import { getAlgorithms, createTask } from '@/api/task'

// 表单数据
const form = ref<TaskCreateParams>({
    imageId: undefined,
    name: '',
    description: '',
    algorithm: '',
    parameters: '{}'
})

// 影像列表
const imageList = ref<RemoteSensingImage[]>([])
// 算法列表
const algorithmList = ref<Record<string, Algorithm>>({})
// 当前选中的算法
const currentAlgorithm = ref<Algorithm>()
// 算法参数
const algorithmParams = ref<Record<string, number>>({})

// 获取影像列表
const getImages = async () => {
    try {
        const res = await getImageList({
            current: 1,
            size: 1000,
            status: 1
        })
        imageList.value = res.records
    } catch (error: any) {
        ElMessage.error(error.message || '获取影像列表失败')
    }
}

// 获取算法列表
const getAlgorithmList = async () => {
    try {
        algorithmList.value = await getAlgorithms()
    } catch (error: any) {
        ElMessage.error(error.message || '获取算法列表失败')
    }
}

// 算法选择改变
const handleAlgorithmChange = (algorithm: string) => {
    currentAlgorithm.value = algorithmList.value[algorithm]
    // 初始化参数为默认值
    algorithmParams.value = {}
    if (currentAlgorithm.value) {
        Object.entries(currentAlgorithm.value.parameters).forEach(([key, param]) => {
            algorithmParams.value[key] = param.default
        })
    }
}

// 提交表单
const handleSubmit = async () => {
    try {
        // 设置算法参数
        form.value.parameters = JSON.stringify(algorithmParams.value)
        await createTask(form.value)
        ElMessage.success('创建成功')
        // 重置表单
        form.value = {
            imageId: undefined,
            name: '',
            description: '',
            algorithm: '',
            parameters: '{}'
        }
        algorithmParams.value = {}
        currentAlgorithm.value = undefined
    } catch (error: any) {
        ElMessage.error(error.message || '创建失败')
    }
}

onMounted(() => {
    getImages()
    getAlgorithmList()
})
</script>

<template>
    <div class="app-container">
        <el-card>
            <el-form :model="form" label-width="100px">
                <el-form-item label="影像选择" required>
                    <el-select v-model="form.imageId" placeholder="请选择影像">
                        <el-option
                            v-for="image in imageList"
                            :key="image.id"
                            :label="image.name"
                            :value="image.id"
                        />
                    </el-select>
                </el-form-item>

                <el-form-item label="任务名称" required>
                    <el-input v-model="form.name" placeholder="请输入任务名称" />
                </el-form-item>

                <el-form-item label="任务描述">
                    <el-input
                        v-model="form.description"
                        type="textarea"
                        placeholder="请输入任务描述"
                    />
                </el-form-item>

                <el-form-item label="算法选择" required>
                    <el-select
                        v-model="form.algorithm"
                        placeholder="请选择算法"
                        @change="handleAlgorithmChange"
                    >
                        <el-option
                            v-for="(algo, key) in algorithmList"
                            :key="key"
                            :label="algo.name"
                            :value="key"
                        />
                    </el-select>
                </el-form-item>

                <!-- 算法参数 -->
                <template v-if="currentAlgorithm">
                    <el-divider>算法参数</el-divider>
                    <el-form-item
                        v-for="(param, key) in currentAlgorithm.parameters"
                        :key="key"
                        :label="param.description"
                    >
                        <el-input-number
                            v-model="algorithmParams[key]"
                            :min="param.min"
                            :max="param.max"
                            :step="param.type === 'float' ? 0.1 : 1"
                        />
                    </el-form-item>
                </template>

                <el-form-item>
                    <el-button type="primary" @click="handleSubmit">创建任务</el-button>
                </el-form-item>
            </el-form>
        </el-card>
    </div>
</template>

<style scoped>
.app-container {
    padding: 20px;
}
</style> 