package com.rs.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;
import org.springframework.web.multipart.MultipartFile;

/**
 * 训练数据集上传DTO
 */
@Data
public class TrainingDatasetUploadDTO {
    
    /**
     * 数据集文件
     */
    @NotNull(message = "数据集文件不能为空")
    private MultipartFile file;
    
    /**
     * 数据集名称
     */
    @NotBlank(message = "数据集名称不能为空")
    private String datasetName;
    
    /**
     * 数据集描述
     */
    private String description;
    
    /**
     * 样本数量
     */
    private Integer sampleCount;
}