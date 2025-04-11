package com.rs.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 分类模型实体类
 */
@Data
@TableName("classification_model")
public class ClassificationModel {
    
    /**
     * 模型ID
     */
    @TableId(type = IdType.AUTO)
    private Long id;
    
    /**
     * 模型名称
     */
    private String modelName;
    
    /**
     * 模型存储路径
     */
    private String modelPath;
    
    /**
     * 模型类型
     */
    private String modelType;
    
    /**
     * 模型描述
     */
    private String description;
    
    /**
     * 模型精度
     */
    private BigDecimal accuracy;
    
    /**
     * 模型参数JSON
     */
    private String parameters;
    
    /**
     * 是否默认模型：0-否，1-是
     */
    private Integer isDefault;
    
    /**
     * 状态：0-禁用，1-启用
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