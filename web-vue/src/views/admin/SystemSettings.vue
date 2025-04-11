<!-- 系统设置页面 -->
<template>
  <div class="system-settings">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统设置</span>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <!-- 基本设置 -->
        <el-tab-pane label="基本设置" name="basic">
          <el-form
            ref="basicFormRef"
            :model="basicForm"
            :rules="basicRules"
            label-width="120px"
            class="settings-form"
          >
            <el-form-item label="系统名称" prop="systemName">
              <el-input v-model="basicForm.systemName" placeholder="请输入系统名称" />
            </el-form-item>
            <el-form-item label="系统Logo">
              <el-upload
                class="logo-uploader"
                action="#"
                :http-request="uploadLogo"
                :show-file-list="false"
                :before-upload="beforeLogoUpload"
              >
                <img v-if="basicForm.logoUrl" :src="basicForm.logoUrl" class="logo" />
                <el-icon v-else class="logo-uploader-icon"><Plus /></el-icon>
              </el-upload>
              <div class="upload-tip">建议尺寸: 200x200px, 支持 PNG, JPG 格式</div>
            </el-form-item>
            <el-form-item label="系统描述" prop="description">
              <el-input
                v-model="basicForm.description"
                type="textarea"
                :rows="3"
                placeholder="请输入系统描述"
              />
            </el-form-item>
            <el-form-item label="版权信息" prop="copyright">
              <el-input v-model="basicForm.copyright" placeholder="请输入版权信息" />
            </el-form-item>
            <el-form-item label="备案号" prop="icp">
              <el-input v-model="basicForm.icp" placeholder="请输入备案号" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveBasicSettings">保存设置</el-button>
              <el-button @click="resetBasicForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 算法服务设置 -->
        <el-tab-pane label="算法服务" name="algorithm">
          <el-form
            ref="algoFormRef"
            :model="algoForm"
            :rules="algoRules"
            label-width="120px"
            class="settings-form"
          >
            <el-form-item label="算法服务地址" prop="algoServerUrl">
              <el-input v-model="algoForm.algoServerUrl" placeholder="请输入算法服务地址" />
            </el-form-item>
            <el-form-item label="最大并发数" prop="maxConcurrent">
              <el-input-number
                v-model="algoForm.maxConcurrent"
                :min="1"
                :max="20"
                controls-position="right"
              />
            </el-form-item>
            <el-form-item label="超时时间(秒)" prop="timeout">
              <el-input-number
                v-model="algoForm.timeout"
                :min="10"
                :max="3600"
                controls-position="right"
              />
            </el-form-item>
            <el-form-item label="默认模型" prop="defaultModel">
              <el-select v-model="algoForm.defaultModel" placeholder="请选择默认模型">
                <el-option
                  v-for="item in modelOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="启用GPU加速">
              <el-switch v-model="algoForm.enableGpu" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveAlgoSettings">保存设置</el-button>
              <el-button @click="resetAlgoForm">重置</el-button>
              <el-button type="success" @click="testAlgoConnection">测试连接</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 文件存储设置 -->
        <el-tab-pane label="文件存储" name="storage">
          <el-form
            ref="storageFormRef"
            :model="storageForm"
            :rules="storageRules"
            label-width="120px"
            class="settings-form"
          >
            <el-form-item label="存储类型" prop="storageType">
              <el-radio-group v-model="storageForm.storageType">
                <el-radio label="local">本地存储</el-radio>
                <el-radio label="oss">对象存储</el-radio>
              </el-radio-group>
            </el-form-item>

            <!-- 本地存储配置 -->
            <template v-if="storageForm.storageType === 'local'">
              <el-form-item label="存储路径" prop="localPath">
                <el-input v-model="storageForm.localPath" placeholder="请输入本地存储路径" />
              </el-form-item>
              <el-form-item label="最大存储空间" prop="maxSpace">
                <el-input-number
                  v-model="storageForm.maxSpace"
                  :min="1"
                  :max="10000"
                  controls-position="right"
                />
                <span class="unit-label">GB</span>
              </el-form-item>
            </template>

            <!-- 对象存储配置 -->
            <template v-if="storageForm.storageType === 'oss'">
              <el-form-item label="服务地址" prop="ossEndpoint">
                <el-input v-model="storageForm.ossEndpoint" placeholder="请输入对象存储服务地址" />
              </el-form-item>
              <el-form-item label="存储桶名称" prop="ossBucket">
                <el-input v-model="storageForm.ossBucket" placeholder="请输入存储桶名称" />
              </el-form-item>
              <el-form-item label="AccessKey" prop="ossAccessKey">
                <el-input v-model="storageForm.ossAccessKey" placeholder="请输入AccessKey" />
              </el-form-item>
              <el-form-item label="SecretKey" prop="ossSecretKey">
                <el-input
                  v-model="storageForm.ossSecretKey"
                  type="password"
                  show-password
                  placeholder="请输入SecretKey"
                />
              </el-form-item>
            </template>

            <el-form-item label="文件服务地址" prop="fileServerUrl">
              <el-input v-model="storageForm.fileServerUrl" placeholder="请输入文件服务地址" />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="saveStorageSettings">保存设置</el-button>
              <el-button @click="resetStorageForm">重置</el-button>
              <el-button type="success" @click="testStorageConnection">测试连接</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 系统维护 -->
        <el-tab-pane label="系统维护" name="maintenance">
          <el-card class="maintenance-card">
            <template #header>
              <div class="card-header">
                <span>数据库备份</span>
              </div>
            </template>
            <div class="card-content">
              <p>定期备份数据库可以防止数据丢失，建议每天进行一次备份。</p>
              <div class="action-buttons">
                <el-button type="primary" @click="backupDatabase">立即备份</el-button>
                <el-button @click="restoreDatabase">恢复备份</el-button>
              </div>
            </div>
          </el-card>

          <el-card class="maintenance-card">
            <template #header>
              <div class="card-header">
                <span>缓存管理</span>
              </div>
            </template>
            <div class="card-content">
              <p>清除系统缓存可以释放服务器资源，但可能会导致系统短暂变慢。</p>
              <div class="action-buttons">
                <el-button type="warning" @click="clearCache">清除缓存</el-button>
              </div>
            </div>
          </el-card>

          <el-card class="maintenance-card">
            <template #header>
              <div class="card-header">
                <span>系统日志</span>
              </div>
            </template>
            <div class="card-content">
              <p>查看系统日志可以帮助排查问题和监控系统运行状态。</p>
              <div class="action-buttons">
                <el-button @click="viewSystemLogs">查看日志</el-button>
                <el-button type="danger" @click="clearLogs">清除日志</el-button>
              </div>
            </div>
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 日志查看对话框 -->
    <el-dialog v-model="logsDialogVisible" title="系统日志" width="80%">
      <div class="logs-container">
        <el-tabs v-model="activeLogTab">
          <el-tab-pane label="系统日志" name="system">
            <el-input
              v-model="systemLogs"
              type="textarea"
              :rows="20"
              readonly
              class="log-textarea"
            />
          </el-tab-pane>
          <el-tab-pane label="错误日志" name="error">
            <el-input
              v-model="errorLogs"
              type="textarea"
              :rows="20"
              readonly
              class="log-textarea"
            />
          </el-tab-pane>
          <el-tab-pane label="访问日志" name="access">
            <el-input
              v-model="accessLogs"
              type="textarea"
              :rows="20"
              readonly
              class="log-textarea"
            />
          </el-tab-pane>
        </el-tabs>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="logsDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="downloadLogs">下载日志</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

// 当前激活的标签页
const activeTab = ref('basic')

// 基本设置表单
const basicFormRef = ref()
const basicForm = reactive({
  systemName: '遥感智能分类分析系统',
  logoUrl: '',
  description: '基于深度学习的遥感影像智能分类分析系统',
  copyright: '© 2023 遥感智能分类分析系统',
  icp: '京ICP备XXXXXXXX号'
})

// 基本设置验证规则
const basicRules = {
  systemName: [
    { required: true, message: '请输入系统名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 200, message: '长度不能超过 200 个字符', trigger: 'blur' }
  ],
  copyright: [
    { required: true, message: '请输入版权信息', trigger: 'blur' }
  ]
}

// 算法服务设置表单
const algoFormRef = ref()
const algoForm = reactive({
  algoServerUrl: 'http://localhost:5000',
  maxConcurrent: 5,
  timeout: 300,
  defaultModel: 'resnet50',
  enableGpu: true
})

// 算法服务验证规则
const algoRules = {
  algoServerUrl: [
    { required: true, message: '请输入算法服务地址', trigger: 'blur' },
    { pattern: /^https?:\/\/.+/, message: '请输入有效的URL地址', trigger: 'blur' }
  ],
  maxConcurrent: [
    { required: true, message: '请输入最大并发数', trigger: 'blur' }
  ],
  timeout: [
    { required: true, message: '请输入超时时间', trigger: 'blur' }
  ],
  defaultModel: [
    { required: true, message: '请选择默认模型', trigger: 'change' }
  ]
}

// 模型选项
const modelOptions = [
  { label: 'ResNet-50', value: 'resnet50' },
  { label: 'VGG-16', value: 'vgg16' },
  { label: 'DenseNet-121', value: 'densenet121' },
  { label: 'EfficientNet-B0', value: 'efficientnet_b0' },
  { label: 'MobileNet-V2', value: 'mobilenet_v2' }
]

// 文件存储设置表单
const storageFormRef = ref()
const storageForm = reactive({
  storageType: 'local',
  localPath: '/data/files',
  maxSpace: 1000,
  ossEndpoint: 'https://oss-cn-beijing.aliyuncs.com',
  ossBucket: 'remote-sensing',
  ossAccessKey: '',
  ossSecretKey: '',
  fileServerUrl: 'http://localhost:5001'
})

// 文件存储验证规则
const storageRules = {
  storageType: [
    { required: true, message: '请选择存储类型', trigger: 'change' }
  ],
  localPath: [
    { required: true, message: '请输入本地存储路径', trigger: 'blur' }
  ],
  maxSpace: [
    { required: true, message: '请输入最大存储空间', trigger: 'blur' }
  ],
  ossEndpoint: [
    { required: true, message: '请输入对象存储服务地址', trigger: 'blur' }
  ],
  ossBucket: [
    { required: true, message: '请输入存储桶名称', trigger: 'blur' }
  ],
  ossAccessKey: [
    { required: true, message: '请输入AccessKey', trigger: 'blur' }
  ],
  ossSecretKey: [
    { required: true, message: '请输入SecretKey', trigger: 'blur' }
  ],
  fileServerUrl: [
    { required: true, message: '请输入文件服务地址', trigger: 'blur' },
    { pattern: /^https?:\/\/.+/, message: '请输入有效的URL地址', trigger: 'blur' }
  ]
}

// 日志对话框
const logsDialogVisible = ref(false)
const activeLogTab = ref('system')
const systemLogs = ref('')
const errorLogs = ref('')
const accessLogs = ref('')

// 保存基本设置
const saveBasicSettings = async () => {
  if (!basicFormRef.value) return
  
  await basicFormRef.value.validate((valid: boolean, fields: Record<string, any>) => {
    if (valid) {
      // 模拟API请求
      setTimeout(() => {
        ElMessage.success('基本设置保存成功')
      }, 500)
    } else {
      console.log('验证失败', fields)
    }
  })
}

// 重置基本设置表单
const resetBasicForm = () => {
  if (basicFormRef.value) {
    basicFormRef.value.resetFields()
  }
}

// 上传Logo前的验证
const beforeLogoUpload = (file: File) => {
  const isImage = file.type === 'image/jpeg' || file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('Logo只能是JPG或PNG格式!')
  }
  if (!isLt2M) {
    ElMessage.error('Logo大小不能超过2MB!')
  }
  return isImage && isLt2M
}

// 上传Logo
const uploadLogo = async (options: { file: File }) => {
  const { file } = options
  return new Promise((resolve) => {
    // 模拟上传
    const reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onload = () => {
      basicForm.logoUrl = reader.result as string
      ElMessage.success('Logo上传成功')
      resolve({ data: { url: basicForm.logoUrl } })
    }
  })
}

// 保存算法服务设置
const saveAlgoSettings = async () => {
  if (!algoFormRef.value) return
  
  await algoFormRef.value.validate((valid: boolean, fields: Record<string, any>) => {
    if (valid) {
      // 模拟API请求
      setTimeout(() => {
        ElMessage.success('算法服务设置保存成功')
      }, 500)
    } else {
      console.log('验证失败', fields)
    }
  })
}

// 重置算法服务表单
const resetAlgoForm = () => {
  if (algoFormRef.value) {
    algoFormRef.value.resetFields()
  }
}

// 测试算法服务连接
const testAlgoConnection = () => {
  ElMessage.info('正在测试算法服务连接...')
  // 模拟测试
  setTimeout(() => {
    ElMessage.success('算法服务连接成功')
  }, 1000)
}

// 保存文件存储设置
const saveStorageSettings = async () => {
  if (!storageFormRef.value) return
  
  await storageFormRef.value.validate((valid: boolean, fields: Record<string, any>) => {
    if (valid) {
      // 模拟API请求
      setTimeout(() => {
        ElMessage.success('文件存储设置保存成功')
      }, 500)
    } else {
      console.log('验证失败', fields)
    }
  })
}

// 重置文件存储表单
const resetStorageForm = () => {
  if (storageFormRef.value) {
    storageFormRef.value.resetFields()
  }
}

// 测试存储连接
const testStorageConnection = () => {
  ElMessage.info('正在测试存储服务连接...')
  // 模拟测试
  setTimeout(() => {
    ElMessage.success('存储服务连接成功')
  }, 1000)
}

// 数据库备份
const backupDatabase = () => {
  ElMessage.info('正在备份数据库...')
  // 模拟备份
  setTimeout(() => {
    ElMessage.success('数据库备份成功')
  }, 1500)
}

// 恢复数据库
const restoreDatabase = () => {
  ElMessageBox.confirm(
    '恢复数据库将覆盖当前数据，是否继续？',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    ElMessage.info('正在恢复数据库...')
    // 模拟恢复
    setTimeout(() => {
      ElMessage.success('数据库恢复成功')
    }, 1500)
  }).catch(() => {
    ElMessage.info('已取消操作')
  })
}

// 清除缓存
const clearCache = () => {
  ElMessageBox.confirm(
    '清除缓存可能会导致系统短暂变慢，是否继续？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(() => {
    ElMessage.info('正在清除缓存...')
    // 模拟清除
    setTimeout(() => {
      ElMessage.success('缓存清除成功')
    }, 1000)
  }).catch(() => {
    ElMessage.info('已取消操作')
  })
}

// 查看系统日志
const viewSystemLogs = () => {
  // 模拟获取日志
  systemLogs.value = generateMockLogs('系统')
  errorLogs.value = generateMockLogs('错误')
  accessLogs.value = generateMockLogs('访问')
  logsDialogVisible.value = true
}

// 生成模拟日志
const generateMockLogs = (type: '系统' | '错误' | '访问') => {
  let logs = ''
  const date = new Date()
  
  for (let i = 0; i < 50; i++) {
    const time = new Date(date.getTime() - i * 60000)
    const timeStr = time.toLocaleString()
    
    if (type === '系统') {
      logs += `[${timeStr}] [INFO] 系统服务正常运行中\n`
      if (i % 5 === 0) {
        logs += `[${timeStr}] [INFO] 用户登录成功: user${Math.floor(Math.random() * 100)}\n`
      }
      if (i % 7 === 0) {
        logs += `[${timeStr}] [INFO] 任务完成: task_${Math.floor(Math.random() * 1000)}\n`
      }
    } else if (type === '错误') {
      if (i % 10 === 0) {
        logs += `[${timeStr}] [ERROR] 数据库连接超时，已自动重连\n`
      }
      if (i % 15 === 0) {
        logs += `[${timeStr}] [ERROR] 文件上传失败: file_${Math.floor(Math.random() * 100)}.jpg\n`
      }
    } else if (type === '访问') {
      logs += `[${timeStr}] [INFO] ${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)} - GET /api/images\n`
      if (i % 3 === 0) {
        logs += `[${timeStr}] [INFO] ${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)} - POST /api/tasks\n`
      }
    }
  }
  
  return logs
}

// 清除日志
const clearLogs = () => {
  ElMessageBox.confirm(
    '确定要清除所有系统日志吗？',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    ElMessage.success('系统日志已清除')
  }).catch(() => {
    ElMessage.info('已取消操作')
  })
}

// 下载日志
const downloadLogs = () => {
  ElMessage.success('日志文件下载中...')
}

// 页面加载时获取设置
onMounted(() => {
  // 模拟获取设置
  setTimeout(() => {
    // 这里可以从API获取设置并更新表单
    console.log('设置已加载')
  }, 500)
})
</script>

<style scoped lang="scss">
.system-settings {
  padding: 20px;
}

.settings-form {
  max-width: 800px;
  margin: 20px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-uploader {
  width: 200px;
  height: 200px;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
  
  &:hover {
    border-color: #409eff;
  }
  
  .logo {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }
  
  .logo-uploader-icon {
    font-size: 28px;
    color: #8c939d;
    width: 200px;
    height: 200px;
    line-height: 200px;
    text-align: center;
  }
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.unit-label {
  margin-left: 10px;
  color: #606266;
}

.maintenance-card {
  margin-bottom: 20px;
  
  .card-content {
    padding: 10px 0;
    
    p {
      margin-bottom: 15px;
      color: #606266;
    }
    
    .action-buttons {
      display: flex;
      gap: 10px;
    }
  }
}

.logs-container {
  .log-textarea {
    font-family: monospace;
    font-size: 12px;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>