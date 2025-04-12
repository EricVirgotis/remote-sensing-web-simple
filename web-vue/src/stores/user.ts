import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { UserInfo, LoginResponse } from '@/types/user'
import { login as userLogin, logout as userLogout, updatePassword as updateUserPassword, register as userRegister } from '@/api/user'
import { ElMessage } from 'element-plus'
import router from '@/router'

export const useUserStore = defineStore('user', () => {
  // 用户信息
  const userInfo = ref<UserInfo | null>(null)
  // token
  const token = ref<string | null>(null)

  // 从localStorage中恢复用户信息
  const initUserInfo = () => {
    const storedUserInfo = localStorage.getItem('userInfo')
    if (storedUserInfo) {
      try {
        const data = JSON.parse(storedUserInfo)
        // 确保头像URL正确加载
        if (data.userInfo && !data.userInfo.avatar) {
          data.userInfo.avatar = `${import.meta.env.VITE_FILE_URL}/file/avatars/default_avatar.svg`
        }
        userInfo.value = data.userInfo
        token.value = data.token
      } catch (error) {
        console.error('解析用户信息失败:', error)
        localStorage.removeItem('userInfo')
      }
    }
  }

  // 登录
  const login = async (username: string, password: string) => {
    try {
      const res = await userLogin(username, password)
      // 检查响应数据是否包含必要的用户信息和token
      if (!res) {
        throw new Error('登录失败，服务器响应为空')
      }
      if (!res.userInfo || !res.token) {
        console.error('登录响应数据不完整:', res)
        throw new Error('登录失败，请稍后重试')  
      }
      userInfo.value = res.userInfo
      token.value = res.token
      // 存储用户信息和token到localStorage
      localStorage.setItem('userInfo', JSON.stringify({
        userInfo: res.userInfo,
        token: res.token
      }))
      ElMessage.success('登录成功')
      // 获取重定向地址
      const redirect = router.currentRoute.value.query.redirect as string
      if (redirect) {
        router.replace(redirect)
      } else {
        // 如果没有重定向地址，根据角色跳转到不同页面
        if (res.userInfo.role === 1) {
          router.replace('/admin')
        } else {
          router.replace('/dashboard')
        }
      }
    } catch (error: any) {
      // 提供更详细的错误信息
      console.error('登录失败详情:', error)
      // 如果错误对象包含消息，则显示该消息；否则显示通用错误消息
      const errorMessage = error.message || '登录失败，请稍后重试'
      ElMessage.error(errorMessage)
      throw error
    }
  }

  // 退出登录
  const logout = async () => {
    try {
      await userLogout()
      userInfo.value = null
      token.value = null
      // 清除localStorage中的用户信息
      localStorage.removeItem('userInfo')
      ElMessage.success('退出成功')
      router.push('/login')
    } catch (error) {
      ElMessage.error('退出失败')
      throw error
    }
  }

  // 判断是否登录
  const isLoggedIn = () => {
    try {
      const storedUserInfo = localStorage.getItem('userInfo')
      if (!storedUserInfo) return false
      
      const data = JSON.parse(storedUserInfo)
      return !!(data.token && data.userInfo)
    } catch (error) {
      console.error('解析用户信息失败:', error)
      localStorage.removeItem('userInfo')
      return false
    }
  }

  // 判断是否是管理员
  const isAdmin = () => {
    try {
      const storedUserInfo = localStorage.getItem('userInfo')
      if (!storedUserInfo) return false
      
      const data = JSON.parse(storedUserInfo)
      return data.userInfo?.role === 1
    } catch (error) {
      console.error('解析用户信息失败:', error)
      localStorage.removeItem('userInfo')
      return false
    }
  }

  // 修改密码
  const changePassword = async (data: { id: number; oldPassword: string; newPassword: string }) => {
    await updateUserPassword(data)
  }

  // 注册
  const register = async (data: { username: string; password: string; realName: string; phone: string; email: string }) => {
    return userRegister(data)
  }

  return {
    userInfo,
    token,
    initUserInfo,
    login,
    logout,
    isLoggedIn,
    isAdmin,
    changePassword,
    register
  }
})