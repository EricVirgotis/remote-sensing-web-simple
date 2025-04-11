package com.rs.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 分析任务实体类
 */
@Data
@TableName("analysis_task")
public class AnalysisTask {
    
    /**
     * 任务ID
     */
    @TableId(type = IdType.AUTO)
    private Long id;
    
    /**
     * 用户ID
     */
    private Long userId;
    
    /**
     * 影像ID
     */
    private Long imageId;
    
    /**
     * 模型ID
     */
    private Long modelId;
    
    /**
     * 任务名称
     */
    private String taskName;
    
    /**
     * 任务状态：PENDING-等待中，RUNNING-运行中，COMPLETED-已完成，FAILED-失败
     */
    private String taskStatus;
    
    /**
     * 结果存储路径
     */
    private String resultPath;
    
    /**
     * 开始时间
     */
    private LocalDateTime startTime;
    
    /**
     * 结束时间
     */
    private LocalDateTime endTime;
    
    /**
     * 错误信息
     */
    private String errorMessage;
    
    /**
     * 任务参数JSON
     */
    private String parameters;
    
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