<!-- 分析任务创建页面 -->
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue' // 引入 computed
import { ElMessage } from 'element-plus'
import type { RemoteSensingImage } from '@/types/image'
import type { TaskCreateParams } from '@/types/task'
import type { ClassificationModel } from '@/types/model'
import { getImageList } from '@/api/image'
import { createTask } from '@/api/task'
import { getAvailableModels } from '@/api/model'
import { useUserStore } from '@/stores/user'

// 表单数据
const form = ref<TaskCreateParams>({
    imageId: undefined,
    modelId: undefined, // 修改为 modelId
    name: '',
    description: '',
    // algorithm: '', // 移除 algorithm
    // parameters: '{}' // 移除 parameters，如果后端创建任务不再需要参数
})

// 影像列表
const imageList = ref<RemoteSensingImage[]>([])
// 模型列表
const modelList = ref<ClassificationModel[]>([])
// // 算法列表
// const algorithmList = ref<Record<string, Algorithm>>({})
// // 当前选中的算法
// const currentAlgorithm = ref<Algorithm>()
// // 算法参数
// const algorithmParams = ref<Record<string, number>>({})

// 获取影像列表
const getImages = async () => {
    try {
        const res = await getImageList({
            current: 1,
            size: 1000, // 获取足够多的影像
            status: 1
        })
        imageList.value = res.records
    } catch (error: any) {
        ElMessage.error(error.message || '获取影像列表失败')
    }
}

// 获取用户store
const userStore = useUserStore()

// 获取可用模型列表
const getModels = async () => {
    try {
        if (!userStore.userInfo?.id) {
            ElMessage.error('用户未登录')
            return
        }
        modelList.value = await getAvailableModels(userStore.userInfo.id)
    } catch (error: any) {
        ElMessage.error(error.message || '获取模型列表失败')
    }
}

// // 获取算法列表
// const getAlgorithmList = async () => {
//     try {
//         algorithmList.value = await getAlgorithms()
//     } catch (error: any) {
//         ElMessage.error(error.message || '获取算法列表失败')
//     }
// }

// // 算法选择改变
// const handleAlgorithmChange = (algorithm: string) => {
//     currentAlgorithm.value = algorithmList.value[algorithm]
//     // 初始化参数为默认值
//     algorithmParams.value = {}
//     if (currentAlgorithm.value) {
//         Object.entries(currentAlgorithm.value.parameters).forEach(([key, param]) => {
//             algorithmParams.value[key] = param.default
//         })
//     }
// }

// 格式化模型选项标签
const formatModelLabel = (model: ClassificationModel) => {
    let label = model.modelName
    if (model.accuracy !== null && model.accuracy !== undefined) {
        label += ` (精度: ${(model.accuracy * 100).toFixed(2)}%)`
    }
    if (model.isDefault) {
        label += ' [默认]'
    }
    return label
}

// 提交表单
const handleSubmit = async () => {
    // 校验必填项
    if (!form.value.imageId) {
        ElMessage.warning('请选择影像')
        return
    }
    if (!form.value.modelId) {
        ElMessage.warning('请选择模型')
        return
    }
    if (!form.value.name.trim()) {
        ElMessage.warning('请输入任务名称')
        return
    }

    try {
        // // 设置算法参数
        // form.value.parameters = JSON.stringify(algorithmParams.value)
        await createTask(form.value)
        ElMessage.success('创建成功')
        // 重置表单
        form.value = {
            imageId: undefined,
            modelId: undefined,
            name: '',
            description: '',
            // algorithm: '',
            // parameters: '{}'
        }
        // algorithmParams.value = {}
        // currentAlgorithm.value = undefined
    } catch (error: any) {
        ElMessage.error(error.message || '创建失败')
    }
}

onMounted(() => {
    getImages()
    getModels() // 获取模型列表
    // getAlgorithmList()
})
</script>

<template>
    <div class="app-container">
        <el-card>
            <el-form :model="form" label-width="100px">
                <el-form-item label="影像选择" required>
                    <el-select v-model="form.imageId" placeholder="请选择影像" filterable>
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

                <el-form-item label="模型选择" required>
                    <el-select v-model="form.modelId" placeholder="请选择模型" filterable>
                        <el-option
                            v-for="model in modelList"
                            :key="model.id"
                            :label="formatModelLabel(model)" 
                            :value="model.id"
                        />
                    </el-select>
                </el-form-item>

                <!-- 移除算法选择和参数 -->
                <!-- <el-form-item label="算法选择" required>
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
                </el-form-item> -->

                <!-- 算法参数 -->
                <!-- <template v-if="currentAlgorithm">
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
                </template> -->

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
.el-select {
    width: 100%; /* 让下拉框宽度适应容器 */
}
</style>