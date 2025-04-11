/**
 * 数据集
 */
export interface Dataset {
    /**
     * 数据集ID
     */
    id: number
    
    /**
     * 数据集名称
     */
    name: string
    
    /**
     * 用户ID
     */
    userId: number
    
    /**
     * 存储桶
     */
    bucket: string
    
    /**
     * 对象键
     */
    objectKey: string
    
    /**
     * 数据集描述
     */
    description: string
    
    /**
     * 状态(0:禁用 1:启用)
     */
    status: number
    
    /**
     * 创建时间
     */
    createTime: string
    
    /**
     * 更新时间
     */
    updateTime: string
}

/**
 * 数据集分页列表
 */
export interface DatasetPage {
    /**
     * 记录列表
     */
    records: Dataset[]
    
    /**
     * 总记录数
     */
    total: number
    
    /**
     * 每页记录数
     */
    size: number
    
    /**
     * 当前页码
     */
    current: number
} 