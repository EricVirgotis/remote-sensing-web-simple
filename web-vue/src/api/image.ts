import { request } from './request'
import { fileRequest } from './file_request'
import type { RemoteSensingImage, ImageUploadParams, ImageQueryParams } from '@/types/image'
import type { PageResult } from '@/types/common'

// 上传影像文件
export function uploadImageFile(file: File) {
    return fileRequest.upload('images', file)
}

// 获取影像文件URL
export function getImageFileUrl(bucketName: string, objectKey: string) {
    return fileRequest.getFileUrl(bucketName, objectKey)
}

// 删除影像文件
export function deleteImageFile(bucketName: string, objectKey: string) {
    return fileRequest.delete(bucketName, objectKey)
}

// 上传影像信息
export function uploadImage(data: ImageUploadParams) {
    return request.post<RemoteSensingImage>('/images', data)
}

// 分页查询影像
export function getImageList(params: ImageQueryParams) {
    return request.get<PageResult<RemoteSensingImage>>('/images', { params })
}

// 获取影像详情
export function getImageDetail(id: number) {
    return request.get<RemoteSensingImage>(`/images/${id}`)
}

// 删除影像
export function deleteImage(id: number) {
    return request.delete(`/images/${id}`)
} 