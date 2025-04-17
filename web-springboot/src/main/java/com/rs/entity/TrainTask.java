package com.rs.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.util.Date;

@Data
@TableName("training_task")
public class TrainTask {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long userId;
    private Long datasetId;
    private String taskName;
    
    // 添加前端传递的字段，用于接收前端数据
    @TableField(exist = false)
    private String name;
    
    private String modelType;
    
    // 数据库中的model_name字段
    @TableField("model_name")
    private String modelName;
    
    // 添加前端传递的字段，用于接收预训练标志
    @TableField(exist = false)
    private Boolean usePretrained;
    
    // 添加前端传递的训练参数字段
    @TableField(exist = false)
    private Integer epochs;
    
    @TableField(exist = false)
    private Integer batchSize;
    
    @TableField(exist = false)
    private Double learningRate;
    
    private String parameters;
    private String taskStatus;
    private Integer progress;
    private String modelPath;
    private Double accuracy;
    private Double loss; // 添加 loss 字段
    private String errorMessage;
    private Date startTime;
    private Date endTime;
    private Date createTime;
    private Date updateTime;
    private Boolean deleted;
}