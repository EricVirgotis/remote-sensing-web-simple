// 分析任务
export interface AnalysisTask {
    id: number
    userId: number
    username: string
    imageId: number
    name: string
    description: string
    algorithm: string
    parameters: string
    status: number
    errorMessage: string
    startTime: string
    endTime: string
    createTime: string
    updateTime: string
}

// 任务创建参数
export interface TaskCreateParams {
    imageId: number | undefined
    name: string
    description: string
    algorithm: string
    parameters: string
}

// 任务查询参数
export interface TaskQueryParams {
    current: number
    size: number
    name?: string
    algorithm?: string
    status?: number
    imageId?: number
}

// 算法定义
export interface Algorithm {
    name: string
    description: string
    parameters: {
        [key: string]: {
            type: string
            description: string
            default: number
            min: number
            max: number
        }
    }
} 