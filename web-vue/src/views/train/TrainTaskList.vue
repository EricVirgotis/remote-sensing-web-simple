<template>
  <div class="train-task-list">
    <!-- 操作栏 -->
    <div class="operation-bar">
      <el-form :inline="true" :model="queryForm">
        <el-form-item label="任务名称">
          <el-input v-model="queryForm.name" placeholder="请输入任务名称" clearable @keyup.enter="handleQuery" />
        </el-form-item>
        <el-form-item label="任务状态">
          <el-select v-model="queryForm.status" placeholder="请选择任务状态" clearable style="width: 220px">
            <el-option label="全部" :value="''" />
            <el-option label="训练中" :value="0" />
            <el-option label="训练成功" :value="1" />
            <el-option label="训练失败" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="模型选择">
          <el-select v-model="queryForm.model_name" placeholder="请选择模型" clearable style="width: 220px">
            <el-option label="LeNet-5" value="LeNet-5" />
            <el-option label="AlexNet" value="AlexNet" />
            <el-option label="VGGNet-16" value="VGGNet-16" />
            <el-option label="GoogleNet" value="GoogleNet" />
            <el-option label="ResNet50" value="ResNet50" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button type="success" @click="handleAdd">新建</el-button>
          <el-button @click="handleRefresh">刷新</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 训练任务表格 -->
    <el-table v-loading="loading" :data="tableData" border style="width: 100%">
      <el-table-column prop="taskName" label="任务名称" min-width="120" show-overflow-tooltip />
      <el-table-column prop="modelName" label="模型名称" min-width="120" show-overflow-tooltip />
      <el-table-column prop="epochs" label="训练轮数" width="100" />
      <el-table-column prop="batchSize" label="批次大小" width="100" />
      <el-table-column prop="learningRate" label="学习率" width="100" />
      <el-table-column prop="accuracy" label="准确率" width="100">
        <template #default="{ row }">
          <span>{{ row.accuracy ? (row.accuracy * 100).toFixed(2) + '%' : '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="loss" label="损失值" width="100">
        <template #default="{ row }">
          <span>{{ row.loss ? row.loss.toFixed(4) : '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 0 ? 'warning' : row.status === 1 ? 'success' : 'danger'">
            {{ row.status === 0 ? '训练中' : row.status === 1 ? '训练成功' : '训练失败' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="createTime" label="创建时间" width="180" show-overflow-tooltip>
        <template #default="{ row }">
          {{ formatDateTime(row.createTime) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button
            v-if="row.status !== 0"
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
        v-model:current-page="queryForm.current"
        v-model:page-size="queryForm.size"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 新建训练任务对话框 -->
    <el-dialog v-model="dialogVisible" title="新建训练任务" width="500px" @close="handleDialogClose">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="模型选择" prop="modelName">
          <el-select v-model="form.modelName" placeholder="请选择模型" style="width: 100%" @change="handleModelChange">
            <el-option label="LeNet-5" value="LeNet-5" />
            <el-option label="AlexNet" value="AlexNet" />
            <el-option label="VGGNet-16" value="VGGNet-16" />
            <el-option label="GoogleNet" value="GoogleNet" />
            <el-option label="ResNet50" value="ResNet50" />
          </el-select>
          <div style="margin-top: 10px;">
            <el-checkbox v-model="form.usePretrained" :disabled="form.modelName === 'LeNet-5' || form.modelName === 'AlexNet'">使用预训练权重</el-checkbox>
            <el-tooltip v-if="form.modelName === 'LeNet-5' || form.modelName === 'AlexNet'" content="该模型没有官方预训练权重可用" placement="top">
              <el-icon style="margin-left: 5px;"><QuestionFilled /></el-icon>
            </el-tooltip>
          </div>
        </el-form-item>
        
        <el-form-item label="数据集" prop="datasetId">
          <el-select v-model="form.datasetId" placeholder="请选择数据集" style="width: 100%">
            <el-option
              v-for="item in datasetOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="训练轮数" prop="epochs">
          <el-input-number v-model="form.epochs" :min="1" :max="1000" />
        </el-form-item>
        <el-form-item label="批次大小" prop="batchSize">
          <el-input-number v-model="form.batchSize" :min="1" :max="1000" />
        </el-form-item>
        <el-form-item label="学习率" prop="learningRate">
          <el-input-number v-model="form.learningRate" :min="0.0001" :max="1" :step="0.0001" :precision="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { formatDateTime } from '@/utils/format'
import type { Dataset } from '@/types/dataset'
import type { TrainTask } from '@/types/train'
import { pageDatasets } from '@/api/dataset'
import { createTrainTask, pageTrainTasks, deleteTrainTask } from '@/api/train'

// 查询表单
const queryForm = reactive({
  current: 1,
  size: 10,
  name: '',
  status: undefined as number | undefined,
  model_name: ''
})

// 表格数据
const loading = ref(false)
const tableData = ref<TrainTask[]>([])
const total = ref(0)

// 对话框
const dialogVisible = ref(false)
const formRef = ref<FormInstance>()
const form = reactive({
  name: '',
  datasetId: undefined as number | undefined,
  modelName: 'ResNet50',
  usePretrained: true,
  epochs: 10,
  batchSize: 32,
  learningRate: 0.001
})

// 数据集选项
const datasetOptions = ref<Dataset[]>([])

// 处理模型选择变化
const handleModelChange = (value: string) => {
  if (value === 'LeNet-5' || value === 'AlexNet') {
    form.usePretrained = false
  }
}

// 表单校验规则
const rules: FormRules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  datasetId: [{ required: true, message: '请选择数据集', trigger: 'change' }],
  modelName: [{ required: true, message: '请选择模型', trigger: 'change' }],
  epochs: [{ required: true, message: '请输入训练轮数', trigger: 'blur' }],
  batchSize: [{ required: true, message: '请输入批次大小', trigger: 'blur' }],
  learningRate: [{ required: true, message: '请输入学习率', trigger: 'blur' }]
}

// 查询训练任务列表
const handleQuery = async () => {
  loading.value = true
  try {
    const res = await pageTrainTasks(queryForm)
    // 解析parameters字段中的训练参数
    tableData.value = res.records.map(item => {
      if (item.parameters) {
        try {
          const params = JSON.parse(item.parameters)
          return {
            ...item,
            epochs: params.epochs,
            batchSize: params.batchSize,
            learningRate: params.learningRate
          }
        } catch (e) {
          console.error('解析训练参数失败:', e)
        }
      }
      return item
    })
    total.value = res.total
  } catch (error) {
    console.error('查询训练任务列表失败:', error)
    ElMessage.error('查询训练任务列表失败')
  } finally {
    loading.value = false
  }
}

// 查询数据集列表
const queryDatasetList = async () => {
  try {
    const res = await pageDatasets({
      current: 1,
      size: 1000,
      status: 1 // 只查询启用的数据集
    })
    datasetOptions.value = res.records
  } catch (error) {
    console.error('查询数据集列表失败:', error)
    ElMessage.error('查询数据集列表失败')
  }
}

// 新建训练任务
const handleAdd = () => {
  dialogVisible.value = true
  queryDatasetList()
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      if (!form.datasetId) {
        ElMessage.error('请选择数据集')
        return
      }
      try {
        await createTrainTask({
          name: form.name,
          datasetId: form.datasetId,
          modelName: form.modelName,
          usePretrained: form.usePretrained,
          epochs: form.epochs,
          batchSize: form.batchSize,
          learningRate: form.learningRate
        })
        ElMessage.success('创建训练任务成功')
        dialogVisible.value = false
        handleQuery()
      } catch (error) {
        console.error('创建训练任务失败:', error)
        ElMessage.error('创建训练任务失败')
      }
    }
  })
}

// 关闭对话框
const handleDialogClose = () => {
  if (!formRef.value) return
  formRef.value.resetFields()
}

// 刷新
const handleRefresh = async () => {
  loading.value = true
  try {
    const res = await pageTrainTasks({
      current: queryForm.current,
      size: queryForm.size,
      name: queryForm.name,
      status: queryForm.status
    })
    tableData.value = res.records
    total.value = res.total
    ElMessage.success('刷新成功')
  } catch (error: any) {
    ElMessage.error('刷新失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 分页
const handleSizeChange = () => {
  queryForm.current = 1
  handleQuery()
}

const handleCurrentChange = () => {
  handleQuery()
}

// 删除训练任务
const handleDelete = async (row: TrainTask) => {
  try {
    await ElMessageBox.confirm('确认删除该训练任务吗？', '提示', {
      type: 'warning'
    })
    await deleteTrainTask(row.id)
    ElMessage.success('删除成功')
    handleQuery()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除训练任务失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 初始化
onMounted(() => {
  handleQuery()
})
</script>

<style scoped>
.train-task-list {
  padding: 20px;
}

.operation-bar {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>