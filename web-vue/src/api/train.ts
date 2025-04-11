import { request } from './request'
import type { TrainTask, TrainTaskPage } from '@/types/train'

/**
 * 创建训练任务
 */
export function createTrainTask(data: {
  name: string
  datasetId: number
  epochs: number
  batchSize: number
  learningRate: number
}) {
  return request.post<number>('/train-task', data)
}

/**
 * 分页查询训练任务
 */
export function pageTrainTasks(params: {
  current: number
  size: number
  name?: string
  status?: number
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