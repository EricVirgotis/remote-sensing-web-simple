/**
 * 训练任务状态
 */
export enum TrainTaskStatus {
  /**
   * 进行中
   */
  RUNNING = 0,
  
  /**
   * 已完成
   */
  COMPLETED = 1,
  
  /**
   * 失败
   */
  FAILED = 2
}

/**
 * 训练任务
 */
export interface TrainTask {
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
   * 数据集存储桶
   */
  datasetBucket: string
  
  /**
   * 数据集对象键
   */
  datasetObjectKey: string
  
  /**
   * 模型权重存储桶
   */
  modelBucket: string
  
  /**
   * 模型权重对象键
   */
  modelObjectKey: string
  
  /**
   * 训练轮数
   */
  epochs: number
  
  /**
   * 批次大小
   */
  batchSize: number
  
  /**
   * 学习率
   */
  learningRate: number
  
  /**
   * 任务状态
   */
  status: TrainTaskStatus
  
  /**
   * 失败原因
   */
  errorMsg: string
  
  /**
   * 训练准确率
   */
  accuracy: number
  
  /**
   * 训练损失
   */
  loss: number
  
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
 * 训练任务分页列表
 */
export interface TrainTaskPage {
  /**
   * 记录列表
   */
  records: TrainTask[]
  
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