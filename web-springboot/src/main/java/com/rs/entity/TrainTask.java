package com.rs.entity;

import com.baomidou.mybatisplus.annotation.IdType;
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
    private String modelType;
    private String parameters;
    private Integer taskStatus;
    private Integer progress;
    private String modelPath;
    private Double accuracy;
    private String errorMessage;
    private Date startTime;
    private Date endTime;
    private Date createTime;
    private Date updateTime;
    private Boolean deleted;
}