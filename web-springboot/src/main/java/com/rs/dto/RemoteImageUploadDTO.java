package com.rs.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;
import org.springframework.web.multipart.MultipartFile;

/**
 * 遥感影像上传DTO
 */
@Data
public class RemoteImageUploadDTO {
    
    /**
     * 影像文件
     */
    @NotNull(message = "影像文件不能为空")
    private MultipartFile file;
    
    /**
     * 影像名称
     */
    @NotBlank(message = "影像名称不能为空")
    private String imageName;
    
    /**
     * 影像描述
     */
    private String description;
}