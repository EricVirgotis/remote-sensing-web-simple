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
    modelId: number | undefined // 添加模型ID
    name: string
    description: string
    // algorithm: string // 移除算法相关字段，如果不再需要
    // parameters: string // 移除算法相关字段，如果不再需要
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