package com.rs.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Data;

/**
 * 分析任务提交DTO
 */
@Data
public class AnalysisTaskSubmitDTO {
    
    /**
     * 影像ID
     */
    @NotNull(message = "影像ID不能为空")
    private Long imageId;
    
    /**
     * 模型ID
     */
    @NotNull(message = "模型ID不能为空")
    private Long modelId;
    
    /**
     * 任务名称
     */
    private String taskName;
    
    /**
     * 任务参数JSON
     */
    private String parameters;
}