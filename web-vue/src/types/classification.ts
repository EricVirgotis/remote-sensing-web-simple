/**
 * 图像分类任务
 */
export interface ClassificationTask {
    /**
     * 任务ID
     */
    id: number
    
    /**
     * 任务名称
     */
    name: string
    
    /**
     * 用户ID
     */
    userId: number
    
    /**
     * 图像文件存储桶
     */
    bucket: string
    
    /**
     * 图像文件对象键
     */
    objectKey: string
    
    /**
     * 预测类别ID
     */
    classId?: number
    
    /**
     * 预测类别名称
     */
    className?: string
    
    /**
     * 预测置信度
     */
    confidence?: number
    
    /**
     * 任务状态(0:进行中 1:已完成 2:失败)
     */
    status: number
    
    /**
     * 失败原因
     */
    errorMsg?: string
    
    /**
     * 创建时间
     */
    createTime: string
    
    /**
     * 更新时间
     */
    updateTime: string
} 