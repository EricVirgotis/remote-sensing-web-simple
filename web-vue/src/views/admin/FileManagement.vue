<!-- 成果文件管理页面 -->
<template>
  <div class="file-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>成果文件管理</span>
          <div>
            <el-button type="primary" @click="refreshFileList">刷新</el-button>
          </div>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form :model="searchForm" inline class="search-form">
        <el-form-item label="文件名">
          <el-input
            v-model="searchForm.fileName"
            placeholder="请输入文件名"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="文件类型">
          <el-select v-model="searchForm.fileType" placeholder="请选择文件类型" clearable>
            <el-option
              v-for="item in fileTypeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="创建时间">
          <el-date-picker
            v-model="searchForm.timeRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 文件表格 -->
      <el-table v-loading="loading" :data="tableData" style="width: 100%">
        <el-table-column prop="fileName" label="文件名" min-width="180" show-overflow-tooltip />
        <el-table-column prop="fileType" label="文件类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getFileTypeTag(row.fileType)">
              {{ getFileTypeName(row.fileType) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="fileSize" label="文件大小" width="120">
          <template #default="{ row }">
            {{ formatFileSize(row.fileSize) }}
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="180" />
        <el-table-column prop="creator" label="创建者" width="120" />
        <el-table-column prop="downloadCount" label="下载次数" width="100" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handlePreview(row)">
              预览
            </el-button>
            <el-button type="success" link @click="handleDownload(row)">
              下载
            </el-button>
            <el-button type="danger" link @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.current"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 预览对话框 -->
    <el-dialog v-model="previewDialogVisible" title="文件预览" width="80%">
      <div v-if="currentFile" class="preview-container">
        <div class="file-info">
          <h3>{{ currentFile.fileName }}</h3>
          <p>类型：{{ getFileTypeName(currentFile.fileType) }}</p>
          <p>大小：{{ formatFileSize(currentFile.fileSize) }}</p>
          <p>创建时间：{{ currentFile.createTime }}</p>
          <p>创建者：{{ currentFile.creator }}</p>
        </div>
        
        <!-- 图像预览 -->
        <div v-if="isImageFile(currentFile.fileType)" class="image-preview">
          <img :src="currentFile.url" alt="图像预览" />
        </div>
        
        <!-- 其他文件类型预览 -->
        <div v-else class="other-preview">
          <el-empty description="暂不支持此类型文件的预览" />
          <div class="preview-actions">
            <el-button type="primary" @click="handleDownload(currentFile)">
              下载文件
            </el-button>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 文件类型选项
const fileTypeOptions = [
  { label: '分类结果', value: 'classification' },
  { label: '训练模型', value: 'model' },
  { label: '数据集', value: 'dataset' },
  { label: '影像文件', value: 'image' },
  { label: '其他', value: 'other' }
]

// 搜索表单
const searchForm = reactive({
  fileName: '',
  fileType: '',
  timeRange: []
})

// 分页信息
const pagination = reactive({
  current: 1,
  size: 10,
  total: 0
})

// 加载状态
const loading = ref(false)

// 表格数据
const tableData = ref([])

// 预览对话框
const previewDialogVisible = ref(false)
const currentFile = ref(null)

// 获取文件类型标签样式
const getFileTypeTag = (type) => {
  const map = {
    classification: 'success',
    model: 'primary',
    dataset: 'warning',
    image: 'info',
    other: ''
  }
  return map[type] || ''
}

// 获取文件类型名称
const getFileTypeName = (type) => {
  const map = {
    classification: '分类结果',
    model: '训练模型',
    dataset: '数据集',
    image: '影像文件',
    other: '其他'
  }
  return map[type] || '未知'
}

// 格式化文件大小
const formatFileSize = (size) => {
  if (size < 1024) {
    return size + ' B'
  } else if (size < 1024 * 1024) {
    return (size / 1024).toFixed(2) + ' KB'
  } else if (size < 1024 * 1024 * 1024) {
    return (size / (1024 * 1024)).toFixed(2) + ' MB'
  } else {
    return (size / (1024 * 1024 * 1024)).toFixed(2) + ' GB'
  }
}

// 判断是否为图像文件
const isImageFile = (type) => {
  return type === 'image' || type === 'classification'
}

// 刷新文件列表
const refreshFileList = async () => {
  loading.value = true
  try {
    // 模拟API请求
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 模拟数据
    const mockData = Array.from({ length: 20 }, (_, index) => {
      const types = ['classification', 'model', 'dataset', 'image', 'other']
      const type = types[Math.floor(Math.random() * types.length)]
      const size = Math.floor(Math.random() * 1024 * 1024 * 10) // 0-10MB
      
      return {
        id: index + 1,
        fileName: `文件_${index + 1}_${type}.${type === 'image' ? 'tif' : type === 'model' ? 'pth' : 'zip'}`,
        fileType: type,
        fileSize: size,
        createTime: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toLocaleString(),
        creator: `用户${Math.floor(Math.random() * 10) + 1}`,
        downloadCount: Math.floor(Math.random() * 100),
        url: type === 'image' ? 'https://example.com/image.jpg' : ''
      }
    })
    
    tableData.value = mockData
    pagination.value.total = 100 // 模拟总数
    
    ElMessage.success('刷新成功')
  } catch (error) {
    console.error('获取文件列表失败', error)
    ElMessage.error('获取文件列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.value.current = 1
  refreshFileList()
}

// 重置搜索
const handleReset = () => {
  searchForm.fileName = ''
  searchForm.fileType = ''
  searchForm.timeRange = []
  handleSearch()
}

// 预览文件
const handlePreview = (row) => {
  currentFile.value = row
  previewDialogVisible.value = true
}

// 下载文件
const handleDownload = (row) => {
  ElMessage.success(`开始下载文件：${row.fileName}`)
  // 实际项目中这里应该调用下载API
}

// 删除文件
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除文件