package com.rs.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 训练数据集实体类
 */
@Data
@TableName("training_dataset")
public class TrainingDataset {
    
    /**
     * 数据集ID
     */
    @TableId(type = IdType.AUTO)
    private Long id;
    
    /**
     * 用户ID
     */
    private Long userId;
    
    /**
     * 数据集名称
     */
    private String datasetName;
    
    /**
     * 数据集存储路径
     */
    private String datasetPath;
    
    /**
     * 数据集大小(字节)
     */
    private Long datasetSize;
    
    /**
     * 样本数量
     */
    private Integer sampleCount;
    
    /**
     * 数据集描述
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