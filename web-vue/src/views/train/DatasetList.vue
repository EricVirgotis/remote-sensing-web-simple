<template>
  <div class="dataset-list">
    <!-- 操作栏 -->
    <div class="operation-bar">
      <el-input
        v-model="queryParams.name"
        placeholder="请输入数据集名称"
        clearable
        style="width: 200px"
        @keyup.enter="handleQuery"
      />
      <el-select
        v-model="queryParams.status"
        placeholder="请选择状态"
        clearable
        style="width: 200px; margin-left: 10px"
        @change="handleQuery"
      >
        <el-option
          v-for="item in statusOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
      <el-button
        type="primary"
        :icon="Plus"
        style="margin-left: 10px"
        @click="handleAdd"
      >
        新建数据集
      </el-button>
      <el-button
        :icon="Refresh"
        style="margin-left: 10px"
        @click="handleQuery"
      >
        刷新
      </el-button>
    </div>
    
    <!-- 数据集列表 -->
    <el-table
      v-loading="loading"
      :data="datasetList"
      style="width: 100%; margin-top: 20px"
    >
      <el-table-column prop="name" label="数据集名称" min-width="150" />
      <el-table-column prop="description" label="描述" min-width="200" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'">
            {{ row.status === 1 ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="createTime" label="创建时间" width="180" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button
            link
            type="primary"
            @click="handleDownload(row)"
          >
            下载
          </el-button>
          <el-button
            link
            type="danger"
            @click="handleDelete(row)"
          >
            删除
          </el-button>
          <el-button
            link
            type="primary"
            @click="handleEdit(row)"
          >
            编辑
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <el-pagination
      v-model:current-page="queryParams.current"
      v-model:page-size="queryParams.size"
      :total="total"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      style="margin-top: 20px; justify-content: flex-end"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
    
    <!-- 新建数据集对话框 -->
    <el-dialog
      v-model="dialog.visible"
      :title="dialog.title"
      width="500px"
      append-to-body
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="数据集名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入数据集名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            placeholder="请输入数据集描述"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status" v-if="dialog.type === 'edit'">
          <el-select v-model="form.status" placeholder="请选择状态">
            <el-option
              v-for="item in statusOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="数据集文件" prop="file" v-if="dialog.type === 'add'">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            accept=".zip"
            :on-change="handleFileChange"
            :before-upload="handleBeforeUpload"
          >
            <template #trigger>
              <el-button type="primary">选择文件</el-button>
            </template>
            <template #tip>
              <div class="el-upload__tip">
                请上传zip格式的数据集文件，文件大小不超过1GB
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleCancel">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, Refresh } from '@element-plus/icons-vue'
import type { FormInstance, FormRules, UploadInstance, UploadFile, UploadFiles } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createDataset, pageDatasets, deleteDataset, downloadDataset, updateDataset } from '@/api/dataset'
import type { Dataset } from '@/types/dataset'

// 状态选项
const statusOptions = [
  { label: '启用', value: 1 },
  { label: '禁用', value: 0 }
]

// 查询参数
const queryParams = ref({
  current: 1,
  size: 10,
  name: '',
  status: undefined as number | undefined
})

// 加载状态
const loading = ref(false)

// 数据集列表
const datasetList = ref<Dataset[]>([])

// 总记录数
const total = ref(0)

// 对话框
const dialog = ref({
  visible: false,
  title: '新建数据集',
  type: 'add' as 'add' | 'edit'
})

// 表单
const formRef = ref<FormInstance>()
const uploadRef = ref<UploadInstance>()
const form = ref({
  id: undefined as number | undefined,
  name: '',
  description: '',
  file: null as File | null,
  status: 1 as number
})

// 表单校验规则
const rules = ref<FormRules>({
  name: [
    { required: true, message: '请输入数据集名称', trigger: 'blur' }
  ],
  file: [
    { required: true, message: '请选择数据集文件', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
})

// 查询列表
const getList = async () => {
  loading.value = true
  try {
    const { records, total: totalCount } = await pageDatasets(queryParams.value)
    datasetList.value = records
    total.value = totalCount
  } catch (error) {
    console.error('获取数据集列表失败：', error)
    ElMessage.error('获取数据集列表失败')
  } finally {
    loading.value = false
  }
}

// 查询按钮
const handleQuery = () => {
  queryParams.value.current = 1
  getList()
}

// 每页条数改变
const handleSizeChange = (val: number) => {
  queryParams.value.size = val
  getList()
}

// 当前页改变
const handleCurrentChange = (val: number) => {
  queryParams.value.current = val
  getList()
}

// 新建按钮
const handleAdd = () => {
  dialog.value.visible = true
  dialog.value.title = '新建数据集'
  dialog.value.type = 'add'
  form.value = {
    id: undefined,
    name: '',
    description: '',
    file: null,
    status: 1
  }
}

// 文件改变
const handleFileChange = (uploadFile: UploadFile, uploadFiles: UploadFiles) => {
  if (uploadFile.raw) {
    form.value.file = uploadFile.raw
  }
}

// 取消按钮
const handleCancel = () => {
  dialog.value.visible = false
  formRef.value?.resetFields()
  uploadRef.value?.clearFiles()
}

// 文件上传前的验证
const handleBeforeUpload = (file: File) => {
  const isZip = file.type === 'application/zip' || file.name.endsWith('.zip')
  const isLt1GB = file.size / 1024 / 1024 / 1024 < 1

  if (!isZip) {
    ElMessage.error('只能上传zip格式的文件！')
    return false
  }
  if (!isLt1GB) {
    ElMessage.error('文件大小不能超过1GB！')
    return false
  }
  return true
}

// 提交按钮
const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (dialog.value.type === 'add') {
          // 创建数据集
          const formData = new FormData()
          const datasetInfo = {
            name: form.value.name,
            description: form.value.description
          }
          formData.append('dataset', new Blob([JSON.stringify(datasetInfo)], { type: 'application/json' }))
          if (form.value.file) {
            formData.append('file', form.value.file)
          }
          await createDataset(formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          })
          ElMessage.success('创建成功')
        } else {
          // 更新数据集
          await updateDataset(form.value.id!, {
            name: form.value.name,
            description: form.value.description,
            status: form.value.status
          })
          ElMessage.success('更新成功')
        }
        dialog.value.visible = false
        formRef.value?.resetFields()
        uploadRef.value?.clearFiles()
        getList()
      } catch (error: any) {
        console.error(dialog.value.type === 'add' ? '创建数据集失败：' : '更新数据集失败：', error)
        const errorMessage = error.response?.data?.msg || (dialog.value.type === 'add' ? '创建数据集失败' : '更新数据集失败')
        ElMessage.error(errorMessage)
      }
    }
  })
}

// 删除按钮
const handleDelete = async (row: Dataset) => {
  try {
    await ElMessageBox.confirm('确认删除该数据集吗？', '提示', {
      type: 'warning'
    })
    await deleteDataset(row.id)
    ElMessage.success('删除成功')
    getList()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除数据集失败：', error)
      ElMessage.error('删除数据集失败')
    }
  }
}

// 下载按钮
const handleDownload = async (row: Dataset) => {
  try {
    const response = await downloadDataset(row.id)
    
    // 检查响应是否为错误信息
    if (response instanceof Blob && response.type === 'application/json') {
      // 如果是JSON格式的错误信息，读取并显示
      const text = await response.text()
      const error = JSON.parse(text)
      ElMessage.error(error.msg || '下载失败')
      return
    }
    
    // 从对象键中提取文件名
    const fileName = row.objectKey.substring(row.objectKey.lastIndexOf('/') + 1)
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', fileName)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('下载数据集失败：', error)
    ElMessage.error('下载数据集失败')
  }
}

// 编辑按钮
const handleEdit = (row: Dataset) => {
  dialog.value.visible = true
  dialog.value.title = '编辑数据集'
  dialog.value.type = 'edit'
  form.value = {
    id: row.id,
    name: row.name,
    description: row.description || '',
    file: null,
    status: row.status
  }
}

// 组件挂载时查询列表
onMounted(() => {
  getList()
})
</script>

<style scoped>
.dataset-list {
  padding: 20px;
}

.operation-bar {
  display: flex;
  align-items: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}
</style>