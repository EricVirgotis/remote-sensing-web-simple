// 遥感影像
export interface RemoteSensingImage {
    id: number
    userId: number
    name: string
    description: string
    bucketName: string
    objectKey: string
    size: number
    format: string
    width: number
    height: number
    bands: number
    status: number
    createTime: string
    updateTime: string
}

// 影像上传参数
export interface ImageUploadParams {
    name: string
    description: string
    bucketName: string
    objectKey: string
    size: number
    format: string
    width: number
    height: number
    bands: number
}

// 影像查询参数
export interface ImageQueryParams {
    current: number
    size: number
    name?: string
    format?: string
    status?: number
} 