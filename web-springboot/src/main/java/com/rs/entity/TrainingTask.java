package com.rs.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 模型训练任务实体类
 */
@Data
@TableName("training_task")
public class TrainingTask {
    
    /**
     * 训练任务ID
     */
    @TableId(type = IdType.AUTO)
    private Long id;
    
    /**
     * 用户ID
     */
    private Long userId;
    
    /**
     * 数据集ID
     */
    private Long datasetId;
    
    /**
     * 任务名称
     */
    private String taskName;
    
    /**
     * 模型名称
     */
    private String modelName;
    
    /**
     * 模型类型
     */
    private String modelType;
    
    /**
     * 任务状态：PENDING-等待中，RUNNING-运行中，COMPLETED-已完成，FAILED-失败
     */
    private String taskStatus;
    
    /**
     * 生成模型存储路径
     */
    private String modelPath;
    
    /**
     * 开始时间
     */
    private LocalDateTime startTime;
    
    /**
     * 结束时间
     */
    private LocalDateTime endTime;
    
    /**
     * 模型精度
     */
    private BigDecimal accuracy;
    
    /**
     * 训练参数JSON
     */
    private String parameters;
    
    /**
     * 错误信息
     */
    private String errorMessage;
    
    /**
     * 创建时间
     */
    private LocalDateTime createTime;
    
    /**
     * 更新时间
     */
    private LocalDateTime updateTime;
    
    /**
     * 是否删除：0-未删除，1-已删除
     */
    @TableLogic
    private Integer deleted;
}