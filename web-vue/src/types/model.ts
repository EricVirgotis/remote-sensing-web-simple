// src/types/model.ts

/**
 * 分类模型类型定义
 */
export interface ClassificationModel {
  id: number // 模型ID
  userId: number // 用户ID
  modelName: string // 模型名称
  modelPath: string // 模型存储路径
  modelType: string // 模型类型
  description?: string // 模型描述
  accuracy?: number // 模型精度 (0-1 之间的小数)
  parameters?: string // 模型参数JSON
  isDefault: number // 是否默认模型：0-否，1-是
  status: number // 状态：0-禁用，1-启用
  createTime: string // 创建时间 (ISO 8601 格式字符串)
  updateTime: string // 更新时间 (ISO 8601 格式字符串)
}