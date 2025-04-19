package com.rs.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.rs.entity.TrainingTask;

import java.math.BigDecimal;

/**
 * 训练任务服务接口
 */
public interface TrainingTaskService extends IService<TrainingTask> {
    
    /**
     * 更新训练任务状态
     * @param taskId 任务ID
     * @param taskStatus 任务状态
     * @param modelPath 模型路径
     * @param accuracy 模型精度
     * @param errorMessage 错误信息
     * @return 是否更新成功
     */
    boolean updateTaskStatus(Long taskId, String taskStatus, String modelPath, BigDecimal accuracy, String errorMessage);
}