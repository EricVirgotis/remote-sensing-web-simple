import { request } from './request'
import type { Dataset } from '@/types/dataset'

/**
 * 创建数据集
 */
export function createDataset(data: FormData) {
    return request.post<number>('/dataset', data)
}

/**
 * 分页查询数据集
 */
export function pageDatasets(params: {
    current: number
    size: number
    name?: string
    status?: number
}) {
    return request.get<{
        records: Dataset[]
        total: number
        size: number
        current: number
    }>('/list_datasets', { params })
}

/**
 * 获取数据集详情
 */
export function getDatasetDetail(id: number) {
    return request.get<Dataset>(`/dataset/${id}`)
}

/**
 * 删除数据集
 */
export function deleteDataset(id: number) {
    return request.delete(`/dataset/${id}`)
}

/**
 * 下载数据集
 */
export function downloadDataset(id: number) {
    return request.get(`/dataset/${id}/download`, {
        responseType: 'blob'
    })
}

/**
 * 更新数据集
 */
export function updateDataset(id: number, data: {
    name: string
    description: string
    status: number
}) {
    return request.put(`/dataset/${id}`, data)
}