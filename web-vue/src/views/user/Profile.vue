<!-- 个人中心页面 -->
<template>
  <div class="profile">
    <el-row :gutter="20">
      <!-- 个人信息卡片 -->
      <el-col :span="8">
        <el-card class="profile-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="header-title">个人信息</span>
              <el-button
                type="primary"
                link
                @click="handleEdit"
              >
                <el-icon><Edit /></el-icon>
                编辑资料
              </el-button>
            </div>
          </template>
          <div class="profile-info">
            <div class="avatar-wrapper">
              <el-avatar
                :size="100"
                :src="userInfo?.avatar"
              />
              <el-upload
                class="avatar-uploader"
                :auto-upload="false"
                :show-file-list="false"
                :on-change="handleAvatarChange"
                :before-upload="beforeAvatarUpload"
              >
                <el-button
                  type="primary"
                  link
                  class="change-avatar"
                >
                  <el-icon><Camera /></el-icon>
                  更换头像
                </el-button>
              </el-upload>
            </div>
            <div class="info-list">
              <div class="info-item">
                <span class="label">用户名：</span>
                <span class="value">{{ userInfo?.username }}</span>
              </div>
              <div class="info-item">
                <span class="label">真实姓名：</span>
                <span class="value">{{ userInfo?.realName }}</span>
              </div>
              <div class="info-item">
                <span class="label">手机号：</span>
                <span class="value">{{ userInfo?.phone }}</span>
              </div>
              <div class="info-item">
                <span class="label">邮箱：</span>
                <span class="value">{{ userInfo?.email }}</span>
              </div>
              <div class="info-item">
                <span class="label">角色：</span>
                <el-tag :type="userInfo?.role === 1 ? 'danger' : 'info'" size="small">
                  {{ userInfo?.role === 1 ? '管理员' : '普通用户' }}
                </el-tag>
              </div>
              <div class="info-item">
                <span class="label">状态：</span>
                <el-tag :type="userInfo?.status === 1 ? 'success' : 'danger'" size="small">
                  {{ userInfo?.status === 1 ? '正常' : '禁用' }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 修改密码卡片 -->
      <el-col :span="8">
        <el-card class="password-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="header-title">修改密码</span>
              <el-icon><Lock /></el-icon>
            </div>
          </template>
          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-width="100px"
            status-icon
          >
            <el-form-item label="原密码" prop="oldPassword">
              <el-input
                v-model="passwordForm.oldPassword"
                type="password"
                show-password
                placeholder="请输入原密码"
              />
            </el-form-item>
            <el-form-item label="新密码" prop="newPassword">
              <el-input
                v-model="passwordForm.newPassword"
                type="password"
                show-password
                placeholder="请输入新密码"
              />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input
                v-model="passwordForm.confirmPassword"
                type="password"
                show-password
                placeholder="请确认新密码"
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                :loading="passwordLoading"
                @click="handleChangePassword"
              >
                <el-icon><Check /></el-icon>
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <!-- 编辑个人信息对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑个人信息"
      width="500px"
      destroy-on-close
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editRules"
        label-width="100px"
        status-icon
      >
        <el-form-item label="真实姓名" prop="realName">
          <el-input
            v-model="editForm.realName"
            placeholder="请输入真实姓名"
          />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input
            v-model="editForm.phone"
            placeholder="请输入手机号"
          />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="editForm.email"
            placeholder="请输入邮箱"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="editLoading"
            @click="handleSaveEdit"
          >
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { FormInstance, UploadProps, FormItemRule } from 'element-plus'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { updateUser } from '@/api/user'
import { fileRequest } from '@/api/file_request'
import type { UpdateUserParams } from '@/types/user'
import { Edit, Camera, Lock, Check } from '@element-plus/icons-vue'

const userStore = useUserStore()

// 用户信息
const userInfo = computed(() => userStore.userInfo)

// 修改密码表单
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 修改密码表单校验规则
const validatePass2 = (rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== passwordForm.value.newPassword) {
    callback(new Error('两次输入密码不一致!'))
  } else {
    callback()
  }
}

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入原密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应在6-20个字符之间', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应在6-20个字符之间', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validatePass2, trigger: 'blur' }
  ]
}

const passwordLoading = ref(false)
const passwordFormRef = ref<FormInstance>()

// 处理修改密码
const handleChangePassword = async () => {
  if (!passwordFormRef.value) return

  try {
    await passwordFormRef.value.validate()
    passwordLoading.value = true

    await userStore.changePassword({
      id: userInfo.value?.id as number,
      oldPassword: passwordForm.value.oldPassword,
      newPassword: passwordForm.value.newPassword
    })

    ElMessage.success('密码修改成功')
    passwordForm.value = {
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    }
  } catch (error) {
    console.error('修改密码失败:', error)
  } finally {
    passwordLoading.value = false
  }
}

// 编辑表单
const editForm = ref({
  realName: '',
  phone: '',
  email: ''
})

// 编辑表单校验规则
const editRules = {
  realName: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '真实姓名长度应在2-20个字符之间', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/, message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
} satisfies Record<string, FormItemRule[]>

const editDialogVisible = ref(false)
const editLoading = ref(false)
const editFormRef = ref<FormInstance>()

// 处理编辑
const handleEdit = () => {
  editForm.value = {
    realName: userInfo.value?.realName || '',
    phone: userInfo.value?.phone || '',
    email: userInfo.value?.email || ''
  }
  editDialogVisible.value = true
}

// 处理保存编辑
const handleSaveEdit = async () => {
  if (!editFormRef.value) return

  // 确保用户ID存在
  console.log('当前用户信息:', JSON.stringify(userInfo.value, null, 2))
  if (!userInfo.value?.id) {
    // 尝试重新初始化用户信息
    try {
      await userStore.initUserInfo()
      console.log('重新初始化后的用户信息:', JSON.stringify(userInfo.value, null, 2))
      if (!userInfo.value?.id) {
        ElMessage.error('用户信息不完整，请重新登录后重试')
        return
      }
    } catch (error) {
      console.error('初始化用户信息失败:', error)
      ElMessage.error('用户信息不完整，请重新登录后重试')
      return
    }
  }

  try {
    await editFormRef.value.validate()
    editLoading.value = true

    await updateUser({
      id: userInfo.value.id,
      realName: editForm.value.realName,
      phone: editForm.value.phone,
      email: editForm.value.email,
      role: userInfo.value.role,
      status: userInfo.value.status
    })

    // 更新本地用户信息
    const storedUserInfo = localStorage.getItem('userInfo')
    if (storedUserInfo) {
      try {
        const data = JSON.parse(storedUserInfo)
        if (data && data.userInfo && userInfo.value) {
          data.userInfo = {
            ...data.userInfo,
            realName: editForm.value.realName,
            phone: editForm.value.phone,
            email: editForm.value.email
          }
          localStorage.setItem('userInfo', JSON.stringify(data))
          userStore.initUserInfo()
        } else {
          throw new Error('用户信息不完整')
        }
      } catch (error) {
        console.error('更新用户信息失败:', error)
        ElMessage.error('更新用户信息失败，请重新登录后重试')
        userStore.logout()
        return
      }
    }

    ElMessage.success('个人信息修改成功')
    editDialogVisible.value = false
  } catch (error) {
    console.error('修改个人信息失败:', error)
    ElMessage.error('修改个人信息失败，请稍后重试')
  } finally {
    editLoading.value = false
  }
}

// 处理头像上传前的验证
const beforeAvatarUpload: UploadProps['beforeUpload'] = (file) => {
  const isJPG = file.type === 'image/jpeg'
  const isPNG = file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isJPG && !isPNG) {
    ElMessage.error('头像只能是 JPG 或 PNG 格式!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('头像大小不能超过 2MB!')
    return false
  }
  return true
}

// 处理头像文件改变
const handleAvatarChange: UploadProps['onChange'] = async (uploadFile) => {
  if (!uploadFile.raw) return
  
  try {
    // 上传文件到文件服务
    let retryCount = 0;
    const maxRetries = 3;
    let lastError;
    let url = '';

    while (retryCount < maxRetries) {
      try {
        const uploadResult = await fileRequest.upload('avatars', uploadFile.raw);
        url = uploadResult.url;
        const { bucket, objectKey } = uploadResult;
        
        // 确保URL格式正确
        if (!url || typeof url !== 'string') {
          throw new Error('文件服务返回的URL格式不正确')
        }

        // 上传成功，跳出重试循环
        lastError = null;
        return { url, bucket, objectKey };
      } catch (error) {
        lastError = error;
        retryCount++;
        if (retryCount < maxRetries) {
          console.warn(`头像上传失败，正在进行第${retryCount}次重试...`);
          await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
        }
      }
    }

    // 如果所有重试都失败，抛出最后一个错误
    if (lastError) {
      console.error('头像上传失败，已达到最大重试次数:', lastError);
      throw lastError;
    }
    
    // 更新用户头像
    const updateParams: UpdateUserParams = {
      id: userInfo.value?.id as number,
      avatar: url
    }
    
    try {
      await updateUser(updateParams)
      
      // 更新本地用户信息
      const storedUserInfo = localStorage.getItem('userInfo')
      if (storedUserInfo) {
        const data = JSON.parse(storedUserInfo)
        data.userInfo.avatar = url
        localStorage.setItem('userInfo', JSON.stringify(data))
        // 强制刷新用户信息
        userStore.initUserInfo()
        // 不再直接修改computed属性
      }
      
      ElMessage.success('头像更新成功')
    } catch (updateError: any) {
      console.error('更新用户头像失败:', updateError)
      const errorMsg = updateError.response?.data?.msg || updateError.message || '更新用户头像失败'
      ElMessage.error(errorMsg)
      throw updateError // 重新抛出错误，进入外层catch块
    }
  } catch (error: any) {
    console.error('头像上传或更新失败:', error)
    const errorMessage = error.response?.data?.msg || error.message || '头像上传失败'
    ElMessage.error(errorMessage)
    
    // 如果上传失败，使用默认头像
    const defaultAvatarUrl = `${import.meta.env.VITE_FILE_URL}/file/avatars/default_avatar.svg`
    
    // 先检查默认头像是否可访问
    try {
      const checkResponse = await fetch(defaultAvatarUrl, { method: 'HEAD' })
      if (!checkResponse.ok) {
        console.error('默认头像不可访问:', defaultAvatarUrl)
        return
      }
      
      // 确保用户ID存在
      if (!userInfo.value || typeof userInfo.value.id !== 'number') {
        console.error('用户信息不完整，无法更新头像')
        ElMessage.error('用户信息不完整，请重新登录后重试')
        return
      }
      
      const updateParams: UpdateUserParams = {
        id: userInfo.value.id,
        avatar: defaultAvatarUrl
      }
      
      await updateUser(updateParams)
      
      // 更新本地用户信息
      const storedUserInfo = localStorage.getItem('userInfo')
      if (storedUserInfo) {
        try {
          const data = JSON.parse(storedUserInfo)
          if (data && data.userInfo) {
            data.userInfo.avatar = defaultAvatarUrl
            localStorage.setItem('userInfo', JSON.stringify(data))
            userStore.initUserInfo()
          }
        } catch (parseError) {
          console.error('解析用户信息失败:', parseError)
        }
      }
      
      ElMessage.warning('已使用默认头像')
    } catch (err) {
      console.error('设置默认头像失败:', err)
      ElMessage.error('设置默认头像失败，请稍后重试')
    }
  }
}
</script>

<style scoped>
.profile {
  padding: 20px;
  min-height: calc(100vh - 140px);
  background-color: #f5f7fa;
}

.profile-card,
.password-card {
  height: 100%;
  transition: all 0.3s;
}

.profile-card:hover,
.password-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  font-size: 16px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 8px;
}

.profile-info {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.avatar-wrapper {
  position: relative;
  margin-bottom: 30px;
  text-align: center;
}

.change-avatar {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.info-list {
  width: 100%;
}

.info-item {
  display: flex;
  margin-bottom: 20px;
  padding: 0 20px;
  line-height: 24px;
}

.info-item .label {
  width: 80px;
  color: #606266;
  font-weight: 500;
}

.info-item .value {
  color: #303133;
  flex: 1;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.el-form-item__content) {
  flex-wrap: nowrap;
}

:deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #dcdfe6 inset;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #409eff inset;
}

:deep(.el-form--label-top .el-form-item__label) {
  margin-bottom: 8px;
}

:deep(.el-button--primary) {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}
</style>