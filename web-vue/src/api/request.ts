import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

// 扩展AxiosRequestConfig类型以支持silent选项
declare module 'axios' {
  export interface AxiosRequestConfig {
    silent?: boolean
  }
}

// 创建 axios 实例
const instance: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 10000,
})

// 请求拦截器
instance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 从 localStorage 获取 token 和 userId
    const userInfoStr = localStorage.getItem('userInfo')
    if (userInfoStr) {
      try {
        const parsedInfo = JSON.parse(userInfoStr)
        // 兼容两种可能的数据结构：直接包含token/userInfo或嵌套在data中
        const token = parsedInfo.token || (parsedInfo.data && parsedInfo.data.token)
        const userInfo = parsedInfo.userInfo || (parsedInfo.data && parsedInfo.data.userInfo) || parsedInfo
        
        if (token && config.headers) {
          // 添加 token 到请求头
          config.headers.Authorization = `Bearer ${token}`
        }
        
        // 添加 X-User-ID 请求头
        if (userInfo && userInfo.id && config.headers) {
          config.headers['X-User-ID'] = userInfo.id
        } else {
          // 如果需要 userId 但不存在，可以考虑取消请求或记录警告
          console.warn('缺少 X-User-ID，请求可能失败:', config.url);
        }
      } catch (error) {
        console.error('解析用户信息或添加请求头失败:', error)
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
instance.interceptors.response.use(
  (response: AxiosResponse) => {
    // 如果是二进制数据或文件上传请求，直接返回
    if (response.config.responseType === 'blob' || 
        (response.config.headers && 
         typeof response.config.headers['Content-Type'] === 'string' && 
         response.config.headers['Content-Type'].includes('multipart/form-data'))) {
      return response.data
    }
    
    // 对于登录接口，特殊处理
    if (response.config.url === '/api/user/login') {
      console.groupCollapsed('登录接口响应处理')
      console.log('完整响应对象:', response)
      
      // 检查响应数据是否有效
      if (!response.data) {
        console.error('登录失败：服务器响应为空')
        console.groupEnd()
        return Promise.reject(new Error('登录失败，服务器响应为空'))
      }
      
      console.log('登录响应原始数据:', JSON.stringify(response.data))
      
      // 统一处理登录响应数据
      const { code, message, data } = response.data
      
      // 如果响应成功且包含data（包含token和userInfo）
      if ((code === 200 || code === 0) && data) {
        // 获取登录用户名
        const username = JSON.parse(response.config.data).username
        // 检查data中是否直接包含token，或者是否嵌套在data.data中
        const token = data.token || (data.data && data.data.token) || data
        
        // 创建一个新的axios实例用于获取用户信息，避免循环依赖
        const userInfoInstance = axios.create({
          baseURL: import.meta.env.VITE_API_URL,
          timeout: 10000,
          headers: {
            Authorization: `Bearer ${token}`
          }
        })
        
        // 使用token获取用户信息
        return userInfoInstance.get('/user/current')
          .then(userResponse => {
            // 获取用户信息成功
            console.log('获取用户信息成功:', userResponse.data)
            
            // 构造标准的LoginResponse格式
            // 从响应中提取用户信息，兼容不同的数据结构
            const responseData = userResponse.data;
            const userInfo = responseData.data || 
                            (responseData.userInfo) || 
                            (responseData.data && responseData.data.userInfo) || 
                            responseData;
            
            // 确保userInfo是一个有效的对象
            if (!userInfo || typeof userInfo !== 'object') {
              console.error('无法从响应中提取有效的用户信息:', responseData);
              throw new Error('获取用户信息失败，响应格式不正确');
            }
            
            // 保留原始登录响应中的avatar字段
            const originalLoginData = response.data.data;
            if (originalLoginData && originalLoginData.userInfo && originalLoginData.userInfo.avatar) {
              userInfo.avatar = originalLoginData.userInfo.avatar;
            }
            
            const loginResponse = {
              token: token,
              userInfo: userInfo
            }
            
            console.log('处理后的登录响应数据:', loginResponse)
            console.groupEnd()
            return loginResponse
          })
          .catch(error => {
            console.error('获取用户信息失败:', error)
            // 检查错误响应
            const errorResponse = error.response?.data;
            
            // 如果获取用户信息失败，构造基本的用户信息
            // 但保留错误信息以便前端显示
            const loginResponse = {
              token: token,
              userInfo: errorResponse || {
                id: 0,
                username: username,
                realName: '',
                phone: null,
                email: null,
                role: 0,
                status: 1,
                error: '获取用户信息失败'
              }
            }
            console.log('使用基本用户信息:', loginResponse)
            console.groupEnd()
            return loginResponse
          })
      }
      
      // 处理错误情况
      const errorMsg = message || '登录失败，请稍后重试'
      console.error('登录失败:', errorMsg)
      console.groupEnd()
      return Promise.reject(new Error(errorMsg))
    }
    
    // 处理其他接口的标准响应格式
    const { code, msg, data } = response.data
    
    // 请求成功
    if (code === 200 || code === 0) {
      return data
    }

    // 登录过期
    if (code === 401) {
      const userStore = useUserStore()
      userStore.logout()
      return Promise.reject(new Error('登录已过期，请重新登录'))
    }

    // 显示错误信息
    const errorMessage = msg || (data && typeof data === 'object' ? JSON.stringify(data) : '请求失败')
    const error = new Error(errorMessage) as Error & { response?: any, data?: any }
    error.response = response
    error.data = response.data
    if (!response.config?.silent) {
      ElMessage.error(errorMessage)
    }
    return Promise.reject(error)
  },
  (error) => {
    // 处理网络错误
    console.groupCollapsed('请求错误详情')
    console.error('请求配置:', error.config)
    console.error('响应数据:', error.response?.data)
    console.error('响应状态:', error.response?.status)
    console.error('响应头:', error.response?.headers)
    console.groupEnd()
    
    let message = '网络请求失败，请检查网络连接'
    if (error.response) {
      const { status, data } = error.response
      switch (status) {
        case 400:
          message = (data && data.msg) || '请求参数错误'
          break
        case 401:
          message = '登录已过期，请重新登录'
          const userStore = useUserStore()
          userStore.logout()
          break
        case 403:
          message = '没有权限访问该资源'
          break
        case 404:
          message = '请求的资源不存在'
          break
        case 500:
          message = (data && data.msg) || '服务器内部错误'
          break
        default:
          message = (data && data.msg) || '请求失败'
      }
    }
    if (!error.config?.silent) {
      ElMessage.error(message)
    }
    return Promise.reject(new Error(message))
  }
)

// 封装请求方法
const request = {
  get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return instance.get(url, config)
  },

  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return instance.post(url, data, config)
  },

  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return instance.put(url, data, config)
  },

  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return instance.delete(url, config)
  },
}

export { request }
 