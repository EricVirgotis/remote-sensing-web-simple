import { request } from './request'
import { algoRequest } from './algo_request'
import type { AnalysisTask, TaskCreateParams, TaskQueryParams, Algorithm } from '@/types/task'
import type { PageResult } from '@/types/common'

// 创建任务
export function createTask(data: TaskCreateParams) {
    return request.post<AnalysisTask>('/tasks', data)
}

// 分页查询任务
export function getTaskList(params: TaskQueryParams) {
    return request.get<PageResult<AnalysisTask>>('/tasks', { params })
}

// 获取任务详情
export function getTaskDetail(id: number) {
    return request.get<AnalysisTask>(`/tasks/${id}`)
}

// 获取任务状态
export function getTaskStatus(id: number) {
    return request.get<number>(`/tasks/${id}/status`)
}

// 删除任务
export function deleteTask(id: number) {
    return request.delete(`/tasks/${id}`)
}

// 获取支持的算法列表
export function getAlgorithms() {
    return algoRequest.get<Record<string, Algorithm>>('/algorithm')
}

// 获取算法详情
export function getAlgorithm(name: string) {
    return algoRequest.get<Algorithm>(`/algorithm/${name}`)
}

// 执行算法预测
export function predict(data: { algorithm: string; parameters: any }) {
    return algoRequest.post('/algorithm/predict', data)
} 