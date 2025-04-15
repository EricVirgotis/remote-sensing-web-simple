import { request } from './request'
import type { TrainTask, TrainTaskPage } from '@/types/train'

/**
 * 创建训练任务
 */
export function createTrainTask(data: {
  name: string
  datasetId: number
  modelName: string
  usePretrained: boolean
  epochs: number
  batchSize: number
  learningRate: number
}) {
  // 将modelName映射为model_name，以匹配后端数据库字段要求
  const requestData = {
    name: data.name,
    datasetId: data.datasetId,
    model_type: data.modelName,  // 后端已有model_type字段
    model_name: data.modelName,  // 添加model_name字段，数据库表中必填字段
    modelName: data.modelName,   // 保留原字段，与TrainTask实体类匹配
    parameters: JSON.stringify({
      usePretrained: data.usePretrained,
      batchSize: data.batchSize,
      epochs: data.epochs,
      learningRate: data.learningRate
    }),
    // 直接传递训练参数，与TrainTask实体类匹配
    usePretrained: data.usePretrained,
    batchSize: data.batchSize,
    epochs: data.epochs,
    learningRate: data.learningRate
  }
  return request.post<number>('/train-task/create', requestData)
}

/**
 * 分页查询训练任务
 */
export function pageTrainTasks(params: {
  current: number
  size: number
  name?: string
  status?: number
  model_name?: string
}) {
  return request.get<TrainTaskPage>('/train-task/page', { params })
}

/**
 * 获取训练任务详情
 */
export function getTrainTaskDetail(id: number) {
  return request.get<TrainTask>(`/train-task/${id}`)
}

/**
 * 删除训练任务
 */
export function deleteTrainTask(id: number) {
  return request.delete<void>(`/train-task/${id}`)
}