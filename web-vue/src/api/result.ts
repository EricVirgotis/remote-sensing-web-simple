import { request } from './request'
import { fileRequest } from './file_request'
import type { AnalysisResult } from '@/types/result'

// 获取任务的所有结果
export function getResultsByTaskId(taskId: number) {
    return request.get<AnalysisResult[]>(`/results/task/${taskId}`)
}

// 获取结果详情
export function getResultDetail(id: number) {
    return request.get<AnalysisResult>(`/results/${id}`)
}

// 删除结果
export function deleteResult(id: number) {
    return request.delete(`/results/${id}`)
}

// 获取结果文件URL
export function getResultFileUrl(bucketName: string, objectKey: string) {
    return fileRequest.getFileUrl(bucketName, objectKey)
}

// 删除结果文件
export function deleteResultFile(bucketName: string, objectKey: string) {
    return fileRequest.delete(bucketName, objectKey)
} 