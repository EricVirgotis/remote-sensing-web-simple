// 分析结果
export interface AnalysisResult {
    id: number
    taskId: number
    name: string
    description: string
    bucketName: string
    objectKey: string
    resultType: string
    metrics: string
    createTime: string
    updateTime: string
} 