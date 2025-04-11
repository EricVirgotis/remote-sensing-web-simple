import { request } from './request'
import type { ClassificationTask } from '@/types/classification'

/**
 * 创建分类任务
 */
export function createTask(data: FormData) {
    return request.post<ClassificationTask>('/classification', data, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}

/**
 * 分页查询任务列表
 */
export function pageQuery(params: {
    pageNum?: number
    pageSize?: number
}) {
    return request.get<{
        records: ClassificationTask[]
        total: number
        size: number
        current: number
    }>('/classification/page', { params })
}

/**
 * 获取任务详情
 */
export function getTaskDetail(taskId: number) {
    return request.get<ClassificationTask>(`/classification/${taskId}`)
}

/**
 * 删除任务
 */
export function deleteTask(taskId: number) {
    return request.delete(`/classification/${taskId}`)
} 