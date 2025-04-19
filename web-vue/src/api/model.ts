import request from '@/utils/request'
import type { ClassificationModel } from '@/types/model'

/**
 * 获取当前用户可用的所有分类模型（包括默认模型和用户自己的模型）
 * @returns Promise<ClassificationModel[]>
 */
export function getAvailableModels(): Promise<ClassificationModel[]> {
  // request.get 解析为后端的 Result 对象，因为拦截器返回 response.data
  // 我们需要从该对象中提取 'data' 属性。
  // 假设 Result 对象有一个 'data' 属性包含数组。
  return request.get<any>('/api/classification-model/available').then(res => res.data)
}

/**
 * 获取模型分页列表 (仅用户自己的模型)
 * @param params 查询参数
 * @returns Promise<PageResult<ClassificationModel>>
 */
// 如果需要获取用户自己的模型分页列表，可以取消注释下面的代码
// import type { PageResult, PageParams } from '@/types/global'
// export interface ModelQueryParams extends PageParams {
//   modelName?: string
//   modelType?: string
// }
// export function getModelPage(params: ModelQueryParams): Promise<PageResult<ClassificationModel>> {
//   return request.get<PageResult<ClassificationModel>>('/api/classification-model/page', { params })
// }

// 其他模型相关的 API 函数...