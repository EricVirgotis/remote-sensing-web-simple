<!-- 遥感影像上传页面 -->
<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { UploadProps, UploadInstance } from 'element-plus'
import { uploadImageFile, uploadImage } from '@/api/image'
import type { ImageUploadParams } from '@/types/image'

// 上传参数
const uploadParams = ref<ImageUploadParams>({
    name: '',
    description: '',
    bucketName: 'images',
    objectKey: '',
    size: 0,
    format: '',
    width: 0,
    height: 0,
    bands: 0
})

// 上传组件实例
const upload = ref<UploadInstance>()

// 获取图片尺寸
const getImageDimensions = (file: File): Promise<{ width: number; height: number }> => {
    return new Promise((resolve, reject) => {
        if (file.type === 'image/tiff') {
            // TODO: TIFF格式需要特殊处理，暂时提示用户手动输入
            ElMessage.warning('TIFF格式暂不支持自动获取尺寸，请手动输入')
            resolve({ width: 0, height: 0 })
            return
        }

        const img = new Image()
        img.onload = () => {
            resolve({
                width: img.width,
                height: img.height
            })
        }
        img.onerror = () => {
            reject(new Error('获取图片尺寸失败'))
        }
        img.src = URL.createObjectURL(file)
    })
}

// 文件上传前的处理
const beforeUpload: UploadProps['beforeUpload'] = async (file) => {
    // 检查文件类型
    const isValidFormat = ['image/tiff', 'image/jpeg', 'image/png'].includes(file.type)
    if (!isValidFormat) {
        ElMessage.error('只能上传TIFF、JPEG、PNG格式的图片！')
        return false
    }

    // 检查文件大小
    const isLt2G = file.size / 1024 / 1024 / 1024 < 2
    if (!isLt2G) {
        ElMessage.error('图片大小不能超过2GB！')
        return false
    }

    // 设置上传参数
    uploadParams.value.name = file.name
    uploadParams.value.size = file.size
    uploadParams.value.format = file.type.split('/')[1]  // 从MIME类型中提取格式

    // 获取图片尺寸
    try {
        const { width, height } = await getImageDimensions(file)
        uploadParams.value.width = width
        uploadParams.value.height = height
        
        // 对于JPG和PNG格式，默认设置为3个波段（RGB）
        if (file.type !== 'image/tiff') {
            uploadParams.value.bands = 3
        }
    } catch (error) {
        ElMessage.warning('获取图片尺寸失败，请手动输入')
    }

    return true
}

// 自定义上传
const customUpload: UploadProps['httpRequest'] = async (options) => {
    try {
        // 检查必填字段
        if (!uploadParams.value.name) {
            ElMessage.error('请输入影像名称')
            return
        }
        if (!uploadParams.value.width) {
            ElMessage.error('请输入影像宽度')
            return
        }
        if (!uploadParams.value.height) {
            ElMessage.error('请输入影像高度')
            return
        }
        if (!uploadParams.value.bands) {
            ElMessage.error('请输入波段数')
            return
        }

        // 上传文件到对象存储
        const res = await uploadImageFile(options.file as File)
        
        // 更新上传参数中的文件信息
        const params = {
            ...uploadParams.value,
            bucketName: res.bucket,
            objectKey: res.objectKey
        }
        
        // 上传影像信息到后端
        const image = await uploadImage(params)
        
        ElMessage.success('上传成功')
        
        // 清空表单
        uploadParams.value = {
            name: '',
            description: '',
            bucketName: 'images',
            objectKey: '',
            size: 0,
            format: '',
            width: 0,
            height: 0,
            bands: 0
        }
        upload.value?.clearFiles()
        
    } catch (error: any) {
        ElMessage.error(error.message || '上传失败')
    }
}
</script>

<template>
    <div class="app-container">
        <div class="page-header">
            <h2 class="page-title">遥感影像上传</h2>
            <p class="page-description">上传您的遥感影像文件，支持TIFF、JPEG、PNG等格式</p>
        </div>
        
        <el-card class="upload-card">
            <el-form :model="uploadParams" label-width="120px">
                <el-form-item label="影像文件">
                    <el-upload
                        ref="upload"
                        class="upload-demo"
                        drag
                        action=""
                        :auto-upload="true"
                        :show-file-list="true"
                        :before-upload="beforeUpload"
                        :http-request="customUpload"
                        accept=".tif,.tiff,.jpg,.jpeg,.png"
                    >
                        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                        <div class="el-upload__text">
                            将文件拖到此处，或<em>点击上传</em>
                        </div>
                        <template #tip>
                            <div class="el-upload__tip">
                                支持上传TIFF、JPEG、PNG格式的图片，且大小不超过2GB
                            </div>
                        </template>
                    </el-upload>
                </el-form-item>
                
                <el-form-item label="影像名称">
                    <el-input v-model="uploadParams.name" placeholder="请输入影像名称" />
                </el-form-item>
                
                <el-form-item label="影像描述">
                    <el-input
                        v-model="uploadParams.description"
                        type="textarea"
                        placeholder="请输入影像描述"
                    />
                </el-form-item>
                
                <el-form-item label="影像宽度">
                    <el-input-number v-model="uploadParams.width" :min="0" />
                </el-form-item>
                
                <el-form-item label="影像高度">
                    <el-input-number v-model="uploadParams.height" :min="0" />
                </el-form-item>
                
                <el-form-item label="波段数">
                    <el-input-number v-model="uploadParams.bands" :min="0" />
                </el-form-item>
                
                <el-form-item>
                    <el-button type="primary" size="large" @click="customUpload({file: uploadParams.file})">
                        <el-icon><Upload /></el-icon> 提交上传
                    </el-button>
                    <el-button size="large" @click="resetForm">
                        <el-icon><RefreshLeft /></el-icon> 重置表单
                    </el-button>
                </el-form-item>
            </el-form>
        </el-card>
    </div>
</template>

<style lang="scss" scoped>
.app-container {
    padding: 24px;
}

.page-header {
    margin-bottom: 24px;
}

.page-title {
    font-size: 24px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 8px;
}

.page-description {
    font-size: 14px;
    color: var(--text-secondary);
}

.upload-card {
    margin-bottom: 24px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    
    :deep(.el-card__body) {
        padding: 24px;
    }
}

.upload-demo {
    width: 100%;
    
    :deep(.el-upload-dragger) {
        width: 100%;
        height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border: 2px dashed var(--border-color);
        border-radius: 8px;
        background-color: var(--background-light);
        transition: all 0.3s;
        
        &:hover {
            border-color: var(--primary-color);
            background-color: rgba(24, 144, 255, 0.05);
        }
        
        .el-icon--upload {
            font-size: 48px;
            color: var(--primary-color);
            margin-bottom: 16px;
        }
        
        .el-upload__text {
            font-size: 16px;
            color: var(--text-secondary);
            
            em {
                color: var(--primary-color);
                font-style: normal;
                text-decoration: underline;
                cursor: pointer;
            }
        }
    }
    
    :deep(.el-upload__tip) {
        font-size: 14px;
        color: var(--text-secondary);
        margin-top: 12px;
        text-align: center;
    }
}

:deep(.el-form-item__label) {
    font-weight: 500;
}

:deep(.el-input), :deep(.el-textarea), :deep(.el-input-number) {
    width: 100%;
    max-width: 500px;
}

:deep(.el-textarea__inner) {
    min-height: 100px;
}
</style>