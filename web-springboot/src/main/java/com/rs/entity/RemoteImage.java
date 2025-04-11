package com.rs.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 遥感影像实体类
 */
@Data
@TableName("remote_image")
public class RemoteImage {
    
    /**
     * 影像ID
     */
    @TableId(type = IdType.AUTO)
    private Long id;
    
    /**
     * 用户ID
     */
    private Long userId;
    
    /**
     * 影像名称
     */
    private String imageName;
    
    /**
     * 影像存储路径
     */
    private String imagePath;
    
    /**
     * 影像大小(字节)
     */
    private Long imageSize;
    
    /**
     * 影像格式
     */
    private String imageFormat;
    
    /**
     * 上传时间
     */
    private LocalDateTime uploadTime;
    
    /**
     * 影像描述
     */
    private String description;
    
    /**
     * 元数据JSON
     */
    private String metadata;
    
    /**
     * 状态：0-无效，1-有效
     */
    private Integer status;
    
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