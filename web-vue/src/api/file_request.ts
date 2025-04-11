import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

// 创建 axios 实例
const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_FILE_URL,
  timeout: 60000,
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    // 如果是文件上传请求，处理响应数据格式
    if (response.config.url?.includes('/upload/')) {
      const { code, msg, data } = response.data
      if (code === 200 || code === 0) {
        // 确保返回的数据包含必要的字段
        if (data && typeof data.url === 'string' && typeof data.bucket === 'string' && typeof data.objectKey === 'string') {
          return data
        }
        console.error('文件服务返回的数据格式:', data)
        throw new Error('文件服务返回的数据格式不正确')
      }
      const errorMessage = msg || '文件上传失败'
      console.error('文件上传失败:', errorMessage)
      ElMessage.error(errorMessage)
      return Promise.reject(new Error(errorMessage))
    }

    const { code, msg, data } = response.data

    if (code === 200 || code === 0) {
      return data
    }

    const errorMessage = msg || '请求失败'
    ElMessage.error(errorMessage)
    return Promise.reject(new Error(errorMessage))
  },
  (error) => {
    const errorMessage = error.response?.data?.msg || error.message || '请求失败'
    ElMessage.error(errorMessage)
    return Promise.reject(error)
  }
)

// 封装请求方法
const fileRequest = {
  /**
   * 上传文件
   * @param bucket 存储桶名称
   * @param file 文件对象
   * @param isCache 是否为缓存文件
   * @param config 额外的请求配置
   * @returns { url: string, bucket: string, objectKey: string }
   */
  async upload<T = { url: string, bucket: string, objectKey: string }>(bucket: string, file: File, isCache?: boolean, config?: AxiosRequestConfig): Promise<T> {
    const formData = new FormData()
    formData.append('file', file)
    if (isCache) {
      formData.append('is_cache', 'true')
    }
    
    // 从localStorage获取用户信息
    const userInfoStr = localStorage.getItem('userInfo')
    let userId = ''
    if (!userInfoStr) {
      throw new Error('未找到用户信息，请先登录')
    }
    
    try {
      const parsedInfo = JSON.parse(userInfoStr)
      if (!parsedInfo || typeof parsedInfo !== 'object') {
        throw new Error('用户信息格式不正确')
      }
      
      // 兼容新旧两种用户信息格式
      const userInfo = parsedInfo.userInfo || parsedInfo
      if (!userInfo || typeof userInfo !== 'object') {
        throw new Error('用户信息中缺少userInfo对象')
      }
      
      // 严格验证id字段存在且为有效值
      if (userInfo.id === undefined || userInfo.id === null || 
          (typeof userInfo.id !== 'number' && typeof userInfo.id !== 'string')) {
        console.error('无效的用户ID:', userInfo.id)
        throw new Error('用户信息中缺少有效的id字段')
      }
      
      // 确保id转换为字符串
      userId = String(userInfo.id).trim()
      if (!userId) {
        throw new Error('用户ID不能为空')
      }
    } catch (error) {
      console.error('解析用户信息失败:', error)
      throw new Error('获取用户ID失败，请重新登录后重试')
    }
    
    // 特殊处理头像上传
    if (bucket === 'avatars') {
      // 使用用户ID作为头像存储目录
      const storedUserInfo = localStorage.getItem('userInfo')
      if (storedUserInfo) {
        const userData = JSON.parse(storedUserInfo)
        const userInfo = userData.userInfo || userData
        if (userInfo && userInfo.id) {
          bucket = `avatars/${userInfo.id}`
        } else {
          console.error('用户信息中缺少有效的id字段:', userInfo)
          throw new Error('用户信息中缺少有效的id字段')
        }
      }
      
      // 检查用户是否有旧头像（非默认头像）
      if (storedUserInfo) {
        const userData = JSON.parse(storedUserInfo)
        const currentAvatar = userData.userInfo?.avatar
        
        // 如果当前头像不是默认头像，则删除旧头像
        if (currentAvatar && typeof currentAvatar === 'string' && !currentAvatar.includes('default_avatar')) {
          try {
            // 从URL中提取objectKey
            const urlParts = currentAvatar.split('/')
            // 提取用户ID和文件名
            if (urlParts && urlParts.length >= 2) {
              const pathParts = urlParts.slice(urlParts.length - 2)
              if (pathParts && pathParts.length === 2 && pathParts[0] && pathParts[1]) {
                const oldObjectKey = `${pathParts[0]}/${pathParts[1]}`
                
                // 删除旧头像
                await this.delete(bucket, oldObjectKey)
                console.log('旧头像已删除')
              }
            }
          } catch (error) {
            console.error('删除旧头像失败:', error)
            // 继续上传新头像，不中断流程
          }
        }
      }
    }
    
    // 统一的文件上传逻辑
    return service.post(`/file/upload/${bucket}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'X-User-ID': userId // 添加用户ID到请求头
      },
      ...config,
    })
  },

  /**
   * 获取文件
   * @param bucket 存储桶名称
   * @param objectKey 文件名
   * @param config 额外的请求配置
   * @returns 返回文件内容
   */
  get(bucket: string, objectKey: string, config?: AxiosRequestConfig): Promise<Blob> {
    return service.get(`/file/${bucket}/${objectKey}`, {
      responseType: 'blob',
      ...config,
    })
  },

  /**
   * 删除文件
   * @param bucket 存储桶名称
   * @param objectKey 文件名
   * @param config 额外的请求配置
   * @returns 返回响应数据
   */
  delete<T = any>(bucket: string, objectKey: string, config?: AxiosRequestConfig): Promise<T> {
    return service.delete(`/file/${bucket}/${objectKey}`, config)
  },

  /**
   * 获取文件URL
   * @param bucket 存储桶名称
   * @param objectKey 文件名或包含用户ID的路径
   * @returns 返回文件访问URL
   */
  getFileUrl(bucket: string, objectKey: string): string {
    // 参数验证
    if (!bucket || typeof bucket !== 'string') {
      console.error('无效的存储桶名称:', bucket)
      bucket = 'default' // 使用默认值
    }
    
    if (!objectKey || typeof objectKey !== 'string') {
      console.error('无效的文件名:', objectKey)
      objectKey = 'default_avatar.svg' // 使用默认头像
      return `${import.meta.env.VITE_FILE_URL}/file/avatars/default_avatar.svg`
    }
    
    // 从localStorage获取用户信息
    const userInfoStr = localStorage.getItem('userInfo')
    let userId = ''
    if (!userInfoStr) {
      throw new Error('未找到用户信息，请先登录')
    }
    
    try {
      const parsedInfo = JSON.parse(userInfoStr)
      if (!parsedInfo || typeof parsedInfo !== 'object') {
        throw new Error('用户信息格式不正确')
      }
      
      // 兼容新旧两种用户信息格式
      const userInfo = parsedInfo.userInfo || parsedInfo
      if (!userInfo || typeof userInfo !== 'object') {
        throw new Error('用户信息中缺少userInfo对象')
      }
      
      // 严格验证id字段存在且为有效值
      if (userInfo.id === undefined || userInfo.id === null || 
          (typeof userInfo.id !== 'number' && typeof userInfo.id !== 'string')) {
        console.error('无效的用户ID:', userInfo.id)
        throw new Error('用户信息中缺少有效的id字段')
      }
      
      // 确保id转换为字符串
      userId = String(userInfo.id).trim()
      if (!userId) {
        throw new Error('用户ID不能为空')
      }
    } catch (error) {
      console.error('解析用户信息失败:', error)
      throw new Error('获取用户ID失败，请重新登录后重试')
    }
    
    // 检查objectKey是否已包含用户ID
    try {
      if (objectKey.includes('/')) {
        // 已包含路径分隔符，假定已包含用户ID
        return `${import.meta.env.VITE_FILE_URL}/file/${bucket}/${objectKey}`
      } else {
        // 添加用户ID到路径
        return `${import.meta.env.VITE_FILE_URL}/file/${bucket}/${userId}/${objectKey}`
      }
    } catch (error) {
      console.error('生成文件URL失败:', error)
      // 返回默认头像URL
      return `${import.meta.env.VITE_FILE_URL}/file/avatars/default_avatar.svg`
    }
  }
}

export { fileRequest }