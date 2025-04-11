<!-- 登录页面 -->
<template>
  <div class="login-container">
    <div class="login-content">
      <div class="login-left">
        <div class="login-form-container">
          <div class="login-header">
            <img src="@/assets/images/logo.png" alt="Logo" class="login-logo" />
            <h2 class="login-title">遥感智能分类分析系统</h2>
            <p class="login-subtitle">基于深度学习的遥感影像智能分类分析平台</p>
          </div>
          
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            label-width="0"
            size="large"
            class="login-form"
          >
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="用户名"
                :prefix-icon="User"
                class="login-input"
              />
            </el-form-item>
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="密码"
                :prefix-icon="Lock"
                show-password
                class="login-input"
                @keyup.enter="handleLogin"
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                :loading="loading"
                class="login-button"
                @click="handleLogin"
              >
                登录
              </el-button>
            </el-form-item>
            <div class="login-options">
              <router-link to="/register" class="register-link">
                注册账号
              </router-link>
            </div>
          </el-form>
        </div>
      </div>
      
      <div class="login-right">
        <div class="login-features">
          <h3>系统功能</h3>
          <ul>
            <li>
              <el-icon><Picture /></el-icon>
              <span>遥感影像智能分类</span>
            </li>
            <li>
              <el-icon><DataAnalysis /></el-icon>
              <span>分类结果可视化</span>
            </li>
            <li>
              <el-icon><Monitor /></el-icon>
              <span>模型训练与管理</span>
            </li>
            <li>
              <el-icon><Files /></el-icon>
              <span>遥感影像管理</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
    
    <div class="login-footer">
      <p>© {{ new Date().getFullYear() }} 遥感智能分类分析系统 - 版权所有</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { FormInstance } from 'element-plus'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { useRoute, useRouter } from 'vue-router'
import { User, Lock, Picture, DataAnalysis, Monitor, Files } from '@element-plus/icons-vue'

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()

// 登录表单
const loginForm = ref({
  username: '',
  password: ''
})

// 表单校验规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应在3-20个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应在6-20个字符之间', trigger: 'blur' }
  ]
}

const loading = ref(false)
const loginFormRef = ref<FormInstance>()

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return

  try {
    await loginFormRef.value.validate()
    loading.value = true

    await userStore.login(loginForm.value.username, loginForm.value.password)
  } catch (error: any) {
    console.error('登录失败:', error)
    ElMessage.error(error.message || '登录失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-container {
  height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  position: relative;
  overflow: hidden;
}

.login-content {
  display: flex;
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  height: 100%;
}

.login-left {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.login-form-container {
  width: 100%;
  max-width: 450px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-logo {
  width: 80px;
  height: 80px;
  margin-bottom: 16px;
}

.login-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 8px;
}

.login-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.login-form {
  width: 100%;
}

.login-input {
  height: 50px;
  border-radius: 8px;
}

.login-button {
  width: 100%;
  height: 50px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  margin-top: 10px;
}

.login-options {
  margin-top: 20px;
  text-align: center;
}

.register-link {
  color: var(--primary-color);
  text-decoration: none;
  font-size: 14px;
}

.register-link:hover {
  color: var(--primary-light);
  text-decoration: underline;
}

.login-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: url('@/assets/images/login-bg.jpg') no-repeat center center;
    background-size: cover;
    opacity: 0.8;
    border-radius: 12px;
    z-index: 0;
  }
}

.login-features {
  position: relative;
  z-index: 1;
  background: rgba(255, 255, 255, 0.9);
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  
  h3 {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 20px;
    color: var(--primary-color);
    text-align: center;
  }
  
  ul {
    list-style: none;
    padding: 0;
    
    li {
      display: flex;
      align-items: center;
      margin-bottom: 20px;
      font-size: 16px;
      
      .el-icon {
        margin-right: 12px;
        font-size: 24px;
        color: var(--primary-color);
      }
    }
  }
}

.login-footer {
  text-align: center;
  padding: 20px;
  color: var(--text-secondary);
  font-size: 14px;
}

// 响应式设计
@media (max-width: 992px) {
  .login-content {
    flex-direction: column;
  }
  
  .login-left, .login-right {
    width: 100%;
    max-width: 100%;
  }
  
  .login-right {
    display: none;
  }
  
  .login-form-container {
    max-width: 100%;
  }
}
</style>