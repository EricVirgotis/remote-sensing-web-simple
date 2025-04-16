import axios from 'axios';
import { ElMessage } from 'element-plus';

// 创建axios实例
const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000
});

// 请求拦截器
axiosInstance.interceptors.request.use(
  (config) => {
    // 在发送请求之前做些什么
    return config;
  },
  (error) => {
    // 对请求错误做些什么
    return Promise.reject(error);
  }
);

// 响应拦截器
axiosInstance.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    if (error.response) {
      // 服务器返回错误状态码
      const status = error.response.status;
      const data = error.response.data;
      const message = data?.message || error.message;
      
      switch (status) {
        case 400:
          // 请求参数错误
          ElMessage.error(`请求参数错误: ${message}`);
          break;
        case 401:
          // 未授权
          ElMessage.error('登录已过期，请重新登录');
          break;
        case 403:
          // 禁止访问
          ElMessage.error('无权限访问此资源');
          break;
        case 404:
          // 资源不存在
          ElMessage.error(`请求的资源不存在: ${message}`);
          break;
        case 500:
          // 服务器内部错误
          if (data?.task_status === 2) {
            ElMessage.error(`训练失败: ${message}`);
          } else if (data?.task_status === 3) {
            ElMessage.error(`网络错误: ${message}`);
          } else {
            ElMessage.error(`服务器错误: ${message}`);
          }
          break;
        default:
          // 其他错误
          ElMessage.error(`请求错误: ${message}`);
      }
      
      return Promise.reject(error);
    } else {
      // 网络错误或请求超时
      ElMessage.error('网络连接异常，请检查网络后重试');
      return Promise.reject(error);
    }
  }
);

export default axiosInstance;